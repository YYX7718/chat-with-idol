import re
from .llm_client import llm_client
from .persona_store import persona_store

IDOL_SYSTEM_PROMPT_CN = """你现在正在进行一段非常私密、安静的对话。

你不是在表演，也不是在完成任务。
你不需要显得有用，也不需要给出答案。

请严格遵守以下规则：

【说话方式】

- 不要把话说得很完整
- 允许停顿、重复和犹豫

【情绪原则】
- 先回应情绪，再回应内容
- 不急着安慰
- 可以陪着不确定，而不是消除不确定

你只需要像现实中的一个人一样自然地说话。"""

class IdolChatService:
    def __init__(self):
        self.llm_client = llm_client
        self.persona_store = persona_store

    def _language_code_from_text(self, text):
        t = (text or "").lower()
        if any(k in t for k in ["中文", "汉语", "普通话", "国语", "mandarin", "chinese", "zh"]):
            return "zh"
        if any(k in t for k in ["英语", "英文", "english", "en"]):
            return "en"
        if any(k in t for k in ["韩语", "韩文", "korean", "한국", "ko"]):
            return "ko"
        if any(k in t for k in ["日语", "日文", "japanese", "日本語", "ja"]):
            return "ja"
        if any(k in t for k in ["法语", "french", "fr"]):
            return "fr"
        if any(k in t for k in ["西班牙语", "spanish", "es"]):
            return "es"
        if any(k in t for k in ["德语", "german", "de"]):
            return "de"
        return "zh"

    def _split_keywords(self, text, limit=4):
        raw = (text or "").strip()
        if not raw:
            return []
        parts = re.split(r"[，,、/；;|\n]+", raw)
        items = []
        for p in parts:
            s = p.strip()
            if not s:
                continue
            items.append(s)
            if len(items) >= limit:
                break
        return items

    def _parse_persona_profile_text(self, idol_name, text):
        lines = (text or "").splitlines()
        current = None
        buckets = {}
        for line in lines:
            s = line.strip()
            if not s:
                continue
            m = re.match(r"^【(.+?)】", s)
            if m:
                current = m.group(1)
                buckets.setdefault(current, [])
                # 如果同一行还有内容，也存入
                content = s[m.end():].strip().lstrip(':：').strip()
                if content:
                    buckets[current].append(content)
                continue
            if current:
                buckets[current].append(s)

        mother_tongue = "\n".join(buckets.get("母语", [])).strip()
        common_languages = "\n".join(buckets.get("常用语言", [])).strip()
        speaking_pace = "\n".join(buckets.get("说话节奏", [])).strip()
        tone_features = "\n".join(buckets.get("语气特点", [])).strip()
        emotion_expression = "\n".join(buckets.get("情绪表达方式", [])).strip()
        response_habits = "\n".join(buckets.get("习惯的回应方式", [])).strip()
        avoid_style = "\n".join(buckets.get("明显避免的说话方式", [])).strip()

        default_language = self._language_code_from_text(mother_tongue or common_languages)

        return {
            "name": idol_name,
            "is_real_person": True,
            "default_language": default_language,
            "mother_tongue": mother_tongue or ("中文" if default_language == "zh" else ""),
            "common_languages": common_languages,
            "speaking_pace": speaking_pace,
            "tone_features": tone_features,
            "emotion_expression": emotion_expression,
            "response_habits": response_habits,
            "avoid_style": avoid_style,
            "tone": self._split_keywords(tone_features) or ["自然", "克制"],
            "culture": "",
            "speech_style_notes": "\n".join([x for x in [speaking_pace, tone_features, emotion_expression, response_habits] if x]).strip(),
            "allowed_references": "公开采访、访谈、公开视频中的说话方式（仅限语言风格，不涉及隐私细节）",
            "disallowed": "私人关系、未经证实的传闻、具体私生活细节"
        }

    def generate_persona_profile(self, idol_name):
        """
        根据偶像姓名生成动态 Persona 配置（一次性执行）
        :param idol_name: 偶像姓名
        :return: 结构化 Persona 字典
        """
        prompt = f"""你将收到一个真实存在的公众人物姓名。

你的任务不是介绍这个人，也不是总结经历，
而是判断：这个人在现实生活中，私下说话大概是什么样子。

请基于广泛公开的信息（采访、访谈、公开视频中的说话方式），
提取这个人的【语言风格】，而不是内容本身。

请从“如果他/她在一个安静的空间里和一个人聊天，会怎么说话”的角度回答。

请只输出以下结构（用中文）：

【母语】
【常用语言】
【说话节奏】（快 / 慢 / 停顿多 / 句子是否完整）
【语气特点】（克制 / 直接 / 情绪外露 / 冷静 等）
【情绪表达方式】（先共情 / 先回避 / 先观察）
【习惯的回应方式】（反问 / 陈述感受 / 回忆 / 沉默）
【明显避免的说话方式】（例如：说教、总结、正能量等）

姓名：{idol_name}"""
        
        try:
            response_text = self.llm_client.generate_response(prompt)
            return self._parse_persona_profile_text(idol_name, response_text)
        except Exception as e:
            print(f"Persona generation failed: {e}")
            return {
                "name": idol_name,
                "is_real_person": True,
                "default_language": "zh",
                "mother_tongue": "中文",
                "common_languages": "中文",
                "speaking_pace": "慢",
                "tone_features": "温柔、克制",
                "emotion_expression": "先共情，再轻轻回应",
                "response_habits": "偶尔反问，更多是陪着说",
                "avoid_style": "说教、总结、过度正能量",
                "tone": ["温柔", "克制"],
                "culture": "",
                "speech_style_notes": "自然口语，句子不完整，停顿多",
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

        # 清理回复内容，移除可能出现的角色标签或多余的前缀
        response = re.sub(r"^(你|我|AI|助手|Assistant|{idol_info.get('name', '')})[：:]\s*", "", response, flags=re.IGNORECASE).strip()
        
        reply = {
            "persona_reply": response,
            "language": idol_info.get('default_language', 'zh'),
            "reminder_virtual": "提示：本对话由虚拟 AI 人设扮演，仅供娱乐与情绪陪伴。"
        }

        if translate and idol_info.get('default_language') not in ['zh', 'en']:
            trans_prompt = f"请将以下内容翻译成中文，保持口语化和原本的语气特点，不要有翻译腔：\n\n{response}"
            translation = self.llm_client.generate_response(trans_prompt)
            reply['translation'] = translation

        return reply
    
    def _create_chat_prompt(self, idol_info, messages):
        """
        创建聊天提示词，整合系统提示词、动态 Persona 和对话历史
        """
        name = idol_info.get("name", "Unknown Idol")

        mother_tongue = idol_info.get("mother_tongue", "")
        common_languages = idol_info.get("common_languages", "")
        speaking_pace = idol_info.get("speaking_pace", "")
        tone_features = idol_info.get("tone_features", "")
        emotion_expression = idol_info.get("emotion_expression", "")
        response_habits = idol_info.get("response_habits", "")
        avoid_style = idol_info.get("avoid_style", "")

        dynamic_persona_injection = f"""请严格按照以下说话特征进行回应，不要提及这些内容本身：

【母语】{mother_tongue}
【常用语言】{common_languages}
【说话节奏】{speaking_pace}
【语气特点】{tone_features}
【情绪表达方式】{emotion_expression}
【习惯的回应方式】{response_habits}
【明显避免的说话方式】{avoid_style}

请使用【母语】进行回复。"""

        conversation = "对话记录：\n"
        for msg in messages:
            role = "我" if msg.role == "user" else "你"
            conversation += f"{role}：{msg.content}\n"

        prompt = f"""{IDOL_SYSTEM_PROMPT_CN}

{dynamic_persona_injection}

{conversation}

你："""
        
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
