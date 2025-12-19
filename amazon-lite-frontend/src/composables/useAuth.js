// src/composables/useAuth.js
import { ref } from 'vue';
import api from '../api/axios';

// === 全局状态 (单例模式) ===
// 这样无论在哪个组件引用 useAuth，状态都是同步的
const user = ref(null);
const isLoggedIn = ref(false);

export function useAuth() {

  // 1. 初始化/恢复状态 (在 App.vue 挂载时调用)
  const initializeAuth = async () => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user_info');

    if (token) {
      isLoggedIn.value = true;
      
      // A. 先尝试从本地缓存恢复 (速度快，防止页面闪烁)
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser);
        } catch (e) {
          console.error("解析用户信息失败", e);
          localStorage.removeItem('user_info');
        }
      }

      // B. 后台静默更新用户信息 (确保角色/权限是最新的)
      try {
        const res = await api.get('/users/me');
        user.value = res.data;
        // 更新缓存
        localStorage.setItem('user_info', JSON.stringify(res.data));
      } catch (e) {
        console.error("获取最新用户信息失败", e);
        // 如果 401 说明 token 过期，需要登出
        if (e.response?.status === 401) {
          logout();
        }
      }
    }
  };

  // 2. 登录逻辑
  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const token = res.data.access_token;
      localStorage.setItem('access_token', token);
      
      // 设置状态
      isLoggedIn.value = true;

      // 【关键】登录成功后，立即获取并保存用户信息
      // 很多后端登录接口只返回 token，不返回 user，所以需要单独查一次
      const userRes = await api.get('/users/me');
      user.value = userRes.data;
      localStorage.setItem('user_info', JSON.stringify(userRes.data));

      return true;
    } catch (e) {
      console.error('登录失败:', e);
      throw e;
    }
  };

  // 3. 注册逻辑
  const register = async (email, password, companyName) => {
    try {
      await api.post('/users/', {
        email,
        password,
        company_name: companyName,
        username: email.split('@')[0], // 默认用户名
        role: 'user' // 默认角色
      });
      // 注册后自动登录
      await login(email, password);
    } catch (e) {
      throw e;
    }
  };

  // 4. 登出逻辑
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    user.value = null;
    isLoggedIn.value = false;
  };

  return {
    user,
    isLoggedIn,
    login,
    register,
    logout,
    initializeAuth // 导出这个新函数
  };
}