# 聊天占卜偶像 (Chat Divination Idol)

一个结合聊天与占卜功能的偶像互动系统，用户可以与虚拟偶像进行对话并获取个性化占卜服务。

> 💡 **开源项目** - 欢迎 Star ⭐ 和贡献代码！

## 🌐 在线演示

<div align="center">

### 🚀 [点击这里体验在线版本 →](https://your-demo-url.com)

[![在线演示](https://img.shields.io/badge/🌐-在线演示-blue?style=for-the-badge)](https://your-demo-url.com)

> 💻 **演示地址**：https://your-demo-url.com  
> ⚠️ **提示**：请将链接替换为你的实际部署地址

</div>

## ✨ 特性

- 🎭 **多偶像选择** - 选择你喜欢的虚拟偶像进行互动
- 💬 **自然对话** - 基于 LLM 的智能对话系统
- 🔮 **个性化占卜** - 提供爱情、事业、运势等多种占卜服务
- 💾 **会话管理** - 自动保存聊天和占卜历史
- 🔒 **安全可靠** - API Key 安全存储，不会泄露

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

## 🚀 快速开始

### 方式一：使用启动脚本（Windows，最简单）

1. **配置 API 密钥**
   - 打开 `backend/.env` 文件（如果不存在，请创建）
   - 将 `your_deepseek_api_key_here` 替换为你的实际 API Key
   
2. **启动项目**
   - 双击 `启动后端.bat`
   - 双击 `启动前端.bat`（新窗口）
   
3. **访问应用**
   - 浏览器打开：http://localhost:3000

### 方式二：手动启动

#### 1. 配置 API 密钥

在 `backend` 目录下创建 `.env` 文件：

```env
# DeepSeek API Key（推荐）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 或者使用 OpenAI API Key
# OPENAI_API_KEY=your_openai_api_key_here

# 默认模型（可选）
DEFAULT_MODEL=deepseek-chat
```

**获取 API Key：**
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/

#### 2. 安装依赖并启动

**后端：**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**前端（新终端）：**
```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:3000

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端将在 **http://localhost:5000** 启动

### 前端启动

打开**新的终端窗口**（保持后端运行），执行：

```bash
cd frontend
npm install
npm run dev
```

前端将在 **http://localhost:3000** 启动

### 访问应用

在浏览器中打开：**http://localhost:3000**

## 📖 文档

- 🚀 **[快速部署指南](部署步骤.md)** - 5分钟快速部署到生产环境 ⭐
- 📘 [环境配置指南](SETUP.md) - 详细的配置步骤（推荐新用户阅读）
- 🚀 [运行指南](docs/运行指南.md) - 本地启动和运行说明
- 🌐 [部署指南](docs/部署指南.md) - 详细的部署选项和说明
- 📋 [项目概述](docs/project-overview.md) - 项目架构和设计
- 🔄 [流程图](docs/flow-chart.md) - 业务流程
- 📡 [API 参考](docs/api-reference.md) - API 接口文档
- 💬 [Prompt 设计](docs/prompts/) - Prompt 模板

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)

### 贡献方式

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码

## ⚠️ 重要提示

### 安全注意事项

- ✅ **`.env` 文件已自动忽略** - 不会提交到代码仓库
- ✅ **API Key 安全** - 只存储在后端，不会暴露给前端
- ✅ **可以安全开源** - 代码可以公开，不会泄露敏感信息

### 首次使用

1. 克隆项目后，**必须**创建 `backend/.env` 文件
2. 在 `.env` 文件中配置你的 API Key
3. 参考 [SETUP.md](SETUP.md) 进行详细配置

## 🧪 测试

```bash
cd tests
python -m pytest
```

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者的支持！

## ⭐ 如果这个项目对你有帮助，请给个 Star！

---

**注意：** 使用本项目需要配置 API Key（DeepSeek 或 OpenAI），请确保妥善保管你的 API Key，不要泄露给他人。