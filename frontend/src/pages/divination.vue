<template>
  <div class="divination-container">
    <header class="divination-header">
      <div class="header-left">
        <h2 class="title">{{ idolName || '占卜' }}</h2>
        <div class="subtitle">先占卜，再选择公众人物生成虚拟偶像陪伴聊天</div>
      </div>
      <div class="header-actions">
        <button class="ghost-btn" :disabled="busy" @click="goChat">进入聊天</button>
      </div>
    </header>
    
    <main class="divination-main">
      <div class="content">
        <section class="card">
          <div class="card-title">开始占卜</div>
          <div class="kaiti-notice">
            <div class="kaiti-notice-title">起卦提示</div>
            <div class="kaiti-notice-lines">
              <div>1. 子时不可占卜</div>
              <div>2. 每日占卜最好不超过三卦</div>
              <div>3. 无事不起卦</div>
            </div>
          </div>
          <div class="type-row">
            <button
              v-for="type in divinationTypes"
              :key="type.value"
              class="type-chip"
              :class="{ active: selectedType === type.value }"
              :disabled="busy"
              @click="selectedType = type.value"
            >
              {{ type.name }}
            </button>
          </div>
          <textarea
            v-model="newQuestion"
            class="question-input"
            :disabled="busy"
            rows="3"
            placeholder="输入你想占卜的问题…"
            @keyup.enter.exact.prevent="submitDivination"
          />
          <div class="actions">
            <button class="primary-btn" :disabled="busy || !newQuestion.trim()" @click="submitDivination">
              {{ busy ? '占卜中…' : '开始占卜' }}
            </button>
          </div>
        </section>

        <section class="card history">
          <div class="card-title">占卜记录</div>
          <div v-if="divinations.length === 0" class="empty-state">
            暂无占卜记录
          </div>
          <div
            v-for="divination in divinations"
            :key="divination.id"
            class="divination-item"
          >
            <div class="divination-header-info">
              <span class="divination-type">{{ getDivinationTypeName(divination.type) }}</span>
              <span class="divination-time">{{ formatTime(divination.timestamp) }}</span>
            </div>
            <div class="divination-question">{{ divination.question }}</div>
            <div class="divination-result">{{ divination.result }}</div>
          </div>
        </section>
      </div>
    </main>

    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.text }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api'

export default {
  name: 'Divination',
  setup() {
    const sessionId = ref('')
    const idolName = ref('')
    const divinations = ref([])
    const newQuestion = ref('')
    const selectedType = ref('love')
    const busy = ref(false)
    const toast = ref({ show: false, text: '', type: 'info' })

    const divinationTypes = [
      { value: 'love', name: '爱情' },
      { value: 'career', name: '事业' },
      { value: 'fortune', name: '运势' },
      { value: 'study', name: '学业' }
    ]

    const showToast = (text, type = 'info') => {
      toast.value = { show: true, text, type }
      setTimeout(() => (toast.value.show = false), 2500)
    }
    
    // 占卜类型映射
    const divinationTypeMap = {
      'love': '爱情',
      'career': '事业',
      'fortune': '运势',
      'study': '学业'
    }
    
    // 获取占卜类型中文名称
    const getDivinationTypeName = (type) => {
      return divinationTypeMap[type] || type
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleString()
    }
    
    const loadSession = async () => {
      const sessionData = localStorage.getItem('currentSession')
      if (sessionData) {
        const { session_id } = JSON.parse(sessionData)
        sessionId.value = session_id
        try {
          const sessionInfo = await api.getSession(sessionId.value)
          idolName.value = sessionInfo.persona_config?.name || '占卜'
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
        } catch (error) {
          showToast('创建会话失败，请刷新重试', 'error')
        }
      }
    }
    
    // 获取占卜历史
    const fetchDivinations = async () => {
      try {
        const response = await api.getDivinationHistory(sessionId.value)
        divinations.value = response.divinations
      } catch (error) {
        showToast('获取占卜记录失败，请稍后重试', 'error')
      }
    }

    const submitDivination = async () => {
      if (busy.value) return
      if (!newQuestion.value.trim()) return
      const question = newQuestion.value.trim()
      newQuestion.value = ''
      try {
        busy.value = true
        await api.requestDivination(sessionId.value, {
          type: selectedType.value,
          question
        })
        await fetchDivinations()
        showToast('占卜完成，进入聊天…', 'success')
        setTimeout(() => {
          window.location.href = '#/chat'
        }, 350)
      } catch (error) {
        showToast('占卜请求失败，请稍后重试', 'error')
      }
      busy.value = false
    }
    
    // 返回聊天页面
    const goChat = () => {
      window.location.href = '#/chat'
    }
    
    // 页面加载时初始化
    onMounted(() => {
      loadSession().then(() => {
        if (sessionId.value) {
          fetchDivinations()
        }
      })
    })
    
    return {
      sessionId,
      idolName,
      divinations,
      newQuestion,
      formatTime,
      getDivinationTypeName,
      divinationTypes,
      selectedType,
      busy,
      toast,
      goChat,
      submitDivination
    }
  }
}
</script>

<style scoped>
.divination-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: #ebe7df;
}

.divination-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url('/divination-wallpaper.jpg') no-repeat center center;
  background-size: cover;
  filter: saturate(0.95) contrast(1.02);
  transform: scale(1.02);
  z-index: 0;
}

.divination-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.78) 0%, rgba(248, 250, 252, 0.62) 45%, rgba(248, 250, 252, 0.78) 100%);
  z-index: 0;
}

.divination-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.72);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
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

.divination-main {
  flex: 1;
  overflow: hidden;
  padding: 18px 14px 24px;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.content {
  width: 100%;
  max-width: 980px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.content > .card {
  position: relative;
}

.kaiti-notice {
  border-radius: 14px;
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 10px 30px rgba(2, 6, 23, 0.06);
  margin-bottom: 12px;
  font-family: KaiTi, STKaiti, "Kaiti SC", DFKai-SB, serif;
  color: rgba(15, 23, 42, 0.9);
}

.kaiti-notice-title {
  font-size: 15px;
  font-weight: 900;
  margin-bottom: 6px;
  letter-spacing: 0.6px;
  color: rgba(30, 41, 59, 0.9);
}

.kaiti-notice-lines {
  display: grid;
  gap: 4px;
  font-size: 14px;
  line-height: 1.45;
}

.card {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 16px;
  box-shadow: 0 18px 60px rgba(2, 6, 23, 0.08);
  padding: 16px;
  backdrop-filter: blur(12px);
}

.card-title {
  font-weight: 900;
  color: #0f172a;
  font-size: 14px;
  margin-bottom: 12px;
}

.type-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.type-chip {
  border: 1px solid rgba(15, 23, 42, 0.10);
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 800;
  color: rgba(15, 23, 42, 0.85);
  background: rgba(255, 255, 255, 0.72);
  cursor: pointer;
  transition: transform 0.06s ease, box-shadow 0.12s ease, border-color 0.12s ease;
}

.type-chip.active {
  border-color: rgba(79, 70, 229, 0.35);
  box-shadow: 0 12px 34px rgba(79, 70, 229, 0.16);
  color: #0f172a;
}

.type-chip:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  box-shadow: none;
}

.question-input {
  width: 100%;
  resize: none;
  padding: 12px 14px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 14px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.82);
  outline: none;
  transition: box-shadow 0.12s ease, border-color 0.12s ease;
}

.question-input:focus {
  border-color: rgba(79, 70, 229, 0.35);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.14);
}

.actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.primary-btn,
.ghost-btn {
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

.primary-btn:active,
.ghost-btn:active {
  transform: translateY(1px);
}

.primary-btn:disabled,
.ghost-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  box-shadow: none;
}

.empty-state {
  text-align: center;
  padding: 34px 10px;
  color: rgba(15, 23, 42, 0.55);
  font-size: 13px;
}

.divination-item {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.78);
}

.divination-header-info {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.divination-type {
  background: rgba(79, 70, 229, 0.10);
  color: #3730a3;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.divination-time {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.55);
}

.divination-question {
  margin-top: 8px;
  color: rgba(15, 23, 42, 0.90);
  font-weight: 700;
  white-space: pre-wrap;
  word-break: break-word;
}

.divination-result {
  line-height: 1.5;
  margin-top: 10px;
  color: rgba(15, 23, 42, 0.86);
  white-space: pre-wrap;
  word-break: break-word;
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

@media (min-width: 980px) {
  .content {
    grid-template-columns: 1.1fr 0.9fr;
    gap: 16px;
  }

  .history {
    align-self: start;
  }
}

</style>
