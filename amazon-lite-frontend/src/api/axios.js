// src/api/axios.js
import axios from 'axios';
import { getToken, removeToken, removeUser } from '../utils/auth';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const instance = axios.create({
  baseURL,
  timeout: 15000,
});

// 重试配置
const RETRY_CONFIG = {
  retries: 3,
  retryDelay: (retryCount) => retryCount * 1000, // 1s, 2s, 3s
  shouldRetry: (error) => {
    // 仅针对网络错误或 5xx 服务端错误重试，4xx 客户端错误不重试
    return !error.response || (error.response.status >= 500 && error.response.status <= 599);
  }
};

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
  async (error) => {
    const config = error.config;

    // 401 处理：Token 过期
    if (error.response && error.response.status === 401) {
      removeToken();
      removeUser();
      if (!window.location.pathname.includes('/login')) {
        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
      }
      return Promise.reject(error);
    }

    // 重试逻辑
    if (config && RETRY_CONFIG.shouldRetry(error) && (config.__retryCount || 0) < RETRY_CONFIG.retries) {
      config.__retryCount = config.__retryCount || 0;
      config.__retryCount += 1;

      // 创建延时 Promise
      const backoff = new Promise((resolve) => {
        setTimeout(() => resolve(), RETRY_CONFIG.retryDelay(config.__retryCount));
      });

      console.warn(`[Network] Retrying request... (${config.__retryCount}/${RETRY_CONFIG.retries})`);
      await backoff;
      return instance(config);
    }

    return Promise.reject(error);
  }
);

export default instance;