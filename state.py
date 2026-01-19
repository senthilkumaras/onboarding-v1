from typing import TypedDict, Literal, List

Intent = Literal["CONFUSED", "CURIOUS", "GOT_IT", "TIRED", "PAUSE", "CHOOSE_TOPIC", "UNKNOWN"]

class OnboardingState(TypedDict, total=False):
    # conversation
    user_message: str
    assistant_message: str

    # orchestration
    current_topic: str
    covered_topics: List[str]
    pending_topics: List[str]

    # topic workflow
    overview: str
    intent: Intent

    # control
    is_done: bool
    pause_requested: bool
