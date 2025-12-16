import uuid
from typing import Dict

class PromptManager:
    """管理并版本化 system prompt 的简单实现（内存）"""

    def __init__(self):
        # { prompt_id: {stage: str, content: str, created_at: float} }
        self._prompts: Dict[str, dict] = {}

    def register_prompt(self, stage: str, content: str) -> str:
        pid = str(uuid.uuid4())
        self._prompts[pid] = {
            'stage': stage,
            'content': content,
            'created_at': __import__('time').time()
        }
        return pid

    def get_prompt(self, prompt_id: str) -> dict:
        return self._prompts.get(prompt_id)

    def find_prompts_for_stage(self, stage: str):
        return {pid: p for pid, p in self._prompts.items() if p['stage'] == stage}


# 全局实例
prompt_manager = PromptManager()
