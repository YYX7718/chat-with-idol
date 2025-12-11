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
        # 占卜类型描述
        type_descriptions = {
            "love": "爱情",
            "career": "事业",
            "fortune": "运势",
            "study": "学业"
        }
        
        type_desc = type_descriptions.get(divination_type, divination_type)
        
        # 情绪描述
        emotion_desc = f"情绪{user_emotion}" if user_emotion else ""
        
        # 构建提示词
        prompt = f"""
你是一位名叫{idol_info['name']}的虚拟偶像，{idol_info['personality']}。
你的语言风格：{idol_info['language_style']}。

现在你需要为用户提供{type_desc}占卜服务。

用户的问题是："{question}"
用户的当前状态：{emotion_desc}
占卜的类型：{type_desc}运势

请你为用户提供一个符合你角色设定的占卜结果，要求：
1. 使用符合你性格的语言风格
2. 结合用户的问题和情绪状态
3. 保持积极正面的基调
4. 语言要生动形象，富有情感
5. 结果长度适中，避免过于冗长
6. 可以加入一些与你的角色相关的元素或比喻

输出格式：
{idol_info['name']}的{type_desc}占卜：

[占卜结果内容]

[鼓励性结尾]
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