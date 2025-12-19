<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">我的采购订单</h1>

      <div v-if="loading" class="text-center py-20 text-gray-500">加载中...</div>
      
      <div v-else-if="orders.length === 0" class="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
        <p class="text-gray-500">暂无订单记录</p>
        <button @click="$router.push('/products')" class="mt-4 px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">去选购</button>
      </div>

      <div v-else class="space-y-6">
        <div 
          v-for="order in orders" 
          :key="order.id" 
          @click="openDetail(order)"
          class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer hover:shadow-md transition-all group"
        >
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
            <span class="font-bold text-gray-700">#{{ order.id }}</span>
            <span class="px-3 py-1 rounded-full text-xs font-bold border" :class="getStatusClass(order.status)">
              {{ formatStatus(order.status) }}
            </span>
          </div>
          <div class="p-6">
             <p class="text-sm text-gray-500 mb-2">下单时间: {{ new Date(order.created_at).toLocaleString() }}</p>
             <div class="flex justify-between items-end">
               <div class="text-sm font-medium">共 {{ order.items?.length }} 件商品</div>
               <div class="text-xl font-bold text-orange-600 font-mono">¥{{ order.final_total_price }}</div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedOrder" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h3 class="text-lg font-bold">订单详情 #{{ selectedOrder.id }}</h3>
          <button @click="closeDetail" class="text-gray-400 hover:text-gray-600 bg-gray-100 rounded-full p-1 w-8 h-8">✕</button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          
          <div class="flex items-center text-sm font-medium text-gray-500">
            当前状态：<span class="ml-2 px-2 py-1 rounded bg-gray-100 text-gray-800">{{ formatStatus(selectedOrder.status) }}</span>
          </div>

          <div v-if="selectedOrder.status === 'delivering'" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="p-3 bg-indigo-50 border-b border-indigo-100 flex justify-between items-center">
              <h4 class="text-xs font-bold text-indigo-800 uppercase flex items-center">
                <span class="relative flex h-2 w-2 mr-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                </span>
                实时配送中 (派送员位置)
              </h4>
              <span class="text-xs text-indigo-600">每5秒刷新</span>
            </div>
            <div id="map" class="h-64 w-full bg-gray-100 z-0"></div>
          </div>

          <div v-if="selectedOrder.delivery_photo_url" class="border border-gray-200 rounded-xl p-4">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center">
              到货实拍
            </h4>
            <div class="relative group">
              <img :src="selectedOrder.delivery_photo_url" class="w-full h-48 object-cover rounded-lg cursor-zoom-in" onclick="window.open(this.src)">
            </div>
          </div>

          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left">商品</th>
                <th class="px-4 py-2 text-center">数量</th>
                <th class="px-4 py-2 text-right">小计</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="item in selectedOrder.items" :key="item.id">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ item.product_name }}</div>
                  <div class="text-xs text-gray-500 mt-0.5">{{ item.spec || item.product_spec }} {{ item.color || item.product_color }}</div>
                </td>
                <td class="px-4 py-3 text-center text-gray-500">x{{ item.quantity }}</td>
                <td class="px-4 py-3 text-right font-bold text-gray-900">¥{{ item.subtotal }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="px-6 py-4 bg-gray-50 text-right border-t border-gray-100">
          <span class="text-gray-500 mr-2">实付金额:</span>
          <span class="text-2xl font-bold text-orange-600 font-mono">¥{{ selectedOrder.final_total_price }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import api from '../api/axios';

// === Leaflet 地图核心库 ===
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
// 修复 Leaflet 默认图标加载 bug
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const orders = ref([]);
const loading = ref(true);
const selectedOrder = ref(null);

// 地图相关变量
let mapInstance = null;
let markerInstance = null;
let mapInterval = null;

const fetchMyOrders = async () => {
  try {
    const res = await api.get('/orders/my');
    orders.value = res.data;
  } catch (error) { console.error(error); } finally { loading.value = false; }
};

// 打开弹窗
const openDetail = (order) => {
  selectedOrder.value = order;
  
  // 如果正在派送中，初始化地图
  if (order.status === 'delivering') {
    nextTick(() => {
      initMap(order);
      // 开启轮询
      mapInterval = setInterval(() => updateMapLocation(order.id), 5000);
    });
  }
};

// 关闭弹窗 (务必清理地图资源)
const closeDetail = () => {
  selectedOrder.value = null;
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }
  if (mapInterval) {
    clearInterval(mapInterval);
    mapInterval = null;
  }
};

// 初始化地图
const initMap = (order) => {
  // 默认坐标 (如果有司机坐标就用司机的，没有就默认无锡/上海等中心点)
  const lat = order.driver_lat || 31.5; 
  const lng = order.driver_lng || 120.3;

  mapInstance = L.map('map').setView([lat, lng], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(mapInstance);

  markerInstance = L.marker([lat, lng]).addTo(mapInstance)
    .bindPopup('派送员当前位置')
    .openPopup();
};

// 轮询更新地图位置
const updateMapLocation = async (orderId) => {
  try {
    const res = await api.get(`/orders/${orderId}`); // 获取最新订单信息
    const { driver_lat, driver_lng } = res.data;
    
    if (driver_lat && driver_lng && mapInstance && markerInstance) {
      const newLatLng = new L.LatLng(driver_lat, driver_lng);
      markerInstance.setLatLng(newLatLng);
      mapInstance.panTo(newLatLng);
    }
  } catch (e) { console.error("同步位置失败", e); }
};

const formatStatus = (s) => {
  const map = { pending_confirmation: '等待确认', confirmed: '备货中', delivering: '🚚 派送中', completed: '✅ 已送达', cancelled: '已作废' };
  return map[s] || s;
};

const getStatusClass = (s) => {
  const map = {
    pending_confirmation: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    confirmed: 'bg-green-50 text-green-700 border-green-200',
    delivering: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    completed: 'bg-gray-800 text-white border-gray-900',
    cancelled: 'bg-gray-100 text-gray-400 border-gray-200'
  };
  return map[s] || '';
};

onMounted(fetchMyOrders);

// 组件销毁时清理
onUnmounted(() => {
  if (mapInterval) clearInterval(mapInterval);
});
</script>