// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';

// --- 1. 前台页面组件 (Public) ---
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ProductsView from '../views/ProductsView.vue';
import NewsView from '../views/NewsView.vue';
import NewsDetailView from '../views/NewsDetailView.vue';
import OrderHistoryView from '../views/OrderHistoryView.vue'; // 客户订单历史

// --- 2. 专用页面 ---
// 【关键修复】引入派送员工作台
import DriverDashboard from '../views/DriverDashboard.vue';

// --- 3. 后台管理组件 (Admin) ---
import AdminLayout from '../views/admin/AdminLayout.vue';
import Dashboard from '../views/admin/Dashboard.vue';
import ProductManager from '../views/admin/ProductManager.vue';
import UserManager from '../views/admin/UserManager.vue';
import NewsManager from '../views/admin/NewsManager.vue';
import OrderManager from '../views/admin/OrderManager.vue';
import CategoryManager from '../views/admin/CategoryManager.vue'; // 分类管理
// 1. 引入新组件
import CustomerManager from '../views/admin/CustomerManager.vue';
import EmployeeManager from '../views/admin/EmployeeManager.vue';

const routes = [
  // ==============================
  // 前台路由
  // ==============================
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/products', name: 'Products', component: ProductsView },
  { path: '/news', name: 'NewsList', component: NewsView },
  { path: '/news/:id', name: 'NewsDetail', component: NewsDetailView },
  { path: '/my-orders', name: 'MyOrders', component: OrderHistoryView },
  // 1. 客户查看页 (公开)
      {
        path: '/specs',
        name: 'TechSpecs',
        component: () => import('../views/TechSpecs.vue')
      },

  // ==============================
  // 派送员专用路由 (隐藏导航栏)
  // ==============================
  {
    path: '/driver',
    name: 'DriverDashboard',
    component: DriverDashboard,
    meta: { hideNavbar: true } // 派送员页面不需要官网导航栏
  },

  // ==============================
  // 后台路由 (隐藏导航栏)
  // ==============================
  {
    path: '/admin',
    component: AdminLayout,
    meta: { hideNavbar: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: Dashboard },
      { path: 'products', name: 'AdminProducts', component: ProductManager },
      { path: 'categories', name: 'AdminCategories', component: CategoryManager },
      { path: 'users', name: 'AdminUsers', component: UserManager },
      { path: 'news', name: 'AdminNews', component: NewsManager },
      { path: 'orders', name: 'AdminOrders', component: OrderManager },
      { path: 'customers', name: 'AdminCustomers', component: CustomerManager },
      { path: 'employees', name: 'AdminEmployees', component: EmployeeManager },
      
      // 2. 后台管理页 (需要管理员权限)
      {
        path: '/admin/specs',
        name: 'SpecManager',
        component: () => import('../views/admin/SpecManager.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      }
    ]
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
  const token = localStorage.getItem('access_token');
  const userInfoStr = localStorage.getItem('user_info');
  let user = null;

  if (userInfoStr) {
    try {
      user = JSON.parse(userInfoStr);
    } catch (e) { console.error(e); }
  }

  // 简单的后台权限拦截
  if (to.path.startsWith('/admin')) {
    if (!token) return next('/login');
    // 检查是否为管理员 (支持 is_superuser 或 is_admin)
    if (!user || (!user.is_superuser && !user.is_admin)) {
      alert('无权访问后台');
      return next('/');
    }
  }

  // 简单的派送员权限拦截 (可选)
  if (to.path.startsWith('/driver')) {
    if (!token) return next('/login');
    // 如果你有 role 字段，可以在这里检查 user.role === 'driver'
  }

  next();
});

export default router;