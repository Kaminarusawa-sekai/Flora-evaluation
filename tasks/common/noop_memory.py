class NoopMemory:
    """Fallback memory implementation to keep flows running without llm_memory."""

    _state_store = {}

    def add_memory_intelligently(self, *_args, **_kwargs) -> None:
        return None

    def build_conversation_context(self, *_args, **_kwargs) -> str:
        return ""

    def retrieve_relevant_memory(self, *_args, **_kwargs) -> str:
        return ""

    def build_planning_context(self, *_args, **_kwargs) -> str:
        return ""

    def build_execution_context(self, *_args, **_kwargs) -> str:
        return ""

    def get_core_memory(self, *_args, **_kwargs) -> str:
        return ""

    def save_state(self, task_id: str, state_data) -> None:
        if not task_id:
            return
        self._state_store[task_id] = state_data

    def load_state(self, task_id: str):
        if not task_id:
            return None
        return self._state_store.get(task_id)
