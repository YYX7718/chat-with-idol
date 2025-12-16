import time

class StateManager:
    """简单的会话状态机管理器（内存实现，生产应持久化）

    状态：DIVINATION -> TRANSITION -> IDOL_CHAT
    """

    ALLOWED_TRANSITIONS = {
        None: ['DIVINATION'],
        'DIVINATION': ['TRANSITION'],
        'TRANSITION': ['IDOL_CHAT'],
        'IDOL_CHAT': []
    }

    def __init__(self):
        # { session_id: {state: str, updated_at: timestamp} }
        self._states = {}

    def get_state(self, session_id):
        entry = self._states.get(session_id)
        return entry['state'] if entry else None

    def set_state(self, session_id, new_state):
        current = self.get_state(session_id)
        if not self.can_transition(current, new_state):
            raise ValueError(f"非法的状态迁移: {current} -> {new_state}")
        self._states[session_id] = {
            'state': new_state,
            'updated_at': time.time()
        }
        return self._states[session_id]

    def can_transition(self, from_state, to_state):
        allowed = self.ALLOWED_TRANSITIONS.get(from_state, [])
        return to_state in allowed

    def reset_state(self, session_id):
        if session_id in self._states:
            del self._states[session_id]


# 全局实例（可被注入或替换）
state_manager = StateManager()
