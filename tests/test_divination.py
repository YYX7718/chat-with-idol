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
        self.assertIn('输出必须是纯 JSON 格式', prompt)
    
    @patch('backend.services.divination_service.llm_client.generate_response')
    def test_generate_divination(self, mock_generate_response):
        """测试生成占卜结果"""
        mock_generate_response.return_value = """
{
  "hexagram": "第01卦 乾为天（乾上乾下）",
  "source": "卦辞：天行健，君子以自强不息。\\n象曰：天行健，君子以自强不息。",
  "interpretation": "这是一段较长的解读，用于覆盖测试对长度的要求。这里不做绝对判断，只给象意方向。\\n\\n就你的问题而言，更多强调自我修持与节奏。\\n\\n利在主动与坚持，弊在急躁与硬碰硬。\\n\\n行动上，先稳住当下，再谈推进。",
  "advice": ["先把真正的担心说清楚", "给关系留一点呼吸感", "用行动代替反复内耗"],
  "comfort": "别急，你已经在往更好的方向走了。",
  "question": "你更在意的是“能不能继续”，还是“怎么继续得更舒服”？"
}
        """.strip()
        
        # 调用占卜服务
        result = self.divination_service.generate_divination(
            idol_info=None,
            divination_type='love',
            question='我和我的伴侣会有未来吗？',
            user_emotion=None
        )
        
        # 验证结果
        self.assertIn('【第01卦 乾为天', result)
        self.assertIn('给你三条落地的小建议', result)
        self.assertIn('你更在意的是', result)
        mock_generate_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()
