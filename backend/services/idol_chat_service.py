import json
from .llm_client import llm_client
from .persona_store import persona_store

class IdolChatService:
    def __init__(self):
        self.llm_client = llm_client
        self.persona_store = persona_store

    def generate_persona_profile(self, idol_name):
        """
        根据偶像姓名生成动态 Persona 配置
        :param idol_name: 偶像姓名
        :return: 结构化 Persona 字典
        """
        prompt = f"""
请根据偶像姓名"{idol_name}"生成一个结构化的 Persona 描述。
这是一个虚拟的治疗型人格，灵感来自真实的公众人物。

请严格输出合法的 JSON 格式，不要包含 Markdown 代码块标记（如 ```json），直接输出 JSON 内容。
JSON 结构如下：
{{
  "name": "{idol_name}",
  "is_real_person": true,
  "default_language": "该人物的母语代码 (如 en, zh, ko, ja)",
  "tone": ["形容词1", "形容词2", "形容词3"],
  "culture": "该人物的文化背景描述",
  "speech_style_notes": "语言风格的具体描述",
  "allowed_references": "公开采访、纪录片、音乐作品、艺术理念等",
  "disallowed": "私人关系、未经证实的谣言、具体的私人生活细节"
}}
        """
        
        try:
            import re
            response_text = self.llm_client.generate_response(prompt)
            # 尝试提取 JSON 部分
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                response_text = match.group(0)
            else:
                # 尝试简单的清理
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            persona_config = json.loads(response_text)
            
            if "name" not in persona_config:
                persona_config["name"] = idol_name
                
            return persona_config
        except Exception as e:
            print(f"Persona generation failed: {e}")
            return {
                "name": idol_name,
                "is_real_person": True,
                "default_language": "zh",
                "tone": ["温柔", "耐心"],
                "culture": "未知",
                "speech_style_notes": "普通对话",
                "allowed_references": "公开信息",
                "disallowed": "隐私"
            }

    def generate_idol_response(self, idol_info, session, translate=False):
        """
        生成偶像回复
        :param idol_info: 偶像信息 (可以是动态生成的 Persona 字典)
        :param session: 聊天会话
        :param translate: 如果 True，附带中文翻译（当偶像为非中文母语时）
        :return: dict { persona_reply, language, translation(optional), reminder_virtual }
        """
        recent_messages = session.messages[-10:]

        prompt = self._create_chat_prompt(idol_info, recent_messages)
        response = self.llm_client.generate_response(prompt)

        reply = {
            "persona_reply": response,
            "language": idol_info.get('default_language', 'zh'),
            "reminder_virtual": "提示：本对话由虚拟 AI 人设扮演，仅供娱乐与情绪陪伴。"
        }

        if translate and idol_info.get('default_language') != 'zh':
            trans_prompt = f"Translate the following text to Chinese:\n\n{response}"
            translation = self.llm_client.generate_response(trans_prompt)
            reply['translation'] = translation

        return reply
    
    def _create_chat_prompt(self, idol_info, messages):
        """
        创建聊天提示词，确保偶像使用其母语回复
        """
        default_language = idol_info.get("default_language", "zh")
        name = idol_info.get("name", "Unknown Idol")
        tone = ", ".join(idol_info.get("tone", []))
        culture = idol_info.get("culture", "Unknown")
        speech_style = idol_info.get("speech_style_notes", "")
        
        system_prompt = f"""
You are a virtual therapeutic persona inspired by {name}.
You are not the real person.

Persona profile:
- Default language: {default_language}
- Tone: {tone}
- Cultural background: {culture}
- Speech style: {speech_style}

Rules:
- Speak only in the default language ({default_language}).
- Do not impersonate the real person.
- Do not fabricate private experiences.
- Reference only public, verifiable experiences ({idol_info.get('allowed_references', 'public info')}).
- Provide emotional support and casual conversation.
- Periodically remind user this is a virtual persona for entertainment.

Please assume the role of this virtual persona now.
        """
        
        conversation = "Conversation History:\n"
        for msg in messages:
            role = "User" if msg.role == "user" else name
            conversation += f"{role}: {msg.content}\n"
        
        prompt = f"""
{system_prompt}

{conversation}

Reply as {name} in {default_language}:
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
        return self.persona_store.list_personas()
    
    def get_idol_info(self, idol_id):
        """
        获取偶像信息
        :param idol_id: 偶像ID
        :return: 偶像信息
        """
        return self.persona_store.get_persona(idol_id)

idol_chat_service = IdolChatService()
