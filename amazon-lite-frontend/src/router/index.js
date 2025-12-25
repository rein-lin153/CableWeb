// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated, isAdmin } from '../utils/auth';

// 核心页面静态引入
import HomeView from '../views/HomeView.vue';
import ProductsView from '../views/ProductsView.vue';
import LoginView from '../views/LoginView.vue';

const routes = [
  // ==============================
  // 前台路由
  // ==============================
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  },
  { path: '/products', name: 'Products', component: ProductsView },

  // --- 【关键修复】新增功能路由注册 ---
  {
    path: '/quick-order',
    name: 'QuickOrder',
    // 对应之前的新增文件 src/views/QuickOrderPad.vue
    component: () => import('../views/QuickOrderPad.vue'),
    meta: { requiresAuth: true } // 建议设为需登录，如需公开测试可删去此行
  },
  {
    path: '/tools/voltage-drop',
    name: 'VoltageDrop',
    // 对应之前的新增文件 src/views/tools/VoltageDropCalculator.vue
    // ⚠️ 注意：请确保你已创建 src/views/tools 文件夹并放入了文件
    component: () => import('../views/tools/VoltageDropCalculator.vue')
  },

  // --- 【新增】穿管计算器路由 ---
  {
    path: '/tools/conduit-fill',
    name: 'ConduitFill',
    component: () => import('../views/tools/ConduitCalculator.vue')
  },

  // --- 【新增】装盘计算 & 标签打印 ---
  {
    path: '/tools/reel-calculator',
    name: 'ReelCalculator',
    component: () => import('../views/tools/ReelCalculator.vue')
  },
  {
    path: '/tools/label-printer',
    name: 'LabelPrinter',
    component: () => import('../views/tools/LabelPrinter.vue')
  },

  // --- 【新增】线规换算器路由 ---
  {
    path: '/tools/unit-converter',
    name: 'UnitConverter',
    component: () => import('../views/tools/CableUnitConverter.vue')
  },

  // 用户中心
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
  // 派送员路由
  // ==============================
  {
    path: '/driver',
    name: 'DriverDashboard',
    component: () => import('../views/DriverDashboard.vue'),
    meta: { hideNavbar: true, requiresAuth: true }
  },

  // ==============================
  // 后台路由
  // ==============================
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
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

  // 404 处理
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

router.beforeEach((to, from, next) => {
  const isAuth = isAuthenticated();

  if (to.meta.requiresAuth && !isAuth) {
    return next({ path: '/login', query: { redirect: to.fullPath } });
  }

  if (to.meta.requiresAdmin && !isAdmin()) {
    return next('/');
  }

  if (to.path === '/login' && isAuth) {
    return next('/');
  }

  next();
});

export default router;