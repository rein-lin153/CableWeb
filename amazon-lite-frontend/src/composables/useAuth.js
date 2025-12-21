// src/composables/useAuth.js
import { ref } from 'vue';
import api from '../api/axios';
import { getToken, getUser, setUser, setToken, removeToken, removeUser } from '../utils/auth';

// 全局状态 (单例模式)
const user = ref(null);
const isLoggedIn = ref(false);

export function useAuth() {

  // 1. 初始化状态
  const initializeAuth = async () => {
    const token = getToken();
    const storedUser = getUser();

    if (token) {
      isLoggedIn.value = true;
      if (storedUser) {
        user.value = storedUser;
      }
      
      // 后台静默更新
      try {
        const res = await api.get('/users/me');
        user.value = res.data;
        setUser(res.data); // 更新本地存储
      } catch (e) {
        // 如果 token 失效，api/axios.js 会处理
        console.error("更新用户信息失败", e);
      }
    }
  };

  // 2. 登录
  const login = async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    const token = res.data.access_token;
    setToken(token); // 使用工具存 token
    
    isLoggedIn.value = true;
    user.value = res.data.user; // 假设后端直接返回了 user，如果没返回则需再请求 /users/me
    setUser(user.value);
    
    return true;
  };

  // 3. 注册
  const register = async (email, password, companyName) => {
    await api.post('/users/', {
        email,
        password,
        company_name: companyName,
        username: email.split('@')[0], 
        role: 'user' 
    });
    // 注册后自动登录
    await login(email, password);
  };

  // 4. 登出
  const logout = () => {
    removeToken();
    removeUser();
    user.value = null; // 【关键】重置全局状态
    isLoggedIn.value = false;
  };

  return {
    user,
    isLoggedIn,
    login,
    register,
    logout,
    initializeAuth
  };
}