// src/utils/auth.js

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user_info';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  return localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken() {
  return localStorage.removeItem(TOKEN_KEY);
}

export function getUser() {
  const userStr = localStorage.getItem(USER_KEY);
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    console.error('User info parse error', e);
    return null;
  }
}

export function setUser(user) {
  return localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function removeUser() {
  return localStorage.removeItem(USER_KEY);
}

// 简单的权限检查辅助函数
export function isAuthenticated() {
  return !!getToken();
}

export function isAdmin() {
  const user = getUser();
  return user && (user.role === 'admin' || user.is_admin || user.is_superuser);
}