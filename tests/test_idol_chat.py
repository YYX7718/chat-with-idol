import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.idol_chat_service import IdolChatService

class TestIdolChatService(unittest.TestCase):
    def setUp(self):
        self.idol_chat_service = IdolChatService()
    
    def test_get_idol_list(self):
        """测试获取偶像列表"""
        idols = self.idol_chat_service.get_idol_list()
        
        # 验证偶像列表包含所有预定义的偶像
        idol_names = [idol['name'] for idol in idols]
        self.assertIn('小梦', idol_names)
        self.assertIn('小阳', idol_names)
        self.assertIn('阿哲', idol_names)
        
        # 验证每个偶像都有必要的属性
        for idol in idols:
            self.assertIn('id', idol)
            self.assertIn('name', idol)
            self.assertIn('description', idol)
            self.assertIn('personality', idol)
    
    def test_detect_divination_intent(self):
        """测试检测占卜意图"""
        # 测试包含明显占卜关键词的消息
        messages_with_intent = [
            '我想占卜一下爱情',
            '能帮我算个卦吗？',
            '我想知道我的运势',
            '可以帮我占卜一下事业吗？'
        ]
        
        for message in messages_with_intent:
            with patch('backend.services.idol_chat_service.llm_client.generate_response') as mock_generate:
                mock_generate.return_value = {'content': 'yes'}
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
            with patch('backend.services.idol_chat_service.llm_client.generate_response') as mock_generate:
                mock_generate.return_value = {'content': 'no'}
                result = self.idol_chat_service.detect_divination_intent(message)
                self.assertFalse(result)
    
    @patch('backend.services.idol_chat_service.llm_client.generate_response')
    def test_generate_idol_response(self, mock_generate_response):
        """测试生成偶像回复"""
        # 模拟LLM响应
        mock_response = {
            'content': '你好呀！我是小梦，很高兴能和你聊天~'
        }
        mock_generate_response.return_value = mock_response
        
        # 调用偶像聊天服务
        result = self.idol_chat_service.generate_idol_response(
            messages=[{'role': 'user', 'content': '你好'}],
            idol_name='小梦',
            idol_personality='友好热情的'
        )
        
        # 验证结果
        self.assertEqual(result['content'], '你好呀！我是小梦，很高兴能和你聊天~')
        self.assertEqual(result['role'], 'idol')
        mock_generate_response.assert_called_once()
    
    def test_get_idol_info(self):
        """测试获取偶像信息"""
        idol_info = self.idol_chat_service._get_idol_info('小梦')
        
        # 验证偶像信息
        self.assertEqual(idol_info['name'], '小梦')
        self.assertEqual(idol_info['personality'], '友好热情的')
        self.assertEqual(idol_info['description'], '充满活力的偶像，总是带着阳光般的笑容')
        
        # 测试获取不存在的偶像
        with self.assertRaises(ValueError):
            self.idol_chat_service._get_idol_info('不存在的偶像')

if __name__ == '__main__':
    unittest.main()