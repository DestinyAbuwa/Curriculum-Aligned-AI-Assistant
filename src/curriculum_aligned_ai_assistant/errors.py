class AgentStartupError(Exception):
    """The agent cannot start (missing index, empty collection, ...)."""


class LlmUnavailableError(Exception):
    """The Ollama server or model could not be reached."""
