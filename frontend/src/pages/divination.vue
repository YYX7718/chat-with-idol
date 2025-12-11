<template>
  <div class="divination-container">
    <header class="divination-header">
      <h2>{{ idolName }}</h2>
      <button class="back-btn" @click="goBack">返回聊天</button>
    </header>
    
    <main class="divination-main">
      <div class="divination-history">
        <h3>占卜历史</h3>
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
          <div class="divination-question">
            <strong>问题:</strong> {{ divination.question }}
          </div>
          <div class="divination-result">
            <strong>结果:</strong> {{ divination.result }}
          </div>
        </div>
      </div>
    </main>
    
    <footer class="divination-footer">
      <button class="new-divination-btn" @click="goNewDivination">新占卜</button>
    </footer>
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
    
    // 加载会话信息
    const loadSession = () => {
      const sessionData = localStorage.getItem('currentSession')
      if (sessionData) {
        const { session_id, idol_name } = JSON.parse(sessionData)
        sessionId.value = session_id
        idolName.value = idol_name
      } else {
        // 没有会话信息，返回选择偶像页面
        goBackToChooseIdol()
      }
    }
    
    // 获取占卜历史
    const fetchDivinations = async () => {
      try {
        const response = await api.getDivinations(sessionId.value)
        divinations.value = response.divinations
      } catch (error) {
        console.error('获取占卜历史失败:', error)
      }
    }
    
    // 返回聊天页面
    const goBack = () => {
      window.location.href = '#/idol-chat'
    }
    
    // 返回选择偶像页面
    const goBackToChooseIdol = () => {
      localStorage.removeItem('currentSession')
      window.location.href = '#/choose-idol'
    }
    
    // 新占卜
    const goNewDivination = () => {
      window.location.href = '#/idol-chat'
    }
    
    // 页面加载时初始化
    onMounted(() => {
      loadSession()
      if (sessionId.value) {
        fetchDivinations()
      }
    })
    
    return {
      sessionId,
      idolName,
      divinations,
      formatTime,
      getDivinationTypeName,
      goBack,
      goNewDivination
    }
  }
}
</script>

<style scoped>
.divination-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.divination-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.back-btn {
  padding: 8px 15px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.divination-main {
  flex: 1;
  overflow: hidden;
  padding: 20px;
}

.divination-history {
  background-color: white;
  border-radius: 10px;
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.divination-history h3 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.empty-state {
  text-align: center;
  padding: 50px;
  color: #999;
  font-size: 1.1rem;
}

.divination-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
}

.divination-header-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.divination-type {
  background-color: #4CAF50;
  color: white;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: bold;
}

.divination-time {
  font-size: 0.8rem;
  color: #666;
}

.divination-question {
  margin-bottom: 10px;
  padding-left: 5px;
  border-left: 3px solid #4CAF50;
}

.divination-result {
  line-height: 1.5;
  padding-left: 5px;
  border-left: 3px solid #2196F3;
}

.divination-footer {
  padding: 15px 20px;
  background-color: white;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
}

.new-divination-btn {
  width: 100%;
  padding: 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: bold;
}
</style>