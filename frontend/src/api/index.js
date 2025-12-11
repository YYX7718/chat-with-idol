import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API 请求错误:', error)
    return Promise.reject(error)
  }
)

// API 接口
export const api = {
  // 偶像相关
  getIdols: () => apiClient.get('/idols'),
  getIdol: (idolId) => apiClient.get(`/idols/${idolId}`),
  
  // 会话相关
  createSession: (data) => apiClient.post('/sessions', data),
  getSession: (sessionId) => apiClient.get(`/sessions/${sessionId}`),
  deleteSession: (sessionId) => apiClient.delete(`/sessions/${sessionId}`),
  
  // 聊天相关
  sendMessage: (sessionId, data) => apiClient.post(`/chat/${sessionId}`, data),
  getMessages: (sessionId, params) => apiClient.get(`/chat/${sessionId}/messages`, { params }),
  
  // 占卜相关
  requestDivination: (sessionId, data) => apiClient.post(`/divination/${sessionId}`, data),
  getDivinationHistory: (sessionId, params) => apiClient.get(`/divination/${sessionId}/history`, { params })
}

// 导出默认 API
export default api