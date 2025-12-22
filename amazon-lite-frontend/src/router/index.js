// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated, isAdmin } from '../utils/auth';

// --- 1. 核心前台页面 (保留静态引入，保证首屏速度) ---
import HomeView from '../views/HomeView.vue';
import ProductsView from '../views/ProductsView.vue';
import LoginView from '../views/LoginView.vue';

const routes = [
  // ==============================
  // 前台路由 (Public & User)
  // ==============================
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  { 
    path: '/register', 
    name: 'Register', 
    component: () => import('../views/RegisterView.vue') // 注册页也可以懒加载
  },
  { path: '/products', name: 'Products', component: ProductsView },
  
  // 用户中心 (懒加载)
  {
    path: '/my-inquiries',
    name: 'UserInquiries',
    component: () => import('../views/user/UserInquiries.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders/my',
    name: 'MyOrders',
    component: () => import('../views/OrderHistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('../views/CheckoutView.vue'),
    meta: { requiresAuth: true }
  },

  // ==============================
  // 派送员专用路由 (懒加载)
  // ==============================
  {
    path: '/driver',
    name: 'DriverDashboard',
    component: () => import('../views/DriverDashboard.vue'),
    meta: { hideNavbar: true, requiresAuth: true }
  },

  // ==============================
  // 后台路由 (Admin - 懒加载核心区)
  // ==============================
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'), // 布局也懒加载
    meta: { hideNavbar: true, requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { 
        path: 'dashboard', 
        name: 'AdminDashboard', 
        component: () => import('../views/admin/Dashboard.vue') 
      },
      { 
        path: 'products', 
        name: 'AdminProducts', 
        component: () => import('../views/admin/ProductManager.vue') 
      },
      { 
        path: 'categories', 
        name: 'AdminCategories', 
        component: () => import('../views/admin/CategoryManager.vue') 
      },
      { 
        path: 'users', 
        name: 'AdminUsers', 
        component: () => import('../views/admin/UserManager.vue') 
      },
      { 
        path: 'orders', 
        name: 'AdminOrders', 
        component: () => import('../views/admin/OrderManager.vue') 
      },
      { 
        path: 'customers', 
        name: 'AdminCustomers', 
        component: () => import('../views/admin/CustomerManager.vue') 
      },
      { 
        path: 'inquiries', 
        name: 'AdminInquiries', 
        component: () => import('../views/admin/InquiryManager.vue') 
      },
      {
        path: 'costs',
        name: 'CostCalculator',
        component: () => import('../views/admin/CostCalculator.vue')
      },
    ]
  },
  
  // 404 页面
  { 
    path: '/:pathMatch(.*)*', 
    redirect: '/' 
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    return { top: 0 };
  }
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuth = isAuthenticated();

  // 1. 检查需要登录的页面
  if (to.meta.requiresAuth && !isAuth) {
    // 记录想去的页面，登录后跳转
    return next({ path: '/login', query: { redirect: to.fullPath } });
  }

  // 2. 检查管理员权限
  if (to.meta.requiresAdmin && !isAdmin()) {
    return next('/');
  }

  // 3. 已登录用户访问登录页，直接跳首页
  if (to.path === '/login' && isAuth) {
    return next('/');
  }

  next();
});

export default router;