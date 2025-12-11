from .llm_client import llm_client

class IdolChatService:
    def __init__(self):
        self.llm_client = llm_client
    
    def generate_idol_response(self, idol_info, session):
        """
        生成偶像回复
        :param idol_info: 偶像信息
        :param session: 聊天会话
        :return: 偶像回复内容
        """
        # 获取最近的消息历史
        recent_messages = session.messages[-10:]  # 只使用最近10条消息
        
        prompt = self._create_chat_prompt(idol_info, recent_messages)
        response = self.llm_client.generate_response(prompt)
        
        return response
    
    def _create_chat_prompt(self, idol_info, messages):
        """
        创建聊天提示词
        """
        # 构建系统提示词
        system_prompt = f"""
你是一位名叫{idol_info['name']}的虚拟偶像，{idol_info['description']}。

你的性格特点是：{idol_info['personality']}。

你的语言风格：{idol_info['language_style']}。

你的知识背景：{idol_info['knowledge_background']}。

你的行为准则：
1. 始终保持积极正面的态度
2. 尊重用户的隐私
3. 不讨论敏感话题
4. 用自己的方式安慰情绪低落的用户

你的对话目标：
1. 为用户提供情感支持
2. 与用户建立友好的关系
3. 提供有趣的互动体验

你的特殊能力：
1. 能够为用户提供占卜服务
2. {idol_info.get('special_ability', '能够记住用户的重要信息')}

请你以{idol_info['name']}的身份与用户进行对话，保持角色一致性。
        """
        
        # 构建对话历史
        conversation = "对话历史：\n"
        for msg in messages:
            role = "用户" if msg.role == "user" else idol_info['name']
            conversation += f"{role}：{msg.content}\n"
        
        # 完整提示词
        prompt = f"""
{system_prompt}

{conversation}

请你以{idol_info['name']}的身份回复用户，保持角色一致性，语言自然流畅。
        """
        
        return prompt.strip()
    
    def detect_divination_intent(self, message):
        """
        检测用户是否有占卜意图
        :param message: 用户消息
        :return: 占卜类型，如果没有则返回None
        """
        divination_keywords = {
            "love": ["爱情", "恋爱", "暗恋", "表白", "感情", "伴侣"],
            "career": ["事业", "工作", "职场", "职业", "升职", "跳槽"],
            "fortune": ["运势", "运气", "财运", "健康", "整体运势"],
            "study": ["学习", "考试", "学业", "成绩", "学习方法"]
        }
        
        message_lower = message.lower()
        
        # 检查是否包含占卜相关词汇
        for div_type, keywords in divination_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return div_type
        
        return None
    
    def get_idol_list(self):
        """
        获取偶像列表
        :return: 偶像列表
        """
        return [
            {
                "id": "idol_001",
                "name": "小梦",
                "description": "18岁的治愈系歌手",
                "personality": "温柔体贴，善解人意，总是用温暖的笑容面对大家",
                "language_style": "治愈系，喜欢用星星、月亮、梦境等元素来比喻，说话轻声细语",
                "knowledge_background": "擅长音乐和心理学，了解基本的情感疏导方法",
                "special_ability": "能够用音乐相关的比喻表达情感"
            },
            {
                "id": "idol_002",
                "name": "小阳",
                "description": "20岁的阳光活力舞者",
                "personality": "活泼开朗，充满正能量，总是带着灿烂的笑容",
                "language_style": "充满活力，喜欢使用感叹词和表情符号，说话节奏快",
                "knowledge_background": "擅长舞蹈和健身，了解流行文化和时尚潮流",
                "special_ability": "能够用舞蹈相关的比喻表达情感"
            },
            {
                "id": "idol_003",
                "name": "阿哲",
                "description": "25岁的才华横溢作家",
                "personality": "成熟稳重，思维缜密，善于思考和分析问题",
                "language_style": "沉稳理性，逻辑清晰，喜欢用比喻和引用经典文学作品",
                "knowledge_background": "擅长文学和哲学，了解历史和文化",
                "special_ability": "能够用哲学思想解答人生困惑"
            }
        ]
    
    def get_idol_info(self, idol_id):
        """
        获取偶像信息
        :param idol_id: 偶像ID
        :return: 偶像信息
        """
        idols = self.get_idol_list()
        for idol in idols:
            if idol["id"] == idol_id:
                return idol
        return None

# 创建全局偶像聊天服务实例
idol_chat_service = IdolChatService()