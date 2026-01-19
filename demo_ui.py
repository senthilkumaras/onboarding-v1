import streamlit as st
st.set_page_config(page_title="AI Onboarding Agent", layout="wide")

import base64
import uuid
from pathlib import Path

from master_agent import (
    init_state,
    welcome,
    start_topic,
    handle_user_message,
    continue_to_next_topic,
)

from rate_limit import make_user_key, allow
from observability import log_params_once, log_metric

TOPICS = ["company_basics", "payroll", "benefits", "time_off", "it_setup"]
DOCS_DIR = Path("./rag_docs")


def show_pdf(file_path: Path):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600"></iframe>',
        unsafe_allow_html=True,
    )


# ---- One-time init (prevents duplicates) ----
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.state = init_state()
    st.session_state.chat = []
    st.session_state.selected_pdf = None
    st.session_state.user_input = ""

    # MLflow params once
    log_params_once({
        "runtime": "public-safe",
        "llm_provider": "groq",
        "vectorstore": "faiss",
        "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
    })

    st.session_state.state = welcome(st.session_state.state)
    st.session_state.chat.append(("agent", st.session_state.state["assistant_message"]))

    st.session_state.state = start_topic(st.session_state.state)
    st.session_state.chat.append(("agent", st.session_state.state["assistant_message"]))


# ---- Sidebar workflow ----
st.sidebar.title("🏢 Kaykranmekran Corp")
st.sidebar.subheader("Onboarding Progress")

covered = st.session_state.state.get("covered_topics", [])
current = st.session_state.state.get("current_topic")

for t in TOPICS:
    name = t.replace("_", " ").title()
    if t in covered:
        st.sidebar.success(name)
    elif t == current:
        st.sidebar.info(f"▶ {name}")
    else:
        st.sidebar.warning(name)


# ---- Main UI ----
st.title("🧠 AI Onboarding Assistant")

for role, msg in st.session_state.chat:
    if role == "agent":
        st.markdown(f"**Agent:** {msg}")

        # Show PDF open buttons only if mentioned in the message
        for f in DOCS_DIR.glob("*.pdf"):
            if f.name in msg:
                if st.button(f"📄 Open {f.name}", key=f"open_{f.name}_{len(st.session_state.chat)}"):
                    st.session_state.selected_pdf = f
    else:
        st.markdown(f"**You:** {msg}")


# ---- PDF viewer ----
if st.session_state.selected_pdf:
    st.divider()
    st.subheader(f"📄 Viewing: {st.session_state.selected_pdf.name}")
    show_pdf(st.session_state.selected_pdf)


# ---- Input handling ----
def send_message():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return

    # Public-safe rate limiting
    ua = st.context.headers.get("User-Agent", "unknown") if hasattr(st, "context") else "unknown"
    key = make_user_key(st.session_state.session_id, ua)
    if not allow(key):
        st.warning("Too many requests. Please slow down for a minute 🙂")
        return

    st.session_state.chat.append(("user", user_input))

    st.session_state.state["user_message"] = user_input
    st.session_state.state = handle_user_message(st.session_state.state)
    st.session_state.chat.append(("agent", st.session_state.state["assistant_message"]))

    # Metrics
    log_metric("messages_total", float(len(st.session_state.chat)))
    log_metric("topics_completed", float(len(st.session_state.state.get("covered_topics", []))))

    # Auto-continue on affirmations
    if user_input.lower() in ("next", "continue", "yes", "ok", "awesome", "cool", "yep"):
        st.session_state.state = continue_to_next_topic(st.session_state.state)
        st.session_state.chat.append(("agent", st.session_state.state["assistant_message"]))

    st.session_state.user_input = ""


st.text_input("Type your message and press Enter", key="user_input", on_change=send_message)
