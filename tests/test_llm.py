import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    def setUp(self):
        # 保存原始环境变量
        self.original_api_key = os.environ.get('OPENAI_API_KEY')
        self.original_base_url = os.environ.get('OPENAI_BASE_URL')
        self.original_model = os.environ.get('LLM_MODEL')
        
        # 设置测试环境变量
        os.environ['OPENAI_API_KEY'] = 'test-key'
        os.environ['OPENAI_BASE_URL'] = 'https://api.test.com/v1'
        os.environ['LLM_MODEL'] = 'gpt-3.5-turbo'
        
        self.llm_client = LLMClient()
    
    def tearDown(self):
        # 恢复原始环境变量
        if self.original_api_key:
            os.environ['OPENAI_API_KEY'] = self.original_api_key
        else:
            del os.environ['OPENAI_API_KEY']
        
        if self.original_base_url:
            os.environ['OPENAI_BASE_URL'] = self.original_base_url
        else:
            del os.environ['OPENAI_BASE_URL']
        
        if self.original_model:
            os.environ['LLM_MODEL'] = self.original_model
        else:
            del os.environ['LLM_MODEL']
    
    @patch('openai.ChatCompletion.create')
    def test_generate_response_openai(self, mock_chat_completion):
        """测试使用OpenAI模型生成响应"""
        # 模拟OpenAI响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '测试响应'
        mock_chat_completion.return_value = mock_response
        
        # 调用生成响应方法
        result = self.llm_client.generate_response('你好')
        
        # 验证结果
        self.assertEqual(result, {'content': '测试响应'})
        mock_chat_completion.assert_called_once()
    
    @patch('deepseek.Client')
    def test_generate_response_deepseek(self, mock_client):
        """测试使用DeepSeek模型生成响应"""
        # 设置DeepSeek模型
        self.llm_client.model = 'deepseek-chat'
        
        # 模拟DeepSeek客户端和响应
        mock_deepseek_response = MagicMock()
        mock_deepseek_response.choices[0].message.content = 'DeepSeek测试响应'
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_deepseek_response
        mock_client.return_value = mock_client_instance
        
        # 调用生成响应方法
        result = self.llm_client.generate_response('你好')
        
        # 验证结果
        self.assertEqual(result, {'content': 'DeepSeek测试响应'})
        mock_client.assert_called_once()
        mock_client_instance.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    unittest.main()