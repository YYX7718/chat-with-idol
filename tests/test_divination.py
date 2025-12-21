import unittest
from unittest.mock import patch
from backend.services.divination_service import DivinationService

class TestDivinationService(unittest.TestCase):
    def setUp(self):
        self.divination_service = DivinationService()
    
    def test_get_divination_types(self):
        """测试获取占卜类型列表"""
        types = self.divination_service.get_divination_types()
        type_values = [t["type"] for t in types]
        self.assertEqual(type_values, ['love', 'career', 'fortune', 'study'])
    
    def test_create_divination_prompt(self):
        """测试创建占卜提示词"""
        prompt = self.divination_service._create_divination_prompt(
            idol_info=None,
            divination_type='love',
            question='我和我的伴侣会有未来吗？',
            user_emotion=None
        )
        
        # 验证提示词包含必要的信息
        self.assertIn('占卜类型：love', prompt)
        self.assertIn('我和我的伴侣会有未来吗？', prompt)
        self.assertIn('请严格按照以下 XML 标签格式输出', prompt)
    
    @patch('backend.services.divination_service.llm_client.generate_response')
    def test_generate_divination(self, mock_generate_response):
        """测试生成占卜结果"""
        # 模拟 LLM 返回 XML
        mock_generate_response.return_value = """
        <hexagram>第31卦 咸卦</hexagram>
        <source>卦辞：咸，亨，利贞，取女吉。</source>
        <interpretation>咸卦象征感应。</interpretation>
        <advice>
        1. 保持真诚
        2. 顺其自然
        3. 多沟通
        </advice>
        <comfort>别担心，一切都会好的。</comfort>
        <question>你现在感觉如何？</question>
        """
        
        # 调用占卜服务
        result = self.divination_service.generate_divination(
            idol_info=None,
            divination_type='love',
            question='我和我的伴侣会有未来吗？',
            user_emotion=None
        )
        
        # 验证结果包含格式化后的内容
        self.assertIn('【第31卦 咸卦】', result)
        self.assertIn('卦辞：咸，亨，利贞，取女吉。', result)
        self.assertIn('咸卦象征感应。', result)
        self.assertIn('保持真诚', result)
        self.assertIn('别担心，一切都会好的。', result)
        self.assertIn('你现在感觉如何？', result)

if __name__ == '__main__':
    unittest.main()
