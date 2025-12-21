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
            advice_raw = extract_tag("advice", result)
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
            formatted_result += f"{source}\n\n"
            formatted_result += f"{interpretation}\n\n"
            
            if advice_raw:
                formatted_result += "给你三条落地的小建议：\n"
                # 处理建议列表（按行分割）
                advice_lines = [line.strip() for line in advice_raw.split('\n') if line.strip()]
                for idx, line in enumerate(advice_lines):
                    # 如果模型自己加了序号，去掉它
                    clean_line = re.sub(r'^\d+[\.、]\s*', '', line)
                    formatted_result += f"{idx+1}. {clean_line}\n"
                formatted_result += "\n"

            formatted_result += f"{comfort}\n\n"
            formatted_result += f"{question}"
            
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

**重要：请严格按照以下 XML 标签格式输出，内容必须详实、深入，不要输出任何其他内容。**

<hexagram>
专业卦名，包含卦序与上下卦象（如：第31卦 咸卦 泽山咸 上兑下艮）
</hexagram>

<source>
请引用至少两段与该卦象最相关的古籍原文（如《周易》卦辞、爻辞、《梅花易数》象辞等）。
每一段原文后，必须紧跟一段白话文简译，帮助用户理解古籍含义。
</source>

<interpretation>
请提供一份极具深度的卦象解读（字数不少于 600 字）。请严格按照以下逻辑分段撰写：
1. **卦象详解**：从上下卦的五行生克、自然意象（如山、泽、火、水等）入手，详细解释该卦的本质含义。
2. **结合古籍**：简要剖析上述引用的古籍原文如何对应到当前的卦象中。
3. **深度分析**：针对用户的问题（"{question}"），结合卦象变化（变爻）进行具体、细腻的分析。分析现状、潜在的阻碍、发展的趋势。请把用户带入到卦象的情境中去。
4. **最终结论**：基于以上分析，给出一个明确但不绝对的总结性判断。
</interpretation>

<advice>
基于结论，给出 3-4 条具体、可执行的行动建议。每条建议应当包含“做什么”和“怎么做”。
</advice>

<comfort>
针对用户可能存在的焦虑或困惑，给予一段温暖、治愈、富有哲理的情绪疏导（100字左右）。
</comfort>

<question>
结尾抛出一个引导性的问题，激发用户对现状的深层思考，或引导用户进行下一步的行动（自然温暖）。
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
