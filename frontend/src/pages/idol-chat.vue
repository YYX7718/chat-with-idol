<template>
  <div class="chat-container">
    <header class="chat-header">
      <h2>{{ idolName }}</h2>
      <div class="header-actions">
        <button class="divination-btn" @click="showDivination = true">占卜</button>
        <button class="back-btn" @click="goBack">返回</button>
      </div>
    </header>
    
    <main class="chat-main">
      <div class="messages-container" ref="messagesContainer">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message"
          :class="message.role"
        >
          <div class="message-content">
            {{ message.content }}
          </div>
          <div class="message-time">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
      </div>
    </main>
    
    <footer class="chat-footer">
      <input 
        v-model="inputMessage"
        type="text" 
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
      />
      <button @click="sendMessage">发送</button>
    </footer>
    
    <!-- 占卜弹窗 -->
    <div v-if="showDivination" class="modal">
      <div class="modal-content">
        <h3>选择占卜类型</h3>
        <div class="divination-types">
          <button 
            v-for="type in divinationTypes" 
            :key="type.value"
            @click="startDivination(type.value, type.name)"
          >
            {{ type.name }}
          </button>
        </div>
        <button class="close-btn" @click="showDivination = false">关闭</button>
      </div>
    </div>
    
    <!-- 占卜问题输入弹窗 -->
    <div v-if="showDivinationQuestion" class="modal">
      <div class="modal-content">
        <h3>{{ currentDivinationType }}占卜</h3>
        <input 
          v-model="divinationQuestion"
          type="text" 
          placeholder="请输入您的问题..."
          @keyup.enter="confirmDivination"
        />
        <div class="modal-actions">
          <button @click="confirmDivination">确认</button>
          <button @click="showDivinationQuestion = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import api from '../api'

export default {
  name: 'IdolChat',
  setup() {
    const sessionId = ref('')
    const idolName = ref('')
    const messages = ref([])
    const inputMessage = ref('')
    const showDivination = ref(false)
    const showDivinationQuestion = ref(false)
    const currentDivinationType = ref('')
    const divinationQuestion = ref('')
    const messagesContainer = ref(null)
    
    // 占卜类型
    const divinationTypes = [
      { value: 'love', name: '爱情占卜' },
      { value: 'career', name: '事业占卜' },
      { value: 'fortune', name: '运势占卜' },
      { value: 'study', name: '学业占卜' }
    ]
    
    // 格式化时间
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }
    
    // 加载会话信息
    const loadSession = () => {
      const sessionData = localStorage.getItem('currentSession')
      if (sessionData) {
        const { session_id, idol_name } = JSON.parse(sessionData)
        sessionId.value = session_id
        idolName.value = idol_name
      } else {
        // 没有会话信息，返回选择偶像页面
        goBack()
      }
    }
    
    // 获取消息历史
    const fetchMessages = async () => {
      try {
        const response = await api.getMessages(sessionId.value)
        messages.value = response.messages
        scrollToBottom()
      } catch (error) {
        console.error('获取消息历史失败:', error)
      }
    }
    
    // 发送消息
    const sendMessage = async () => {
      if (!inputMessage.value.trim()) return
      
      const message = inputMessage.value.trim()
      inputMessage.value = ''
      
      // 添加用户消息到列表
      const userMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }
      messages.value.push(userMessage)
      scrollToBottom()
      
      try {
        // 发送消息到服务器
        const response = await api.sendMessage(sessionId.value, { content: message })
        
        // 添加偶像回复到列表
        messages.value.push(response.message)
        scrollToBottom()
      } catch (error) {
        console.error('发送消息失败:', error)
        // 可以在这里添加错误提示
      }
    }
    
    // 开始占卜
    const startDivination = (type, name) => {
      currentDivinationType = name
      showDivination = false
      showDivinationQuestion = true
    }
    
    // 确认占卜
    const confirmDivination = async () => {
      if (!divinationQuestion.value.trim()) return
      
      const question = divinationQuestion.value.trim()
      divinationQuestion.value = ''
      showDivinationQuestion = false
      
      try {
        // 请求占卜
        const response = await api.requestDivination(sessionId.value, {
          type: currentDivinationType.toLowerCase(),
          question: question
        })
        
        // 添加占卜结果到消息列表
        messages.value.push({
          id: Date.now().toString(),
          role: 'idol',
          content: response.divination.result,
          timestamp: new Date().toISOString()
        })
        scrollToBottom()
      } catch (error) {
        console.error('占卜失败:', error)
        // 可以在这里添加错误提示
      }
    }
    
    // 返回选择偶像页面
    const goBack = () => {
      localStorage.removeItem('currentSession')
      window.location.href = '#/choose-idol'
    }
    
    // 监听消息变化，自动滚动到底部
    watch(messages, () => {
      scrollToBottom()
    })
    
    // 页面加载时初始化
    onMounted(() => {
      loadSession()
      if (sessionId.value) {
        fetchMessages()
      }
    })
    
    return {
      sessionId,
      idolName,
      messages,
      inputMessage,
      showDivination,
      showDivinationQuestion,
      currentDivinationType,
      divinationQuestion,
      divinationTypes,
      messagesContainer,
      formatTime,
      sendMessage,
      startDivination,
      confirmDivination,
      goBack
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.divination-btn, .back-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.divination-btn {
  background-color: #ffeb3b;
  color: #333;
}

.back-btn {
  background-color: #f44336;
  color: white;
}

.chat-main {
  flex: 1;
  overflow: hidden;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  max-width: 70%;
  padding: 12px 15px;
  border-radius: 15px;
  position: relative;
}

.message.user {
  align-self: flex-end;
  background-color: #4CAF50;
  color: white;
  border-bottom-right-radius: 5px;
}

.message.idol {
  align-self: flex-start;
  background-color: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 5px;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  text-align: right;
  margin-top: 5px;
}

.chat-footer {
  display: flex;
  padding: 15px 20px;
  background-color: white;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
  gap: 10px;
}

.chat-footer input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 25px;
  font-size: 1rem;
}

.chat-footer button {
  padding: 12px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
}

.modal-content h3 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.divination-types {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.divination-types button {
  padding: 15px;
  border: none;
  border-radius: 5px;
  background-color: #f0f0f0;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.divination-types button:hover {
  background-color: #e0e0e0;
}

.modal-content input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.modal-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.modal-actions button:first-child {
  background-color: #4CAF50;
  color: white;
}

.modal-actions button:last-child {
  background-color: #f44336;
  color: white;
}

.close-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 5px;
  background-color: #f44336;
  color: white;
  cursor: pointer;
  font-size: 1rem;
}
</style>