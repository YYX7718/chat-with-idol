import unittest
from unittest.mock import patch, MagicMock
from backend.services.divination_service import DivinationService

class TestDivinationService(unittest.TestCase):
    def setUp(self):
        self.divination_service = DivinationService()
    
    def test_get_divination_types(self):
        """测试获取占卜类型列表"""
        types = self.divination_service.get_divination_types()
        expected_types = ['love', 'career', 'fortune', 'study']
        self.assertEqual(types, expected_types)
    
    def test_create_divination_prompt(self):
        """测试创建占卜提示词"""
        prompt = self.divination_service._create_divination_prompt(
            type='love',
            question='我和我的伴侣会有未来吗？',
            idol_name='小梦'
        )
        
        # 验证提示词包含必要的信息
        self.assertIn('爱情占卜', prompt)
        self.assertIn('我和我的伴侣会有未来吗？', prompt)
        self.assertIn('小梦', prompt)
        self.assertIn('友好热情的', prompt)
    
    @patch('backend.services.divination_service.llm_client.generate_response')
    def test_generate_divination(self, mock_generate_response):
        """测试生成占卜结果"""
        # 模拟LLM响应
        mock_response = {
            'content': '根据星象显示，你们的关系充满潜力...'
        }
        mock_generate_response.return_value = mock_response
        
        # 调用占卜服务
        result = self.divination_service.generate_divination(
            type='love',
            question='我和我的伴侣会有未来吗？',
            idol_name='小梦'
        )
        
        # 验证结果
        self.assertEqual(result, mock_response['content'])
        mock_generate_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()