// src/api/axios.js
import axios from 'axios';
import { getToken, removeToken, removeUser } from '../utils/auth';
// 注意：这里不能直接 import router from '../router'，否则会产生循环引用报错
// 我们通过 window 或者在 main.js 里挂载的方式，或者简单抛出错误在组件层处理
// 最简单的修复是保持 href 跳转但只在确实需要时触发，或者使用 cleaner way:

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const instance = axios.create({
  baseURL,
  timeout: 15000, // 延长到 15s，适应 B2B 弱网环境
});

instance.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      
      // 401: Token 过期
      if (status === 401) {
        removeToken();
        removeUser();
        
        // 只有当不在登录页时才跳转，防止死循环
        if (!window.location.pathname.includes('/login')) {
             // 简单的跳转是安全的，虽然不是 SPA 方式，但在 401 这种严重错误下是可以接受的
             window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
        }
      }
    }
    return Promise.reject(error);
  }
);

export default instance;