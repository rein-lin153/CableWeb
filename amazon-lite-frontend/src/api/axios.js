// src/api/axios.js
import axios from 'axios';



// 1. 创建 axios 实例 (这里我们命名为 api)
const api = axios.create({
  baseURL: 'https://192.168.1.76:8000/api/v1', // 确保这是你后端的真实地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 2. 请求拦截器：自动携带 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 3. 响应拦截器：处理 401/403 错误
// 【注意】这里必须使用 'api'，不能用 'instance'
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      
      // Token 过期或未登录
      if (status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        // 可选：强制跳转登录页
        // window.location.href = '/login';
      }
      
      // 权限不足
      if (status === 403) {
        alert('⛔ 权限拒绝：您没有执行此操作的管理员权限。');
      }
    }
    return Promise.reject(error);
  }
);

export default api;