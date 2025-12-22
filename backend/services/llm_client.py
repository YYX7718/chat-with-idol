import os
from dotenv import load_dotenv
import openai

# 加载环境变量
load_dotenv()

class LLMClient:
    def __init__(self):
        # 配置API密钥
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "deepseek-chat")
        
        # 配置OpenAI客户端
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_response(self, prompt, model=None, max_tokens=2000, temperature=0.7):
        """
        生成LLM响应
        :param prompt: 提示词
        :param model: 使用的模型
        :param max_tokens: 最大令牌数
        :param temperature: 温度参数
        :return: 生成的响应文本
        """
        model = model or self.default_model
        
        try:
            if model.startswith("deepseek"):
                return self._call_deepseek(prompt, model, max_tokens, temperature)
            else:
                return self._call_openai(prompt, model, max_tokens, temperature)
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
    
    def _call_deepseek(self, prompt, model, max_tokens, temperature):
        """
        调用DeepSeek API
        """
        import requests
        
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        import time
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=90)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt == 2: raise e
                time.sleep(1)
        
        return "占卜由于网络波动未果，请稍后再试。"
    
    def _call_openai(self, prompt, model, max_tokens, temperature):
        """
        调用OpenAI API
        """
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content

# 创建全局LLM客户端实例
llm_client = LLMClient()
