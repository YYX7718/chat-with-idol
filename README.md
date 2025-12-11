# 聊天占卜偶像 (Chat Divination Idol)

一个结合聊天与占卜功能的偶像互动系统，用户可以与虚拟偶像进行对话并获取个性化占卜服务。

## 项目结构

```
chat-divination-idol/
 │ 
 ├── docs/                     # 文档区（README、API说明、prompt设计）
 │   ├── project-overview.md
 │   ├── flow-chart.md
 │   ├── prompts/
 │   │   ├── divination.md
 │   │   ├── transition.md
 │   │   └── idol-system-prompt-template.md
 │   └── api-reference.md
 │ 
 ├── backend/                  # 后端代码（Python）
 │   ├── app.py
 │   ├── services/
 │   │   ├── divination_service.py
 │   │   ├── idol_chat_service.py
 │   │   └── llm_client.py     # DeepSeek/OpenAI 调用
 │   ├── models/
 │   │   └── chat_session.py
 │   └── requirements.txt
 │ 
 ├── frontend/                 # 前端（Vue）
 │   ├── src/
 │   │   ├── pages/
 │   │   │   ├── divination.vue
 │   │   │   ├── choose-idol.vue
 │   │   │   └── idol-chat.vue
 │   │   ├── components/
 │   │   └── api/
 │   └── package.json
 │ 
 ├── tests/                    # 单元测试
 │   ├── test_divination.py
 │   ├── test_llm.py
 │   └── test_idol_chat.py
 │ 
 └── README.md                 # 项目主页介绍
```

## 功能特性

1. **偶像选择**：用户可以选择不同的虚拟偶像进行互动
2. **聊天互动**：与所选偶像进行自然语言对话
3. **占卜服务**：获取个性化的占卜结果
4. **会话管理**：保存聊天和占卜历史

## 技术栈

- **后端**：Python + Flask
- **前端**：Vue 3
- **LLM**：DeepSeek / OpenAI API

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 项目文档

- [项目概述](docs/project-overview.md)
- [流程图](docs/flow-chart.md)
- [API 参考](docs/api-reference.md)
- [Prompt 设计](docs/prompts/)

## 测试

```bash
cd tests
python -m pytest
```

## 许可证

MIT