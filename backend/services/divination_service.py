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
            # 1. 预处理：移除 Markdown 代码块标记（最常见的干扰源）
            # 即使 LLM 输出了 ```json ... ```，我们先把它剥离掉
            clean_result = result
            if "```json" in clean_result:
                clean_result = clean_result.replace("```json", "").replace("```", "")
            elif "```" in clean_result:
                clean_result = clean_result.replace("```", "")
            
            # 2. 查找最外层的 JSON 对象
            # 使用非贪婪匹配或 DOTALL 确保跨行匹配
            match = re.search(r'\{.*\}', clean_result, re.DOTALL)
            
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                
                # 格式化输出给用户，去除显式的标签，使其更自然
                formatted_result = f"【{data.get('hexagram', '未知卦象')}】\n\n"
                
                # 处理 source，可能是字符串也可能是列表
                source = data.get('source', '')
                if isinstance(source, list):
                    source = "\n".join(source)
                formatted_result += f"{source}\n\n"
                
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

**重要：请务必只输出纯 JSON 字符串，严禁使用 Markdown 代码块（如 ```json），严禁输出任何其他解释性文字。**

JSON 结构必须严格符合以下格式：
{{
  "hexagram": "专业卦名，包含卦序与上下卦象（如：第31卦 咸卦 泽山咸 上兑下艮）",
  "source": ["古籍原文句1（标注出处）", "古籍原文句2（标注出处）"],
  "interpretation": "详细解读（不少于500字）。请分段阐述：整体象意、对本问题的具体指向、潜在变数、当下行动建议。",
  "advice": ["建议1（简练）", "建议2（简练）", "建议3（简练）"],
  "comfort": "针对用户情绪的安抚话语（自然温暖）",
  "question": "结尾的引导性追问（自然温暖）"
}}

❌ 禁止行为
- 不得预测具体结果（如成败、时间）
- 不得使用“必然、注定、灾难”等词
- **再次强调：不要输出 ```json 或 ``` 标记，只输出 {{ ... }}**
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
