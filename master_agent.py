from workflows.topic_workflow import run_overview, run_topic_turn

TOPIC_CONTENT = {
    "company_basics": """
Kaykranmekran Corp is a software company focused on building tools for businesses.
We work in a hybrid model with core hours from 9am to 5pm.
Slack is used for quick communication and email for formal messages.
Your manager is your first point of contact for help.
""",
    "payroll": "Payroll policies are described in the payroll document.",
    "benefits": "Benefits policies are described in the benefits document.",
    "time_off": "Time off policies are described in the time off document.",
    "it_setup": "IT setup policies are described in the IT setup document."
}

TOPICS = ["company_basics", "payroll", "benefits", "time_off", "it_setup"]


# -------------------------
# State helpers
# -------------------------
def init_state():
    return {
        "current_topic": None,
        "covered_topics": [],
        "pending_topics": TOPICS.copy(),
        "assistant_message": "",
        "user_message": "",
        "intent": None,
        "overview": "",
        "pause_requested": False,
    }


# -------------------------
# Welcome + start
# -------------------------
def welcome(state):
    state["assistant_message"] = (
        "Hi there, and a warm welcome to Kaykranmekran Corp! "
        "I'm your AI onboarding assistant. I'll guide you through everything you need "
        "to get started — from company basics to payroll, benefits, time off, and IT setup."
    )
    return state


def start_topic(state):
    if not state["pending_topics"]:
        state["assistant_message"] = "You’ve completed all onboarding topics. 🎉"
        return state

    topic = state["pending_topics"][0]
    state["current_topic"] = topic
    return run_overview(state, topic, TOPIC_CONTENT[topic])


# -------------------------
# Main message handler
# -------------------------
def handle_user_message(state):
    topic = state["current_topic"]
    if not topic:
        return state

    return run_topic_turn(state, topic, TOPIC_CONTENT[topic])


# -------------------------
# Continue workflow
# -------------------------
def continue_to_next_topic(state):
    done = state.get("current_topic")

    if done and done not in state["covered_topics"]:
        state["covered_topics"].append(done)

    if done in state["pending_topics"]:
        state["pending_topics"].remove(done)

    if not state["pending_topics"]:
        state["current_topic"] = None
        state["assistant_message"] = "You’ve completed all onboarding topics. 🎉"
        return state

    next_topic = state["pending_topics"][0]
    state["current_topic"] = next_topic
    return run_overview(state, next_topic, TOPIC_CONTENT[next_topic])
