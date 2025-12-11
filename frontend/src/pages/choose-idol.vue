<template>
  <div class="choose-idol-container">
    <h1 class="title">选择你的偶像</h1>
    <div class="idol-list">
      <div 
        v-for="idol in idols" 
        :key="idol.id"
        class="idol-card"
        @click="selectIdol(idol)"
      >
        <div class="idol-avatar">
          {{ idol.name.charAt(0) }}
        </div>
        <h3 class="idol-name">{{ idol.name }}</h3>
        <p class="idol-description">{{ idol.description }}</p>
        <div class="idol-personality">{{ idol.personality }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api'

export default {
  name: 'ChooseIdol',
  setup() {
    const idols = ref([])
    
    // 获取偶像列表
    const fetchIdols = async () => {
      try {
        const response = await api.getIdols()
        idols.value = response.idols
      } catch (error) {
        console.error('获取偶像列表失败:', error)
      }
    }
    
    // 选择偶像
    const selectIdol = async (idol) => {
      try {
        // 创建会话
        const response = await api.createSession({ idol_id: idol.id })
        
        // 保存会话信息到本地存储
        localStorage.setItem('currentSession', JSON.stringify({
          session_id: response.session_id,
          idol_id: idol.id,
          idol_name: idol.name
        }))
        
        // 跳转到聊天页面
        window.location.href = '#/chat'
      } catch (error) {
        console.error('创建会话失败:', error)
      }
    }
    
    // 页面加载时获取偶像列表
    onMounted(() => {
      fetchIdols()
    })
    
    return {
      idols,
      selectIdol
    }
  }
}
</script>

<style scoped>
.choose-idol-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  text-align: center;
  font-size: 2rem;
  color: #333;
  margin-bottom: 30px;
}

.idol-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.idol-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.idol-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.idol-avatar {
  width: 80px;
  height: 80px;
  background-color: #4CAF50;
  border-radius: 50%;
  color: white;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
}

.idol-name {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 10px;
}

.idol-description {
  color: #666;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.idol-personality {
  color: #888;
  font-size: 0.8rem;
  line-height: 1.4;
}
</style>