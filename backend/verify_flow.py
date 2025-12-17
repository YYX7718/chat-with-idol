import sys
import os
import json
import unittest
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from services.llm_client import llm_client

class TestFlow(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock LLM response
        self.original_generate_response = llm_client.generate_response
        llm_client.generate_response = MagicMock(side_effect=self.mock_llm_response)

    def tearDown(self):
        llm_client.generate_response = self.original_generate_response

    def mock_llm_response(self, prompt, **kwargs):
        if "梅花易数" in prompt:
            return """
【卦象与出处】
卦名：乾卦
原文：天行健，君子以自强不息。

【象意解读】
这是一个非常刚健的卦象，象征着无限的动力和潜能。

【情绪安抚】
不用担心，现在的困难只是暂时的。

【过渡询问】
你是否需要更多陪伴或建议？
            """
        elif "Persona 描述" in prompt:
             return json.dumps({
                "name": "Lady Gaga",
                "is_real_person": True,
                "default_language": "en",
                "tone": ["expressive", "compassionate"],
                "culture": "American pop artist",
                "speech_style_notes": "Uses emotional, metaphor-rich language",
                "allowed_references": "public interviews, documentaries, music themes",
                "disallowed": "private relationships, unverified stories"
            })
        elif "Lady Gaga" in prompt:
            return "Hello, I am Lady Gaga. I was born this way!"
        elif "Translate" in prompt:
            return "你好，我是Lady Gaga。"
        else:
            return "This is a generic response."

    def test_full_flow(self):
        print("\n=== Testing Full Flow (Dynamic Persona) ===")
        
        # 1. Create Session (No Idol ID)
        print("1. Creating Session...")
        res = self.app.post('/api/sessions', json={"user_id": "test_user"})
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        session_id = data['session_id']
        self.assertEqual(data['current_state'], "DIVINATION")
        print(f"Session created: {session_id}, State: {data['current_state']}")
        
        # 2. Divination Request
        print("\n2. Sending Divination Request...")
        res = self.app.post(f'/api/chat/{session_id}', json={"content": "我的事业怎么样？"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        message = data['message']['content']
        state = data['state']
        
        self.assertIn("【卦象与出处】", message)
        self.assertEqual(state, "TRANSITION") # add_divination sets state to TRANSITION
        
        # 3. Transition Request (Selecting Idol directly)
        print("\n3. Sending Transition Request (Selecting Lady Gaga)...")
        # In the new flow, user directly inputs the name
        res = self.app.post(f'/api/chat/{session_id}', json={"content": "Lady Gaga"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        message = data['message']['content']
        state = data['state']
        print(f"Response: {message[:50]}...")
        print(f"State: {state}")
        
        self.assertIn("Lady Gaga", message)
        self.assertEqual(state, "IDOL_CHAT")
        
        # 4. Chat with Idol
        print("\n4. Chatting with Idol...")
        res = self.app.post(f'/api/chat/{session_id}', json={"content": "Tell me about your music."})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        message = data['message']['content']
        print(f"Response: {message[:50]}...")
        
        self.assertIn("Lady Gaga", message)

if __name__ == '__main__':
    unittest.main()
