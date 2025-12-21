import unittest
from unittest.mock import MagicMock
import sys
import os

# 添加 backend 到 path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.divination_service import DivinationService

# Mock LLM Client
mock_llm = MagicMock()
mock_llm.generate_response.return_value = """
<hexagram>第31卦 咸卦</hexagram>
<source>卦辞：咸，亨，利贞，取女吉。</source>
<interpretation>咸卦象征感应。</interpretation>
<advice>
1. 保持真诚
2. 顺其自然
3. 多沟通
</advice>
<comfort>别担心，一切都会好的。</comfort>
<question>你现在感觉如何？</question>
"""

# 实例化
service = DivinationService()
service.llm_client = mock_llm

try:
    print("Testing generation...")
    result = service.generate_divination({}, "love", "test question")
    print("Result generated successfully:")
    print(result)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
