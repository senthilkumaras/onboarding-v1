from llms import get_intent_llm, get_voice_llm, get_policy_llm
from rag import retrieve
from cache import get_cached_answer, set_cached_answer

# If you already have prompts.py, keep them there.
# Below assumes these exist. If not, replace them with plain strings.
from prompts import (
    OVERVIEW_PROMPT,
    INTENT_PROMPT,
    CLARIFY_PROMPT,
    PAUSE_PROMPT,
)

def run_overview(state, topic_name: str, content: str):
    llm = get_voice_llm(topic_name)
    msg = (OVERVIEW_PROMPT | llm).invoke({
        "topic": topic_name.replace("_", " ").title(),
        "content": content,
    }).content.strip()

    state["overview"] = msg
    state["assistant_message"] = msg
    return state


def detect_intent(state):
    llm = get_intent_llm()
    raw = (INTENT_PROMPT | llm).invoke({
        "user_message": state["user_message"]
    }).content.strip()

    # normalize to first token like CURIOUS / GOT_IT / CONFUSED / PAUSE
    state["intent"] = raw.split()[0].upper() if raw else "CONFUSED"
    return state


def handle_confused(state, topic_name: str):
    llm = get_voice_llm(topic_name)
    msg = (CLARIFY_PROMPT | llm).invoke({
        "topic": topic_name.replace("_", " ").title(),
        "overview": state.get("overview", ""),
        "user_message": state["user_message"],
    }).content.strip()

    state["assistant_message"] = msg
    return state


def handle_pause(state):
    llm = get_voice_llm(state.get("current_topic", "onboarding"))
    msg = (PAUSE_PROMPT | llm).invoke({}).content.strip()
    state["assistant_message"] = msg
    state["pause_requested"] = True
    return state


def handle_done(state):
    state["assistant_message"] = (
        "You’ve completed this topic.\n\n"
        "You can type **continue** to move to the next topic, or type a topic name like "
        "**benefits**, **time_off**, **it_setup**."
    )
    return state


def handle_curious(state, topic_name: str, content: str):
    q = state["user_message"]

    cached = get_cached_answer(topic_name, q)
    if cached:
        state["assistant_message"] = cached["assistant_message"]
        return state

    docs = retrieve(q, k=4)
    context = "\n\n".join([d.page_content for d in docs])

    sources = []
    for d in docs:
        src = d.metadata.get("source_name", "unknown")
        page = d.metadata.get("page", None)
        if page is not None:
            sources.append(f"- {src} (page {page + 1})")
        else:
            sources.append(f"- {src}")

    llm = get_policy_llm()
    prompt = f"""
You are an HR onboarding assistant.

Rules:
- Answer using ONLY the context.
- If the answer is not in the context, say: "I don't know based on the provided documents."
- Be concise and helpful.

Context:
{context}

Question:
{q}
""".strip()

    answer = llm.invoke(prompt).content.strip()

    final = (
        f"{answer}\n\n"
        "I’ve shared the official documents below. Please feel free to read through them — "
        "you can post any questions here and I’ll be happy to help.\n\n"
        "**Sources**\n" + "\n".join(sources)
    )

    set_cached_answer(topic_name, q, {"assistant_message": final})
    state["assistant_message"] = final
    return state


def run_topic_turn(state, topic_name: str, content: str):
    state = detect_intent(state)
    intent = state.get("intent", "CONFUSED")

    if intent == "CURIOUS":
        return handle_curious(state, topic_name, content)
    if intent in ("PAUSE", "TIRED"):
        return handle_pause(state)
    if intent in ("GOT_IT", "DONE"):
        return handle_done(state)
    return handle_confused(state, topic_name)
