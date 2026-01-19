from dataclasses import dataclass
import os

@dataclass(frozen=True)
class ModelConfig:
    # OpenAI
    gpt_intent_model: str = os.getenv("GPT_INTENT_MODEL", "gpt-4o-mini")

    # Groq
    llama_voice_model: str = os.getenv("LLAMA_VOICE_MODEL", "llama-3.1-8b-instant")

    # Anthropic (set to the ACTIVE Claude model you used)
    claude_hr_model: str = os.getenv("CLAUDE_HR_MODEL", "claude-sonnet-4-5-20250929")

    # Cohere
    command_r_model: str = os.getenv("COMMAND_R_MODEL", "command-a-03-2025")


@dataclass(frozen=True)
class FeatureFlags:
    # Keep true since you said keys are ready, but you can toggle anytime.
    use_claude: bool = os.getenv("USE_CLAUDE", "true").lower() == "true"
    use_command_r: bool = os.getenv("USE_COMMAND_R", "true").lower() == "true"


MODELS = ModelConfig()
FLAGS = FeatureFlags()
