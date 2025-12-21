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
        
        result = self.llm_client.generate_response(prompt)
        logger.info("divination_raw_output result=%s", str(result)[:1200])
        
        # 尝试提取 JSON
        try:
            # 查找 JSON 块
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                
                # 格式化输出给用户，去除显式的标签，使其更自然
                formatted_result = f"【{data.get('hexagram', '未知卦象')}】\n\n"
                formatted_result += f"{data.get('source', '')}\n\n"
                formatted_result += f"{data.get('interpretation', '')}\n\n"
                advice = data.get('advice', '')
                if isinstance(advice, list):
                    advice = "\n".join([f"{idx+1}. {str(item).strip()}" for idx, item in enumerate(advice) if str(item).strip()])
                advice = str(advice).strip()
                if advice:
                    formatted_result += f"给你三条落地的小建议：\n{advice}\n\n"

                formatted_result += f"{data.get('comfort', '')}\n\n"
                formatted_result += f"{data.get('question', '')}"
                
                return formatted_result
            else:
                # 如果不是 JSON，尝试直接返回（兼容旧格式或失败情况）
                logger.warning("Failed to parse JSON from divination response")
                return result
        except Exception as e:
            logger.error(f"Error parsing divination response: {e}")
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

请输出一个标准的 JSON 对象，不要包含 Markdown 格式标记（如 ```json），包含以下字段：

1. "hexagram": 专业卦名，尽量包含卦序（如“第01卦 乾为天”）与卦象（上卦/下卦），不要太模糊。
2. "source": 至少两句真实古籍原文（优先《周易》卦辞/爻辞/象传；可辅以《梅花易数》），并在句子前标注来源（如“卦辞：…”“象曰：…”）。
3. "interpretation": 更完整的解读（不少于 500 字），分段写清楚：整体象意、对本问题的指向、可能的利/弊与变数、当下可行的行动方向。禁止确定性断言。
4. "advice": 三条可执行建议（数组形式），每条不超过 40 字。
5. "comfort": 针对用户情绪的安抚（自然口吻，不要出现“【情绪安抚】”标题）。
6. "question": 结尾温柔追问一句，帮助用户继续表达（自然口吻，不要出现“【过渡询问】”标题）。

❌ 禁止行为
- 不得预测具体结果（如成败、时间）
- 不得使用“必然、注定、灾难”等词
- 输出必须是纯 JSON 格式
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
