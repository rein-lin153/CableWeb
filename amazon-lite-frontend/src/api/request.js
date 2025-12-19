// src/api/request.js
import axios from 'axios';

const service = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // 指向你的 FastAPI 后端
  timeout: 5000
});

// 请求拦截器：自动在 Header 中携带 Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); // 假设登录后你把 token 存在了 localStorage
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default service;