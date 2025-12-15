# 环境配置指南

本指南帮助新用户快速配置和运行项目。

## 📋 前置要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn
- DeepSeek 或 OpenAI API Key

## 🔧 配置步骤

### 步骤 1: 克隆项目

```bash
git clone https://github.com/your-username/chat-with-idol.git
cd chat-with-idol
```

### 步骤 2: 配置后端环境变量

在 `backend` 目录下创建 `.env` 文件：

**Windows (PowerShell):**
```powershell
cd backend
@"
DEEPSEEK_API_KEY=your_api_key_here
DEFAULT_MODEL=deepseek-chat
"@ | Out-File -FilePath .env -Encoding utf8
```

**Linux/Mac:**
```bash
cd backend
cat > .env << EOF
DEEPSEEK_API_KEY=your_api_key_here
DEFAULT_MODEL=deepseek-chat
EOF
```

**或者手动创建：**

创建 `backend/.env` 文件，内容如下：

```env
# DeepSeek API Key（推荐）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 或者使用 OpenAI API Key
# OPENAI_API_KEY=your_openai_api_key_here

# 默认使用的模型（可选，默认为 deepseek-chat）
DEFAULT_MODEL=deepseek-chat
```

**⚠️ 重要：** 将 `your_deepseek_api_key_here` 替换为你的实际 API Key

### 步骤 3: 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

**推荐使用虚拟环境：**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 4: 安装前端依赖

```bash
cd frontend
npm install
```

### 步骤 5: 启动项目

**终端 1 - 启动后端：**
```bash
cd backend
python app.py
```

应该看到：
```
 * Running on http://127.0.0.1:5000
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

应该看到：
```
  ➜  Local:   http://localhost:3000/
```

### 步骤 6: 访问应用

在浏览器打开：**http://localhost:3000**

## 🎯 使用启动脚本（Windows）

如果你在 Windows 上，可以使用提供的批处理文件：

1. 双击 `启动后端.bat`
2. 双击 `启动前端.bat`（新窗口）

## 🔑 获取 API Key

### DeepSeek（推荐）

1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 在控制台创建 API Key
4. 复制 API Key 到 `.env` 文件

### OpenAI

1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 在 API Keys 页面创建新 Key
4. 复制 API Key 到 `.env` 文件

## ✅ 验证配置

### 检查后端

访问：http://localhost:5000/api/idols

如果看到 JSON 格式的偶像列表，说明后端配置成功。

### 检查前端

访问：http://localhost:3000

应该能看到偶像选择界面。

## 🐛 常见问题

### 问题 1: ModuleNotFoundError

**解决：** 确保已安装所有依赖
```bash
cd backend
pip install -r requirements.txt
```

### 问题 2: API 调用失败

**解决：**
- 检查 `.env` 文件是否在 `backend` 目录下
- 确认 API Key 是否正确
- 确认 API Key 是否有余额

### 问题 3: 端口被占用

**解决：**
- 修改 `backend/app.py` 中的端口号
- 或修改 `frontend/vite.config.js` 中的端口号

## 📚 更多帮助

- [运行指南](docs/运行指南.md)
- [安全配置](docs/安全配置指南.md)
- [项目概述](docs/project-overview.md)

