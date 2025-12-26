<template>
  <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
  </div>
  <div v-else>
    <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <div class="bg-orange-100 p-2 rounded-lg text-orange-600">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
        </div>
        <div>
          <div class="text-xs text-gray-500 uppercase font-bold tracking-wider">今日基准铜价</div>
          <div class="text-xl font-mono font-bold text-gray-900 flex items-center gap-2">
            ¥{{ copperPrice.price?.toLocaleString() || '---' }}
            <span class="text-xs text-gray-400 font-normal">Updated: {{ copperPrice.updated }}</span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-3 w-full md:w-auto">
        <button class="flex-1 md:flex-none bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors">
          调整售价
        </button>
        <button class="flex-1 md:flex-none bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors">
          下载报表
        </button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">待处理询价</div>
        <div class="flex justify-between items-end">
          <span class="text-3xl font-bold text-gray-900">{{ stats.pending_inquiries }}</span>
          <span v-if="stats.pending_inquiries > 0" class="text-xs text-orange-600 font-medium bg-orange-50 px-2 py-1 rounded">急需报价</span>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">配送中订单</div>
        <div class="flex justify-between items-end">
          <span class="text-3xl font-bold text-gray-900">{{ stats.active_orders }}</span>
          <span class="text-xs text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded">正在进行</span>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">本月销售额</div>
        <div class="flex justify-between items-end">
          <span class="text-2xl font-bold text-gray-900">¥{{ (stats.total_sales / 10000).toFixed(1) }}w</span>
          <span class="text-xs text-green-600 font-medium">累计</span>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">活跃司机</div>
        <div class="flex justify-between items-end">
          <span class="text-3xl font-bold text-gray-900">{{ stats.active_drivers }}</span>
          <span class="text-xs text-gray-400">人</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <h3 class="font-bold text-gray-800">最新动态</h3>
          <router-link to="/admin/orders" class="text-xs text-orange-600 hover:underline">查看全部</router-link>
        </div>
        <div class="divide-y divide-gray-100">
          <div v-for="inq in recentInquiries" :key="'inq-'+inq.id" class="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
                BOM
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">询价单 #{{ inq.id }} <span class="text-xs font-normal text-gray-500">({{ inq.items.length }} 种商品)</span></p>
                <p class="text-xs text-gray-500">客户: {{ inq.user_email }} • {{ new Date(inq.created_at).toLocaleDateString() }}</p>
              </div>
            </div>
            <button @click="$router.push('/admin/inquiries')" class="px-3 py-1.5 bg-orange-600 text-white text-xs rounded hover:bg-orange-500">去报价</button>
          </div>
          
          <div v-for="ord in recentOrders" :key="'ord-'+ord.id" class="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold text-xs">
                ORD
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">订单 #{{ ord.id }}</p>
                <p class="text-xs text-gray-500">¥{{ ord.final_total_price }} • {{ ord.status }}</p>
              </div>
            </div>
            <button @click="$router.push('/admin/orders')" class="px-3 py-1.5 border border-gray-300 text-gray-600 text-xs rounded hover:bg-gray-50">查看</button>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200 bg-red-50/50">
          <h3 class="font-bold text-red-800">库存预警 (Low Stock)</h3>
        </div>
        <div class="p-4 space-y-4">
          <div v-for="(item, idx) in stats.low_stock_items" :key="idx" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div>
              <div class="text-sm font-bold text-gray-900 truncate w-32" :title="item.name">{{ item.name }}</div>
              <div class="text-xs text-gray-500">当前: {{ item.stock }} {{ item.unit }}</div>
            </div>
            <span class="text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded">缺货</span>
          </div>
          <div v-if="!stats.low_stock_items || stats.low_stock_items.length === 0" class="text-center text-xs text-gray-400 py-4">
            库存充足
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';

const loading = ref(true);
const stats = ref({
  pending_inquiries: 0,
  active_orders: 0,
  total_sales: 0,
  active_drivers: 0,
  low_stock_items: []
});
const copperPrice = ref({ price: 0, updated: '' });
const recentInquiries = ref([]);
const recentOrders = ref([]);

const initData = async () => {
  try {
    const [statsRes, priceRes, inqRes, ordRes] = await Promise.all([
      api.get('/admin/stats'),
      api.get('/meta/prices'),
      api.get('/inquiries/?limit=3&status=pending'),
      api.get('/orders/?limit=3')
    ]);
    
    stats.value = statsRes.data;
    copperPrice.value = priceRes.data.CNY;
    copperPrice.value.updated = priceRes.data.updated.split(' ')[1]; // 只取时间
    recentInquiries.value = inqRes.data;
    recentOrders.value = ordRes.data;
    
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(initData);
</script>