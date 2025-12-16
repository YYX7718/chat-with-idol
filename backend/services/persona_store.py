class PersonaStore:
    """管理偶像 persona 的简单存储（静态示例）。
    在生产中应从数据库或配置文件加载并允许动态更新。
    """

    def __init__(self):
        self._personas = {
            "idol_001": {
                "id": "idol_001",
                "name": "小梦",
                "default_language": "zh",
                "allow_translation": False,
                "tone": ["gentle", "soothing"],
                "constraints": ["virtual_persona"]
            },
            "idol_004": {
                "id": "idol_004",
                "name": "Lady Gaga",
                "default_language": "en",
                "allow_translation": True,
                "tone": ["expressive", "compassionate"],
                "constraints": ["not the real person", "public_experiences_only"]
            }
        }

    def list_personas(self):
        return list(self._personas.values())

    def get_persona(self, persona_id):
        return self._personas.get(persona_id)


persona_store = PersonaStore()
