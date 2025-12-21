// src/api/axios.js
import axios from 'axios';
import { getToken, removeToken, removeUser } from '../utils/auth';

// 使用环境变量，如果没有配置则回退到 localhost
// 注意：Vite 中环境变量必须以 VITE_ 开头
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const instance = axios.create({
  baseURL,
  timeout: 10000, // 增加超时时间防止大文件上传失败
});

// 请求拦截器
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

// 响应拦截器
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      
      // 401 未授权：清理缓存并跳转登录
      if (status === 401) {
        removeToken();
        removeUser();
        // 这里不直接引入 router 以避免循环依赖，使用原生跳转或抛出特定错误由组件处理
        // 或者使用 window.location.href = '/login' (最稳妥的暴力跳转)
        if (window.location.pathname !== '/login') {
            window.location.href = '/login?expired=1'; 
        }
      }
    }
    return Promise.reject(error);
  }
);

export default instance;