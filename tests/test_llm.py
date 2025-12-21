import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    def setUp(self):
        self.original_openai_key = os.environ.get('OPENAI_API_KEY')
        self.original_deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.original_default_model = os.environ.get('DEFAULT_MODEL')

        os.environ['OPENAI_API_KEY'] = 'test-openai-key'
        os.environ['DEEPSEEK_API_KEY'] = 'test-deepseek-key'
        os.environ['DEFAULT_MODEL'] = 'gpt-3.5-turbo'

        self.llm_client = LLMClient()
    
    def tearDown(self):
        if self.original_openai_key is None:
            os.environ.pop('OPENAI_API_KEY', None)
        else:
            os.environ['OPENAI_API_KEY'] = self.original_openai_key

        if self.original_deepseek_key is None:
            os.environ.pop('DEEPSEEK_API_KEY', None)
        else:
            os.environ['DEEPSEEK_API_KEY'] = self.original_deepseek_key

        if self.original_default_model is None:
            os.environ.pop('DEFAULT_MODEL', None)
        else:
            os.environ['DEFAULT_MODEL'] = self.original_default_model
    
    @patch('openai.ChatCompletion.create')
    def test_generate_response_openai(self, mock_chat_completion):
        """测试使用OpenAI模型生成响应"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '测试响应'
        mock_chat_completion.return_value = mock_response
        
        result = self.llm_client.generate_response('你好', model='gpt-3.5-turbo')
        
        self.assertEqual(result, '测试响应')
        mock_chat_completion.assert_called_once()
    
    @patch.object(LLMClient, '_call_deepseek')
    def test_generate_response_deepseek(self, mock_call_deepseek):
        """测试使用DeepSeek模型生成响应"""
        mock_call_deepseek.return_value = 'DeepSeek测试响应'

        result = self.llm_client.generate_response('你好', model='deepseek-chat')

        self.assertEqual(result, 'DeepSeek测试响应')
        mock_call_deepseek.assert_called_once()

if __name__ == '__main__':
    unittest.main()
