import uuid
from datetime import datetime

class Message:
    def __init__(self, role, content):
        self.id = str(uuid.uuid4())
        self.role = role  # user or idol
        self.content = content
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }

class Divination:
    def __init__(self, divination_type, question, result):
        self.id = str(uuid.uuid4())
        self.type = divination_type
        self.question = question
        self.result = result
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "question": self.question,
            "result": self.result,
            "timestamp": self.timestamp
        }

class ChatSession:
    # 会话状态常量
    STATE_DIVINATION = "DIVINATION"
    STATE_TRANSITION = "TRANSITION"
    STATE_IDOL_CHAT = "IDOL_CHAT"

    def __init__(self, idol_id=None, user_id=None):
        self.session_id = str(uuid.uuid4())
        self.idol_id = idol_id
        self.user_id = user_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.messages = []
        self.divinations = []
        self.persona_config = None
        self.transition_step = None
        # 初始状态设置为占卜阶段
        self.current_state = self.STATE_DIVINATION
    
    def add_message(self, role, content):
        message = Message(role, content)
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message
    
    def add_divination(self, divination_type, question, result):
        divination = Divination(divination_type, question, result)
        self.divinations.append(divination)
        self.updated_at = datetime.now().isoformat()
        # 占卜完成后自动切换到过渡阶段
        self.current_state = self.STATE_TRANSITION
        self.transition_step = "ASK_MORE"
        return divination

    def set_state(self, state):
        """
        设置会话状态
        """
        valid_states = [self.STATE_DIVINATION, self.STATE_TRANSITION, self.STATE_IDOL_CHAT]
        if state in valid_states:
            self.current_state = state
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "idol_id": self.idol_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_state": self.current_state,
            "persona_config": self.persona_config,
            "transition_step": self.transition_step,
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    def get_divinations(self):
        return [div.to_dict() for div in self.divinations]

# 会话管理类
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, idol_id=None, user_id=None):
        session = ChatSession(idol_id, user_id)
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id):
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_sessions_by_user(self, user_id):
        return [session for session in self.sessions.values() if session.user_id == user_id]
