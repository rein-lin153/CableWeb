import axios from 'axios';
import router from '../router';
import { useToast } from '../composables/useToast'; // <--- 1. 导入

const instance = axios.create({
  baseURL: 'https://192.168.1.76:8000/api/v1',
});

instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
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
    const { error: showError } = useToast(); // <--- 2. 获取报错方法

    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || '未知错误';
      
      // 401 未登录：静默跳转，或者提示
      if (status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        router.push('/login');
        showError('登录已过期，请重新登录'); // 弹窗提示
      } 
      // 400/403/404/500 等：直接弹窗显示后端返回的 detail
      else {
        showError(detail); 
      }
    } else {
      showError('网络连接失败，请检查服务器');
    }
    return Promise.reject(error);
  }
);

export default instance;