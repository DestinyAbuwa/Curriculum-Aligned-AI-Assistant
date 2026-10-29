class AgentStartupError(Exception):
    """The agent cannot start (missing index, empty collection, ...)."""


class LlmUnavailableError(Exception):
    """The configured language model could not be reached or loaded."""
