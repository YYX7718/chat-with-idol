import unittest
from unittest.mock import patch
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.idol_chat_service import IdolChatService
from backend.models.chat_session import ChatSession

class TestIdolChatService(unittest.TestCase):
    def setUp(self):
        self.idol_chat_service = IdolChatService()
    
    def test_get_idol_list(self):
        """测试获取偶像列表"""
        idols = self.idol_chat_service.get_idol_list()
        
        # 验证偶像列表包含预定义的 persona
        idol_names = [idol['name'] for idol in idols]
        self.assertIn('小梦', idol_names)
        self.assertIn('Lady Gaga', idol_names)
        
        # 验证每个偶像都有必要的属性
        for idol in idols:
            self.assertIn('id', idol)
            self.assertIn('name', idol)
    
    def test_detect_divination_intent(self):
        """测试检测占卜意图"""
        # 测试包含明显占卜关键词的消息
        messages_with_intent = [
            '我想占卜一下爱情',
            '我想知道我的运势',
            '可以帮我占卜一下事业吗？'
        ]
        
        for message in messages_with_intent:
            result = self.idol_chat_service.detect_divination_intent(message)
            self.assertTrue(result)
        
        # 测试不包含占卜关键词的消息
        messages_without_intent = [
            '今天天气真好',
            '你吃饭了吗？',
            '我想去看电影',
            '帮我推荐一本书'
        ]
        
        for message in messages_without_intent:
            result = self.idol_chat_service.detect_divination_intent(message)
            self.assertFalse(result)
    
    @patch('backend.services.idol_chat_service.llm_client.generate_response')
    def test_generate_idol_response(self, mock_generate_response):
        """测试生成偶像回复"""
        mock_generate_response.side_effect = [
            'Hello! Nice to meet you :)',
            '你好！很高兴认识你 :)'
        ]
        
        session = ChatSession(idol_id=None, user_id='test')
        session.add_message('user', 'hello')
        
        idol_info = {
            "name": "Lady Gaga",
            "default_language": "en",
            "tone": ["expressive", "compassionate"],
            "culture": "American pop artist",
            "speech_style_notes": "Uses emotional, metaphor-rich language",
            "allowed_references": "public interviews, documentaries, music themes",
            "disallowed": "private relationships, unverified stories"
        }

        result = self.idol_chat_service.generate_idol_response(idol_info, session, translate=True)
        
        # 验证结果
        self.assertIn('persona_reply', result)
        self.assertIn('translation', result)
        self.assertEqual(result['language'], 'en')
    
    def test_get_idol_info(self):
        """测试获取偶像信息"""
        idol_info = self.idol_chat_service.get_idol_info('idol_001')
        self.assertIsNotNone(idol_info)
        self.assertEqual(idol_info['name'], '小梦')
        self.assertEqual(idol_info['default_language'], 'zh')
        
        missing = self.idol_chat_service.get_idol_info('missing_id')
        self.assertIsNone(missing)

if __name__ == '__main__':
    unittest.main()
