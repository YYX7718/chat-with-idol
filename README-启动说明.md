# 🚀 快速启动指南

## 方式一：使用启动脚本（推荐，最简单）

### 步骤 1：配置 API 密钥

1. 打开 `backend/.env` 文件
2. 将 `your_deepseek_api_key_here` 替换为你的实际 API Key

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx  # 替换这里
```

**获取 API Key：**
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/

### 步骤 2：启动后端

双击运行 `启动后端.bat`

等待看到：
```
 * Running on http://127.0.0.1:5000
```

### 步骤 3：启动前端

双击运行 `启动前端.bat`（**新窗口**，不要关闭后端窗口）

等待看到：
```
  ➜  Local:   http://localhost:3000/
```

### 步骤 4：访问应用

在浏览器打开：**http://localhost:3000**

---

## 方式二：手动启动

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 启动前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

---

## ⚠️ 重要提示

1. **必须先配置 API 密钥**：编辑 `backend/.env` 文件
2. **后端和前端需要同时运行**：需要打开两个终端/窗口
3. **不要关闭运行窗口**：关闭窗口会停止服务

## 🐛 遇到问题？

查看详细文档：[docs/运行指南.md](docs/运行指南.md)

