项目规格说明（Spec）

目标

- 实现一个状态驱动、多阶段对话系统，阶段为 DIVINATION → TRANSITION → IDOL_CHAT。
- 以沉浸式占卜与情绪陪伴为核心，输出必须结构化且可验证。

核心原则

- 梅花易数解读需有古籍依据（《梅花易数》《周易》）。
- 不做确定性预测、不恐吓用户。
- 偶像聊天为虚拟人设，不是真人。
- 偶像默认使用母语输出，翻译为附加功能。
- 以沉浸体验和情绪安抚为核心。

阶段与输出契约

STAGE 1: DIVINATION
- 输入：中文用户问题
- 输出（结构化 JSON）：
  {
    "hexagram": "<卦名>",
    "classical_quote": "<至少一句古籍原文>",
    "interpretation": "<现代语言的象征性解读，非确定性>",
    "reassurance": "<情绪安抚文本>",
    "transition_question": "<是否需要更多建议或陪伴的询问>"
  }
- 语气：平和、安抚
- 约束：不得使用绝对化、恐吓性词汇

STAGE 2: TRANSITION
- 输入：用户是否需要更多建议的回应
- 输出（结构化 JSON）：
  {
    "message":"<温和邀请>",
    "virtual_notice":"<明确这是虚拟 AI 人设>",
    "persona_options":["<persona_id_1>", "<persona_id_2>"]
  }

STAGE 3: IDOL_CHAT
- 输入：选择的 persona id 与后续用户消息
- Persona 配置样例：
  {
    "name":"Lady Gaga",
    "default_language":"en",
    "allow_translation":true,
    "tone":["expressive","compassionate"],
    "culture":"American pop artist",
    "constraints":["not the real person","no private life fabrication"]
  }
- 输出（结构化 JSON）：
  {
    "persona_id":"<id>",
    "original_message":"<原文（偶像母语）>",
    "translation":"<可选翻译>",
    "reminder":"<提示这是虚拟角色>"
  }
- 规则：默认使用 persona 母语，若允许翻译则提供翻译字段（用户可控）。

全局要求

- 状态机必须强制单向迁移：DIVINATION → TRANSITION → IDOL_CHAT。
- 每次响应须记录 prompt_id、persona_id（若使用）、timestamp 与返回的结构化 JSON。
- 所有内容须包含免责声明：“仅供娱乐与情绪支持”。
- 实现安全过滤以阻止确定性或恐吓性语言。
- 编写单元测试：状态迁移、阶段输出字段、过滤器行为。

可直接给 AI 的 Spec Prompt（用于生成代码）

```
You are implementing a state-driven chat system with three stages:
DIVINATION, TRANSITION, and IDOL_CHAT.

This is not a single chatbot but a multi-phase conversational flow.

STAGE 1: DIVINATION
- Input: Chinese user question
- Output (structured JSON):
  {
    "hexagram": "<name>",
    "classical_quote": "<at least one sentence from Meihua Yishu or I Ching>",
    "interpretation": "<modern, non-deterministic symbolic interpretation>",
    "reassurance": "<emotional support text>",
    "transition_question": "<explicit ask whether user wants further guidance or company>"
  }
- Tone: calm, reassuring
- Constraints: no absolute predictions, no deterministic language, avoid words like '必然','注定','灾难'

STAGE 2: TRANSITION
- Input: user's response to whether they want more guidance
- Output (structured JSON):
  {
    "message": "<gentle invite to continue>",
    "virtual_notice": "<explicit statement: this is a virtual AI persona, not a real person>",
    "persona_options": ["<persona_id_1>", "<persona_id_2>"]
  }

STAGE 3: IDOL_CHAT
- Input: selected persona id and subsequent user messages
- Persona config example:
  {
    "name":"Lady Gaga",
    "default_language":"en",
    "allow_translation":true,
    "tone":["expressive","compassionate","artistic"],
    "culture":"American pop artist",
    "constraints":["not the real person","no private life fabrication","only public experiences"]
  }
- Output (structured JSON):
  {
    "persona_id":"<id>",
    "original_message":"<message in persona's language>",
    "translation":"<optional translation if requested>",
    "reminder":"<periodic reminder this is a virtual character>"
  }
- Rules:
  - Persona must use the default_language for original_message.
  - If allow_translation=true, include translation as a separate field only when user requests.
  - Avoid impersonation; reference only public, verifiable experiences.
  - Do not perform medical/psychological/diagnostic tasks.
  - Periodically (configurable frequency) remind user the persona is virtual.

GLOBAL REQUIREMENTS
- State machine must enforce single-phase behavior: DIVINATION → TRANSITION → IDOL_CHAT.
- Every response must record: prompt_id, persona_id (if used), timestamp, and the structured JSON returned.
- All content must include a short disclaimer: "For entertainment and emotional support only." 
- Implement a safety filter to block deterministic or fear-inducing language.
- Provide unit tests for: state transitions, required output fields per stage, safety filter behavior.
```
