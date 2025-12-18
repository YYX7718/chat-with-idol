<template>
  <div class="chat-container">
    <header class="chat-header">
      <div class="header-left">
        <div class="title-group">
          <h2 class="title">{{ idolName }}</h2>
          <div class="subtitle">{{ interactionEnabled ? '陪伴聊天' : '占卜进行中' }}</div>
        </div>
      </div>
      <div class="header-actions">
        <button class="ghost-btn" :disabled="busy" @click="showDivination = true">占卜</button>
        <button class="danger-btn" :disabled="busy" @click="goBack">重置</button>
      </div>
    </header>
    
    <main class="chat-main">
      <div class="messages-container" ref="messagesContainer">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message-row"
          :class="message.role"
        >
          <div class="avatar">
            {{ message.role === 'user' ? '我' : (idolName ? idolName[0] : 'AI') }}
          </div>
          <div class="message-bubble-container">
            <div class="message-bubble">
              {{ message.content }}
            </div>
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <footer class="chat-footer">
      <div class="composer">
        <input 
          v-model="inputMessage"
          class="composer-input"
          type="text" 
          :placeholder="interactionEnabled ? '输入消息...' : '请先完成占卜...'"
          :disabled="!interactionEnabled || busy"
          @keyup.enter="sendMessage"
        />
        <button class="primary-btn" :disabled="!interactionEnabled || busy" @click="sendMessage">
          {{ busy ? '发送中...' : '发送' }}
        </button>
      </div>
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
        <button class="close-btn" :disabled="busy" @click="showDivination = false">关闭</button>
      </div>
    </div>
    
    <!-- 占卜问题输入弹窗 -->
    <div v-if="showDivinationQuestion" class="modal">
      <div class="modal-content">
        <h3>{{ currentDivinationTypeName }}</h3>
        <input 
          v-model="divinationQuestion"
          type="text" 
          class="modal-input"
          placeholder="请输入你的问题..."
          :disabled="busy"
          @keyup.enter="confirmDivination"
        />
        <div class="modal-actions">
          <button class="primary-btn" :disabled="busy" @click="confirmDivination">
            {{ busy ? '占卜中...' : '确认' }}
          </button>
          <button class="ghost-btn" :disabled="busy" @click="showDivinationQuestion = false">取消</button>
        </div>
      </div>
    </div>

    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.text }}
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
    const interactionEnabled = ref(false)
    const showDivination = ref(false)
    const showDivinationQuestion = ref(false)
    const currentDivinationType = ref('')
    const currentDivinationTypeName = ref('')
    const divinationQuestion = ref('')
    const messagesContainer = ref(null)
    const busy = ref(false)
    const toast = ref({ show: false, text: '', type: 'info' })

    const showToast = (text, type = 'info') => {
      toast.value = { show: true, text, type }
      setTimeout(() => (toast.value.show = false), 2500)
    }
    
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
    
    const loadSession = async () => {
      const sessionData = localStorage.getItem('currentSession')
      if (sessionData) {
        const { session_id } = JSON.parse(sessionData)
        sessionId.value = session_id
        try {
          const sessionInfo = await api.getSession(sessionId.value)
          idolName.value = sessionInfo.persona_config?.name || '占卜'
          interactionEnabled.value = sessionInfo.current_state !== 'DIVINATION'
          if (sessionInfo.current_state === 'DIVINATION') {
            showDivination.value = true
          }
        } catch (error) {
          localStorage.removeItem('currentSession')
          await loadSession()
        }
      } else {
        try {
          const response = await api.createSession({ user_id: 'anonymous' })
          sessionId.value = response.session_id
          idolName.value = '占卜'
          localStorage.setItem('currentSession', JSON.stringify({
            session_id: response.session_id
          }))
          interactionEnabled.value = false
          showDivination.value = true
        } catch (error) {
          console.error('创建会话失败:', error)
        }
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
      if (!interactionEnabled.value) return
      if (!inputMessage.value.trim()) return
      if (busy.value) return
      
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
        busy.value = true
        // 发送消息到服务器
        const response = await api.sendMessage(sessionId.value, { content: message })
        
        // 添加偶像回复到列表
        messages.value.push(response.message)
        scrollToBottom()
      } catch (error) {
        showToast('发送失败，请稍后重试', 'error')
      }
      busy.value = false
    }
    
    // 开始占卜
    const startDivination = (type, name) => {
      currentDivinationType.value = type
      currentDivinationTypeName.value = name
      showDivination.value = false
      showDivinationQuestion.value = true
    }
    
    // 确认占卜
    const confirmDivination = async () => {
      if (!divinationQuestion.value.trim()) return
      if (busy.value) return
      if (!currentDivinationType.value) {
        showToast('请先选择占卜类型', 'error')
        return
      }
      
      const question = divinationQuestion.value.trim()
      divinationQuestion.value = ''
      showDivinationQuestion.value = false
      
      try {
        busy.value = true
        // 请求占卜
        const response = await api.requestDivination(sessionId.value, {
          type: currentDivinationType.value,
          question: question
        })
        
        interactionEnabled.value = response.state !== 'DIVINATION'
        await fetchMessages()
        showToast('占卜完成', 'success')
      } catch (error) {
        showToast('占卜失败，请稍后重试', 'error')
      }
      busy.value = false
    }
    
    const goBack = () => {
      localStorage.removeItem('currentSession')
      window.location.href = '#/divination'
    }
    
    // 监听消息变化，自动滚动到底部
    watch(messages, () => {
      scrollToBottom()
    })
    
    // 页面加载时初始化
    onMounted(() => {
      loadSession().then(() => {
        if (sessionId.value) {
          fetchMessages()
        }
      })
    })
    
    return {
      sessionId,
      idolName,
      messages,
      inputMessage,
      interactionEnabled,
      showDivination,
      showDivinationQuestion,
      currentDivinationType,
      currentDivinationTypeName,
      divinationQuestion,
      divinationTypes,
      messagesContainer,
      busy,
      toast,
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
  background: radial-gradient(1200px 600px at 10% 10%, rgba(99, 102, 241, 0.20), transparent 60%),
    radial-gradient(900px 500px at 90% 20%, rgba(16, 185, 129, 0.18), transparent 55%),
    radial-gradient(900px 600px at 20% 90%, rgba(236, 72, 153, 0.14), transparent 60%),
    linear-gradient(135deg, #f5f7ff 0%, #f8fafc 55%, #f2f7ff 100%);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.72);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.2px;
  color: #0f172a;
}

.subtitle {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.65);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.primary-btn,
.ghost-btn,
.danger-btn {
  border: 0;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.06s ease, box-shadow 0.12s ease, opacity 0.12s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
  box-shadow: 0 10px 26px rgba(79, 70, 229, 0.26);
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.75);
  color: #0f172a;
  border: 1px solid rgba(15, 23, 42, 0.10);
}

.danger-btn {
  background: rgba(239, 68, 68, 0.10);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.20);
}

.primary-btn:active,
.ghost-btn:active,
.danger-btn:active {
  transform: translateY(1px);
}

.primary-btn:disabled,
.ghost-btn:disabled,
.danger-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  box-shadow: none;
}

.chat-main {
  flex: 1;
  overflow: hidden;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 18px 14px 26px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-row {
  display: flex;
  gap: 10px;
  max-width: 90%;
}

.message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-row.idol {
  align-self: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  color: #64748b;
  flex-shrink: 0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  border: 1px solid rgba(255,255,255,0.5);
}

.message-row.user .avatar {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
}

.message-bubble-container {
  display: flex;
  flex-direction: column;
  max-width: 100%;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  position: relative;
  font-size: 15px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.message-row.user .message-bubble {
  background: #a5b4fc; /* Weaker purple for bubble to differentiate from avatar */
  background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
  color: #ffffff;
}

.message-row.idol .message-bubble {
  background: #ffffff;
  color: #1e293b;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

/* Little triangle arrow for bubbles */
.message-row.idol .message-bubble::before {
  content: "";
  position: absolute;
  left: -6px;
  top: 14px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 6px solid #ffffff;
}

.message-row.user .message-bubble::before {
  content: "";
  position: absolute;
  right: -6px;
  top: 14px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-left: 6px solid #6366f1;
}

.message-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  padding: 0 2px;
}

.message-row.user .message-time {
  text-align: right;
}

.chat-footer {
  display: flex;
  padding: 14px 14px 18px;
  background: rgba(255, 255, 255, 0.72);
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
}

.composer {
  width: 100%;
  display: flex;
  gap: 10px;
  align-items: center;
}

.composer-input {
  flex: 1;
  padding: 12px 14px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 14px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.82);
  outline: none;
  transition: box-shadow 0.12s ease, border-color 0.12s ease;
}

.composer-input:focus {
  border-color: rgba(79, 70, 229, 0.35);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.14);
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(2, 6, 23, 0.48);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(15, 23, 42, 0.10);
  padding: 22px;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 18px 60px rgba(2, 6, 23, 0.22);
  backdrop-filter: blur(12px);
}

.modal-content h3 {
  text-align: center;
  margin-bottom: 16px;
  color: #0f172a;
  font-weight: 800;
}

.divination-types {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.divination-types button {
  padding: 12px 14px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 14px;
  font-weight: 800;
  color: #0f172a;
  transition: transform 0.06s ease, box-shadow 0.12s ease, border-color 0.12s ease;
}

.divination-types button:hover {
  border-color: rgba(79, 70, 229, 0.25);
  box-shadow: 0 10px 26px rgba(2, 6, 23, 0.10);
}

.modal-content input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 14px;
  font-size: 14px;
  margin-bottom: 16px;
  background: rgba(255, 255, 255, 0.82);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.close-btn {
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.10);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.20);
  cursor: pointer;
  font-size: 13px;
  font-weight: 800;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  z-index: 1200;
  color: #0f172a;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(15, 23, 42, 0.10);
  box-shadow: 0 18px 60px rgba(2, 6, 23, 0.22);
  backdrop-filter: blur(10px);
}

.toast.success {
  border-color: rgba(16, 185, 129, 0.30);
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.30);
}
</style>
