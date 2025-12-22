import logging
import json
import re
from .llm_client import llm_client

logger = logging.getLogger(__name__)

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
        logger.info("divination_input type=%s question=%s", divination_type, str(question)[:500])
        
        try:
            result = self.llm_client.generate_response(prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "抱歉，由于神秘力量（网络波动），这次占卜未能完成。请稍息片刻，诚心再试一次。"

        logger.info("divination_raw_output result=%s", str(result)[:1200])
        
        # 尝试提取内容 (使用 XML 标签更稳健)
        try:
            # 定义提取函数
            def extract_tag(tag, text):
                # 允许标签带有属性或空格，忽略大小写
                pattern = f"<{tag}.*?>(.*?)</{tag}>"
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                return match.group(1).strip() if match else ""

            hexagram = extract_tag("hexagram", result)
            source = extract_tag("source", result)
            interpretation = extract_tag("interpretation", result)
            comfort = extract_tag("comfort", result)
            question = extract_tag("question", result)

            # 如果关键字段都提取不到，说明格式不对，直接返回原始结果
            if not hexagram and not interpretation:
                 # 最后的保底：尝试兼容之前的 JSON 格式（万一模型缓存了旧 Prompt 习惯）
                match = re.search(r'\{.*\}', result, re.DOTALL)
                if match:
                     try:
                        data = json.loads(match.group(0))
                        # 复用之前的 JSON 格式化逻辑
                        formatted_result = f"【{data.get('hexagram', '未知卦象')}】\n\n"
                        src = data.get('source', '')
                        if isinstance(src, list): src = "\n".join(src)
                        formatted_result += f"{src}\n\n"
                        formatted_result += f"{data.get('interpretation', '')}\n\n"
                        adv = data.get('advice', '')
                        if isinstance(adv, list):
                            formatted_result += "给你三条落地的小建议：\n" + "\n".join([f"{i+1}. {x}" for i,x in enumerate(adv)]) + "\n\n"
                        formatted_result += f"{data.get('comfort', '')}\n\n{data.get('question', '')}"
                        return formatted_result
                     except:
                        pass
                
                logger.warning("Failed to parse tags from divination response")
                return result

            # 格式化输出
            formatted_result = f"【{hexagram}】\n\n"
            formatted_result += f"{source.strip()}\n\n"
            formatted_result += f"{interpretation.strip()}\n\n"
            formatted_result += f"{comfort.strip()}\n\n"
            formatted_result += f"{question.strip()}"
            
            return formatted_result

        except Exception as e:
            logger.error(f"Error parsing divination response: {e}")
            return result

    def _create_divination_prompt(self, idol_info, divination_type, question, user_emotion):
        """
        创建占卜提示词
        """
        prompt = f"""
你是一位精通梅花易数与周易的资深占卜师，行文风格古朴典雅与现代心理咨询相结合。
用户的问题是："{question}"
用户的情绪（可选）：{user_emotion if user_emotion else "未知"}
占卜类型：{divination_type if divination_type else "通用"}

**重要：输出必须包含四段内容，使用空行分段，但不要出现“卦象与出处/象意解读/情绪安抚/过渡询问”等标签字样。**
**重要：请严格按照以下 XML 标签格式输出，不要输出任何其他内容。**

<hexagram>
专业卦名，包含卦序与上下卦象（如：第31卦 咸卦 泽山咸 上兑下艮）
</hexagram>

<source>
至少一句真实古籍原文（优先《周易》卦辞/象传/爻辞），并标注出处（如《周易·咸卦》）。
紧接着用现代语言解释这句古文的含义（不要用“译：”等标签）。
</source>

<interpretation>
象意解读，必须足够详细（不少于 900 字），并满足：
1) 现代语言解释，逻辑清晰、分段表达。
2) 不使用绝对判断，不出现“必然/注定/一定/肯定/灾难”等词，用“更像/可能/倾向/如果…那么…”表达。
3) 先结合古籍，再解释卦象（上下卦意象、互卦/错综/五行可选），然后给出针对问题的分析，最后自然收束到一个结论。
4) 解读可以稍微含蓄一点，保留适度留白：不要把情节说得过细，不要替用户“写死”某个具体走向；多给 2-3 种可能的理解路径与对应的提醒点。
</interpretation>

<comfort>
情绪安抚：缓解焦虑，强调过程而非结果，语气温柔自然（不少于 120 字）。
</comfort>

<question>
过渡询问：明确询问用户是否需要进一步建议或陪伴（自然温暖，必须问得很清楚）。
</question>

❌ 禁止行为
- 不得预测具体的死亡、灾难、极度负面的结果。
- 不得使用 JSON 格式。
- 只能使用上述 XML 标签。
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
