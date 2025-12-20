// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';

// --- 1. 前台页面组件 (Public) ---
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ProductsView from '../views/ProductsView.vue';
import NewsView from '../views/NewsView.vue';
import NewsDetailView from '../views/NewsDetailView.vue';
import OrderHistoryView from '../views/OrderHistoryView.vue';
import InquiryList from '../views/InquiryList.vue';
import TechSpecs from '../views/TechSpecs.vue';
import CheckoutView from '../views/CheckoutView.vue'; // [新增] 引入结算页
import UserInquiries from '../views/user/UserInquiries.vue';

// --- 2. 专用页面 ---
import DriverDashboard from '../views/DriverDashboard.vue';

// --- 3. 后台管理组件 (Admin) ---
import AdminLayout from '../views/admin/AdminLayout.vue';
import Dashboard from '../views/admin/Dashboard.vue';
import ProductManager from '../views/admin/ProductManager.vue';
import UserManager from '../views/admin/UserManager.vue';
import NewsManager from '../views/admin/NewsManager.vue';
import OrderManager from '../views/admin/OrderManager.vue';
import CategoryManager from '../views/admin/CategoryManager.vue';
import CustomerManager from '../views/admin/CustomerManager.vue';
import EmployeeManager from '../views/admin/EmployeeManager.vue';
import SpecManager from '../views/admin/SpecManager.vue';
import InquiryManager from '../views/admin/InquiryManager.vue';
import CostCalculator from '../views/admin/CostCalculator.vue';

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
  { path: '/specs', name: 'TechSpecs', component: TechSpecs },
  {
    path: '/my-inquiries',
    name: 'MyInquiries',
    component: UserInquiries,
    meta: { requiresAuth: true }
  },


  // 订单相关
  {
    path: '/orders/my',
    name: 'MyOrders',
    component: OrderHistoryView,
    meta: { requiresAuth: true }
  },

  // [新增] 结算页面路由
  {
    path: '/checkout',
    name: 'Checkout',
    component: CheckoutView,
    meta: { requiresAuth: true }
  },

  // 询价相关
  {
    path: '/inquiries',
    name: 'MyInquiries',
    component: InquiryList,
    meta: { requiresAuth: true }
  },

  // ==============================
  // 派送员专用路由 (隐藏导航栏)
  // ==============================
  {
    path: '/driver',
    name: 'DriverDashboard',
    component: DriverDashboard,
    meta: { hideNavbar: true, requiresAuth: true }
  },



  // ==============================
  // 后台路由 (隐藏导航栏)
  // ==============================
  {
    path: '/admin',
    component: AdminLayout,
    meta: { hideNavbar: true, requiresAuth: true, requiresAdmin: true },
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
      { path: 'specs', name: 'SpecManager', component: SpecManager },
      { path: 'inquiries', name: 'AdminInquiries', component: InquiryManager },
      {
        path: 'costs',
        name: 'CostCalculator',
        component: CostCalculator
      },
    ]
  },
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

  // 1. 检查需要登录的页面
  if (to.meta.requiresAuth && !token) {
    return next('/login');
  }

  // 2. 检查管理员权限
  if (to.meta.requiresAdmin) {
    const isAdmin = user && (user.is_superuser || user.is_admin || user.role === 'admin');
    if (!isAdmin) {
      alert('无权访问后台');
      return next('/');
    }
  }

  next();
});

export default router;