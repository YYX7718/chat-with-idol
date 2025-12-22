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
        <source>《周易·咸卦》：咸，亨，利贞，取女吉。\n这句话大意是：感应相合则亨通，守正有利，婚配为吉。</source>
        <interpretation>咸卦象征感应与互动。这里用“更像/可能/倾向”来表达，不做绝对断言。</interpretation>
        <comfort>别担心，一切都会好的。</comfort>
        <question>你需要我再给你一些更具体的建议，还是想先让我陪你聊聊？</question>
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
        self.assertIn('《周易·咸卦》：咸，亨，利贞，取女吉。', result)
        self.assertIn('咸卦象征感应与互动', result)
        self.assertIn('别担心，一切都会好的。', result)
        self.assertIn('你需要我再给你一些更具体的建议', result)

if __name__ == '__main__':
    unittest.main()
