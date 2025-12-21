<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        我的采购订单
        <span class="ml-3 text-xs font-normal text-gray-500 bg-white px-2 py-1 rounded-full border border-gray-200">仅显示最近半年的订单</span>
      </h1>

      <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
      </div>
      
      <div v-else-if="orders.length === 0" class="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
        </div>
        <p class="text-gray-500">暂无订单记录</p>
        <button @click="$router.push('/products')" class="mt-4 px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-orange-600 transition-colors">去选购材料</button>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="order in orders" 
          :key="order.id" 
          @click="openDetail(order)"
          class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer hover:border-orange-200 hover:shadow-md transition-all group"
        >
          <div class="px-6 py-4 flex justify-between items-center bg-gray-50/50">
            <div class="flex items-center gap-3">
              <span class="font-bold text-gray-700">#{{ order.id }}</span>
              <span class="text-xs text-gray-400">{{ new Date(order.created_at).toLocaleDateString() }}</span>
            </div>
            <span class="px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1" :class="getStatusClass(order.status)">
              <span class="w-1.5 h-1.5 rounded-full" :class="getStatusDotClass(order.status)"></span>
              {{ formatStatus(order.status) }}
            </span>
          </div>
          <div class="p-6 flex justify-between items-center">
             <div class="flex -space-x-2 overflow-hidden">
               <div v-for="i in Math.min(order.items?.length || 0, 3)" :key="i" class="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-200"></div>
               <div v-if="order.items?.length > 3" class="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-100 flex items-center justify-center text-[10px] text-gray-500 font-bold">+{{order.items.length - 3}}</div>
             </div>
             <div class="text-right">
               <div class="text-xs text-gray-400 mb-1">共 {{ order.items?.length }} 件商品</div>
               <div class="text-lg font-bold text-gray-900 font-mono">¥{{ order.final_total_price }}</div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedOrder" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-scale-up">
        
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h3 class="text-lg font-bold text-gray-900">订单详情 #{{ selectedOrder.id }}</h3>
          <button @click="closeDetail" class="text-gray-400 hover:text-gray-900 bg-white border border-gray-200 rounded-full p-2 hover:bg-gray-50 transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-hide">
          
          <div class="relative">
             <div class="absolute left-0 top-1/2 w-full h-1 bg-gray-100 -z-10 rounded"></div>
             <div class="flex justify-between text-xs font-medium text-gray-500">
               <div class="flex flex-col items-center bg-white px-2">
                 <div class="w-3 h-3 rounded-full bg-green-500 mb-2 ring-4 ring-white"></div>
                 已下单
               </div>
               <div class="flex flex-col items-center bg-white px-2">
                 <div class="w-3 h-3 rounded-full mb-2 ring-4 ring-white" :class="['confirmed', 'delivering', 'completed'].includes(selectedOrder.status) ? 'bg-green-500' : 'bg-gray-300'"></div>
                 备货中
               </div>
               <div class="flex flex-col items-center bg-white px-2">
                 <div class="w-3 h-3 rounded-full mb-2 ring-4 ring-white" :class="['delivering', 'completed'].includes(selectedOrder.status) ? 'bg-green-500' : 'bg-gray-300'"></div>
                 配送中
               </div>
               <div class="flex flex-col items-center bg-white px-2">
                 <div class="w-3 h-3 rounded-full mb-2 ring-4 ring-white" :class="selectedOrder.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'"></div>
                 已送达
               </div>
             </div>
          </div>

          <div v-if="selectedOrder.status === 'delivering' || selectedOrder.status === 'completed'">
            
            <div v-if="selectedOrder.shipping_method !== 'third_party'" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
              <div class="p-3 bg-blue-50 border-b border-blue-100 flex justify-between items-center">
                <h4 class="text-xs font-bold text-blue-800 uppercase flex items-center">
                  <span class="relative flex h-2 w-2 mr-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                  </span>
                  金边专车配送中 (实时位置)
                </h4>
                <div class="text-[10px] text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">销售专员正在赶往工地</div>
              </div>
              <div id="map" class="h-64 w-full bg-gray-100 z-0 relative">
                 <div v-if="!mapLoaded" class="absolute inset-0 flex items-center justify-center text-gray-400 text-xs">正在连接卫星定位...</div>
              </div>
            </div>

            <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-5">
              <h4 class="text-sm font-bold text-gray-900 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                物流信息 (外省配送)
              </h4>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div class="text-gray-500 text-xs mb-1">物流公司</div>
                  <div class="font-bold text-gray-900">{{ selectedOrder.logistics_company || 'J&T 极兔速递' }}</div>
                </div>
                <div>
                  <div class="text-gray-500 text-xs mb-1">运单编号</div>
                  <div class="font-bold text-gray-900 font-mono select-all">{{ selectedOrder.tracking_number || '待更新' }}</div>
                </div>
                <div class="col-span-2 mt-2 pt-3 border-t border-gray-200">
                  <div class="text-gray-500 text-xs mb-1">物流轨迹</div>
                  <div class="text-gray-600 bg-white p-2 rounded border border-gray-200 text-xs">
                    {{ selectedOrder.logistics_latest_trace || '您的包裹已发出，正在前往目的地...' }}
                  </div>
                </div>
              </div>
            </div>

          </div>

          <div v-if="selectedOrder.delivery_photo_url" class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              现场签收实拍
            </h4>
            <div class="relative group overflow-hidden rounded-lg">
              <img :src="selectedOrder.delivery_photo_url" class="w-full h-48 object-cover cursor-zoom-in hover:scale-105 transition-transform duration-500" onclick="window.open(this.src)">
            </div>
          </div>

          <div>
            <h4 class="text-sm font-bold text-gray-900 mb-3">商品清单</h4>
            <div class="border border-gray-200 rounded-xl overflow-hidden">
              <table class="min-w-full text-sm">
                <thead class="bg-gray-50 text-xs uppercase text-gray-500 font-medium">
                  <tr>
                    <th class="px-4 py-2 text-left">名称/规格</th>
                    <th class="px-4 py-2 text-center">数量</th>
                    <th class="px-4 py-2 text-right">小计</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in selectedOrder.items" :key="item.id" class="bg-white">
                    <td class="px-4 py-3">
                      <div class="font-bold text-gray-900">{{ item.product_name }}</div>
                      <div class="text-xs text-gray-500 mt-0.5">{{ item.spec || item.product_spec }}</div>
                    </td>
                    <td class="px-4 py-3 text-center text-gray-600 font-mono">x{{ item.quantity }}</td>
                    <td class="px-4 py-3 text-right font-bold text-gray-900 font-mono">¥{{ item.subtotal }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 bg-gray-50 text-right border-t border-gray-100 flex justify-end items-baseline">
          <span class="text-xs text-gray-500 mr-2">共 {{ selectedOrder.items.length }} 件，实付:</span>
          <span class="text-2xl font-bold text-orange-600 font-mono">¥{{ selectedOrder.final_total_price }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import api from '../api/axios';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Leaflet 图标修复
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
const mapLoaded = ref(false);

let mapInstance = null;
let markerInstance = null;
let mapInterval = null;

const fetchMyOrders = async () => {
  try {
    const res = await api.get('/orders/my');
    orders.value = res.data;
  } catch (error) { console.error(error); } finally { loading.value = false; }
};

const openDetail = (order) => {
  selectedOrder.value = order;
  // 仅当是自主配送且在配送中时，初始化地图
  if (order.status === 'delivering' && order.shipping_method !== 'third_party') {
    mapLoaded.value = false;
    nextTick(() => {
      initMap(order);
      mapInterval = setInterval(() => updateMapLocation(order.id), 5000);
    });
  }
};

const closeDetail = () => {
  selectedOrder.value = null;
  if (mapInstance) { mapInstance.remove(); mapInstance = null; }
  if (mapInterval) { clearInterval(mapInterval); mapInterval = null; }
};

const initMap = (order) => {
  const container = document.getElementById('map');
  if (!container) return; // 防止弹窗关闭后执行报错

  // 默认金边坐标 11.5564, 104.9282
  const lat = order.driver_lat || 11.5564; 
  const lng = order.driver_lng || 104.9282;

  mapInstance = L.map('map').setView([lat, lng], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap' }).addTo(mapInstance);
  markerInstance = L.marker([lat, lng]).addTo(mapInstance).bindPopup('配送员当前位置').openPopup();
  mapLoaded.value = true;
};

const updateMapLocation = async (orderId) => {
  try {
    const res = await api.get(`/orders/${orderId}`);
    const { driver_lat, driver_lng } = res.data;
    if (driver_lat && driver_lng && mapInstance && markerInstance) {
      const newLatLng = new L.LatLng(driver_lat, driver_lng);
      markerInstance.setLatLng(newLatLng);
      mapInstance.panTo(newLatLng);
    }
  } catch (e) { console.error("同步位置失败", e); }
};

const formatStatus = (s) => {
  const map = { pending_confirmation: '待确认', confirmed: '备货中', delivering: '配送中', completed: '已送达', cancelled: '已取消' };
  return map[s] || s;
};

const getStatusClass = (s) => {
  const map = {
    pending_confirmation: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    confirmed: 'bg-green-50 text-green-700 border-green-200',
    delivering: 'bg-blue-50 text-blue-700 border-blue-200',
    completed: 'bg-gray-100 text-gray-600 border-gray-200',
    cancelled: 'bg-gray-50 text-gray-400 border-gray-200'
  };
  return map[s] || '';
};

const getStatusDotClass = (s) => {
  const map = { pending_confirmation: 'bg-yellow-500', confirmed: 'bg-green-500', delivering: 'bg-blue-500 animate-pulse', completed: 'bg-gray-500', cancelled: 'bg-gray-300' };
  return map[s] || 'bg-gray-400';
};

onMounted(fetchMyOrders);
onUnmounted(() => { if (mapInterval) clearInterval(mapInterval); });
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
@keyframes scaleUp { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.animate-scale-up { animation: scaleUp 0.2s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.animate-fade-in { animation: fadeIn 0.2s ease-out forwards; }
</style>