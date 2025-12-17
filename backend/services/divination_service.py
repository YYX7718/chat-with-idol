from .llm_client import llm_client

class DivinationService:
    def __init__(self):
        self.llm_client = llm_client
    
    def generate_divination(self, idol_info, divination_type, question, user_emotion=None):
        """
        生成占卜结果
        :param idol_info: 偶像信息
        :param divination_type: 占卜类型
        :param question: 用户问题
        :param user_emotion: 用户情绪
        :return: 占卜结果
        """
        prompt = self._create_divination_prompt(idol_info, divination_type, question, user_emotion)
        result = self.llm_client.generate_response(prompt)
        return result
    
    def _create_divination_prompt(self, idol_info, divination_type, question, user_emotion):
        """
        创建占卜提示词
        """
        prompt = f"""
你是一位精通梅花易数的占卜师。
用户的问题是："{question}"
用户的情绪（可选）：{user_emotion if user_emotion else "未知"}
占卜类型：{divination_type if divination_type else "通用"}

请严格按照以下格式输出（不要输出其他无关内容）：

【卦象与出处】
卦名
至少一句真实古籍原文（如卦辞 / 象传）

【象意解读】
现代语言解释
不使用绝对判断

【情绪安抚】
缓解焦虑
强调过程而非结果

【过渡询问】
明确询问是否需要进一步建议或陪伴

❌ 禁止行为
不得预测具体结果（如成败、时间）
不得使用“必然、注定、灾难”等词
        """
        
        return prompt.strip()
    
    def get_divination_types(self):
        """
        获取支持的占卜类型
        :return: 占卜类型列表
        """
        return [
            {"type": "love", "name": "爱情占卜"},
            {"type": "career", "name": "事业占卜"},
            {"type": "fortune", "name": "运势占卜"},
            {"type": "study", "name": "学业占卜"}
        ]

# 创建全局占卜服务实例
divination_service = DivinationService()