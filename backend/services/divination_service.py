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
        创建占卜提示词 - 恢复深度解析版本
        """
        prompt = f"""你是一位隐居山林的易经宗师，精通梅花易数与六爻预测。你不仅通晓古籍，更能洞察人性，将易理与心理慰藉完美融合。

现在，有一位缘主求卦，其所求之事为："{question}"
占卜类型：{divination_type if divination_type else "综合运势"}
缘主当前心境：{user_emotion if user_emotion else "平静且期待"}

请你凝神静气，起得一卦。你的解析必须包含以下几个维度，且每个维度都要深入透彻。

**重要要求：**
1. **深度解析**：总字数必须在 1000 字以上。不要敷衍，要像真正的宗师一样条分缕析。
2. **结构要求**：请将你的回答放入以下 XML 标签中，以便于我提取。但标签内部的内容应该是纯粹的解析文字，不需要任何标题或前缀。

<hexagram>
这里写卦名。格式：第X卦 [卦名] [卦象描述]（例如：第31卦 咸卦 泽山咸 上兑下艮）。
</hexagram>

<source>
这里给出卦辞或象传原文。必须引用《周易》或相关古籍的真实原文。
紧接着，请你用充满禅意的现代语言，解析这段古文的深层含义。
</source>

<interpretation>
这是最核心的部分，要求极其详尽（不少于 800 字）：
- 首先，从卦象的意象出发（如：泽在山上，山感泽气）。
- 其次，结合互卦、变卦或五行生克，分析事情的现状与潜在变化。
- 再次，针对缘主的问题 "{question}"，给出多层次的剖析。不要给死结论，要给方向，要用“或许”、“倾向于”、“若能...则...”等温和而专业的措辞。
- 最后，给出一个既含蓄又富有智慧的阶段性总结。
</interpretation>

<comfort>
这里是你的慈悲之心。请针对缘主的焦虑或疑惑，给出一份深度的情绪慰藉（不少于 150 字）。
强调因果，强调过程的意义，让缘主感受到被理解与被陪伴的温暖。
</comfort>

<question>
这是你对缘主的关怀。用一两句话自然地询问缘主，是否还有其他疑惑，或者是否需要进一步的指引。
</question>

**禁忌：**
- 绝对禁止使用 JSON 格式。
- 绝对禁止出现“灾难、必死、死局”等极端断语。
- 保持宗师风范，言辞雅致，不落俗套。"""
        
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
