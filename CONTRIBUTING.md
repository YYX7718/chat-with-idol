# 贡献指南

欢迎贡献代码！在开始之前，请先阅读本指南。

## 🚀 快速开始

### 1. Fork 和克隆项目

```bash
git clone https://github.com/your-username/chat-with-idol.git
cd chat-with-idol
```

### 2. 配置环境变量

#### 后端配置

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

#### 前端配置（可选）

前端通常不需要额外配置，开发环境会自动使用 Vite 代理。

如果需要配置生产环境，在 `frontend` 目录创建 `.env.production`：

```env
VITE_API_BASE_URL=https://your-api-domain.com/api
```

### 3. 安装依赖

**后端：**
```bash
cd backend
pip install -r requirements.txt
```

**前端：**
```bash
cd frontend
npm install
```

### 4. 启动项目

**启动后端：**
```bash
cd backend
python app.py
```

**启动前端（新终端）：**
```bash
cd frontend
npm run dev
```

访问：http://localhost:3000

## 📝 开发规范

### 代码风格

- Python: 遵循 PEP 8
- JavaScript: 使用 ESLint 配置
- 提交前运行测试

### 提交信息

使用清晰的提交信息：
```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建/工具变更
```

## 🧪 运行测试

```bash
cd tests
python -m pytest
```

## 🔒 安全注意事项

- **永远不要**提交 `.env` 文件
- **永远不要**在代码中硬编码 API Key
- **永远不要**提交包含敏感信息的文件

## 📚 相关文档

- [项目概述](docs/project-overview.md)
- [API 参考](docs/api-reference.md)
- [运行指南](docs/运行指南.md)

## ❓ 需要帮助？

- 提交 Issue
- 查看文档
- 联系维护者

感谢你的贡献！🎉

