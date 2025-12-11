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
    def __init__(self, idol_id, user_id=None):
        self.session_id = str(uuid.uuid4())
        self.idol_id = idol_id
        self.user_id = user_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.messages = []
        self.divinations = []
    
    def add_message(self, role, content):
        message = Message(role, content)
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message
    
    def add_divination(self, divination_type, question, result):
        divination = Divination(divination_type, question, result)
        self.divinations.append(divination)
        self.updated_at = datetime.now().isoformat()
        return divination
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "idol_id": self.idol_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    def get_divinations(self):
        return [div.to_dict() for div in self.divinations]

# 会话管理类
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, idol_id, user_id=None):
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
