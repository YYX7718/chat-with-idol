# API 参考文档

## 1. 基础信息

### 1.1 服务地址

```
http://localhost:5000/api
```

### 1.2 请求格式

所有请求和响应均使用 JSON 格式。

### 1.3 错误处理

| 错误码 | 描述 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

错误响应格式：

```json
{
  "error": "错误描述",
  "code": 错误码
}
```

## 2. 会话管理 API

### 2.1 创建会话

**请求**：
- 方法：POST
- 路径：/sessions
- 参数：
  - idol_id: 字符串，偶像ID
  - user_id: 字符串，用户ID（可选）

**响应**：

```json
{
  "session_id": "会话ID",
  "idol_id": "偶像ID",
  "created_at": "创建时间",
  "messages": []
}
```

### 2.2 获取会话

**请求**：
- 方法：GET
- 路径：/sessions/{session_id}

**响应**：

```json
{
  "session_id": "会话ID",
  "idol_id": "偶像ID",
  "created_at": "创建时间",
  "updated_at": "更新时间",
  "messages": [
    {
      "id": "消息ID",
      "role": "user|idol",
      "content": "消息内容",
      "timestamp": "时间戳"
    },
    ...
  ]
}
```

### 2.3 删除会话

**请求**：
- 方法：DELETE
- 路径：/sessions/{session_id}

**响应**：

```json
{
  "message": "会话已删除"
}
```

## 3. 聊天 API

### 3.1 发送消息

**请求**：
- 方法：POST
- 路径：/chat/{session_id}
- 参数：
  - content: 字符串，消息内容

**响应**：

```json
{
  "session_id": "会话ID",
  "message": {
    "id": "消息ID",
    "role": "idol",
    "content": "偶像回复内容",
    "timestamp": "时间戳"
  }
}
```

### 3.2 获取消息历史

**请求**：
- 方法：GET
- 路径：/chat/{session_id}/messages
- 参数：
  - limit: 整数，限制返回消息数量（可选）
  - offset: 整数，偏移量（可选）

**响应**：

```json
{
  "session_id": "会话ID",
  "messages": [
    {
      "id": "消息ID",
      "role": "user|idol",
      "content": "消息内容",
      "timestamp": "时间戳"
    },
    ...
  ]
}
```

## 4. 占卜 API

### 4.1 请求占卜

**请求**：
- 方法：POST
- 路径：/divination/{session_id}
- 参数：
  - type: 字符串，占卜类型（love|career|fortune|study）
  - question: 字符串，具体问题（可选）

**响应**：

```json
{
  "session_id": "会话ID",
  "divination": {
    "id": "占卜ID",
    "type": "占卜类型",
    "question": "用户问题",
    "result": "占卜结果",
    "timestamp": "时间戳"
  }
}
```

### 4.2 获取占卜历史

**请求**：
- 方法：GET
- 路径：/divination/{session_id}/history
- 参数：
  - limit: 整数，限制返回数量（可选）
  - offset: 整数，偏移量（可选）

**响应**：

```json
{
  "session_id": "会话ID",
  "divinations": [
    {
      "id": "占卜ID",
      "type": "占卜类型",
      "question": "用户问题",
      "result": "占卜结果",
      "timestamp": "时间戳"
    },
    ...
  ]
}
```

## 5. 偶像 API

### 5.1 获取偶像列表

**请求**：
- 方法：GET
- 路径：/idols

**响应**：

```json
{
  "idols": [
    {
      "id": "偶像ID",
      "name": "偶像名称",
      "description": "偶像描述",
      "avatar": "头像URL",
      "personality": "性格特点"
    },
    ...
  ]
}
```

### 5.2 获取偶像详情

**请求**：
- 方法：GET
- 路径：/idols/{idol_id}

**响应**：

```json
{
  "id": "偶像ID",
  "name": "偶像名称",
  "description": "偶像详细描述",
  "avatar": "头像URL",
  "personality": "性格特点",
  "background": "背景故事",
  "abilities": ["能力1", "能力2", ...]
}
```

## 6. 示例请求

### 6.1 创建会话

```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"idol_id": "idol_001", "user_id": "user_001"}'
```

### 6.2 发送消息

```bash
curl -X POST http://localhost:5000/api/chat/session_001 \
  -H "Content-Type: application/json" \
  -d '{"content": "你好，我想和你聊聊天"}'
```

### 6.3 请求占卜

```bash
curl -X POST http://localhost:5000/api/divination/session_001 \
  -H "Content-Type: application/json" \
  -d '{"type": "love", "question": "我最近和暗恋的人关系有些疏远，不知道该怎么办"}'
```

## 7. 安全说明

- 所有API请求都应使用HTTPS协议（生产环境）
- 建议实现API密钥认证机制
- 定期更新API密钥
- 限制API请求频率，防止滥用