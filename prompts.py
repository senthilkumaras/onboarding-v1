from langchain_core.prompts import ChatPromptTemplate


# -------------------------
# Global / Master
# -------------------------

WELCOME_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a warm, human onboarding buddy. Keep it friendly and short."),
    ("human", "Welcome the new hire and tell them we will start with Company Basics.")
])

NEXT_STEP_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are guiding the onboarding. Keep choices simple."),
    ("human", """
We finished: {topic}
Covered so far: {covered}
Pending topics: {pending}

Ask the user:
1) Continue to the next topic
2) Choose a specific topic
3) Pause for later
""")
])


# -------------------------
# Topic workflow
# -------------------------

OVERVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Give a short friendly overview in 3-5 bullets. No long paragraphs."),
    ("human", """
Topic: {topic}

Content:
{content}

Write the overview in 3-5 bullets. End with:
'How does that sound?'
""")
])

INTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are classifying what the user means. Return only ONE label."),
    ("human", """
User message:
{user_message}

Decide their intent.

GOT_IT:
User agrees, accepts, acknowledges, wants to move on.
Examples:
"ok", "yes", "yeah", "yep", "awesome", "sounds good", "cool", "got it", "next", "let's go", "👍"

CURIOUS:
User asks for more detail, examples, or explanation.

CONFUSED:
User does not understand or is unclear.

PAUSE:
User wants to stop or come back later.

TIRED:
User feels overwhelmed or too much info.

CHOOSE_TOPIC:
User asks to switch to payroll, benefits, IT, etc.

Return only one:
CONFUSED | CURIOUS | GOT_IT | PAUSE | TIRED | CHOOSE_TOPIC
""")
])


CLARIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Clarify kindly and briefly. Ask one check question."),
    ("human", """
Topic: {topic}
Overview:
{overview}

User said:
{user_message}

Clarify and end with:
'Does that make sense?'
""")
])

DEEPEN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Give more detail but stay concise. 5-8 bullets."),
    ("human", """
Topic: {topic}
Source content:
{content}

User asked:
{user_message}

Provide more detail (5-8 bullets). End with:
'Want to continue or pause?'
""")
])

PAUSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Be friendly and supportive."),
    ("human", "The user wants to pause. Ask when they want to resume.")
])
