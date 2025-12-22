<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12 font-sans text-gray-700">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 flex items-center">
            我的采购订单
          </h1>
          <p class="text-sm text-gray-500 mt-1">查看历史采购记录、追踪物流状态、下载合同单据</p>
        </div>
        <div class="flex gap-2">
           <div class="relative">
             <input type="text" placeholder="搜索订单号/项目名..." class="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-64 shadow-sm">
             <svg class="w-4 h-4 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
           </div>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-20">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-2"></div>
          <span class="text-xs text-gray-400">同步ERP数据中...</span>
        </div>
      </div>
      
      <div v-else-if="orders.length === 0" class="text-center py-24 bg-white rounded-xl shadow-sm border border-gray-200 dashed-border">
        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
        </div>
        <p class="text-gray-500 font-medium">暂无采购记录</p>
        <button @click="$router.push('/products')" class="mt-6 px-8 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200">去选购工程材料</button>
      </div>

      <div v-else class="space-y-6">
        <div 
          v-for="order in orders" 
          :key="order.id" 
          @click="openDetail(order)"
          class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden cursor-pointer hover:border-indigo-300 hover:shadow-md transition-all group relative"
        >
          <div class="px-6 py-4 flex flex-wrap justify-between items-center bg-gray-50/50 border-b border-gray-100 gap-2">
            <div class="flex items-center gap-4">
              <div>
                <span class="text-xs text-gray-400 block uppercase tracking-wider">Order ID</span>
                <span class="font-bold text-gray-900 font-mono text-base">#{{ order.id }}</span>
              </div>
              <div class="hidden sm:block w-px h-8 bg-gray-200"></div>
              <div class="hidden sm:block">
                <span class="text-xs text-gray-400 block">下单日期</span>
                <span class="text-sm text-gray-700">{{ new Date(order.created_at).toLocaleDateString() }}</span>
              </div>
            </div>
            
            <div class="flex items-center gap-3">
              <span class="px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 shadow-sm" :class="getStatusClass(order.status)">
                <span class="w-2 h-2 rounded-full" :class="getStatusDotClass(order.status)"></span>
                {{ formatStatus(order.status) }}
              </span>
              <svg class="w-5 h-5 text-gray-300 group-hover:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </div>
          </div>

          <div class="p-6 flex flex-col sm:flex-row justify-between items-center gap-6">
             <div class="flex items-center gap-4 w-full sm:w-auto overflow-x-auto pb-2 sm:pb-0">
               <div v-for="(item, idx) in (order.items || []).slice(0, 4)" :key="idx" class="relative flex-shrink-0 group/item">
                 <div class="w-14 h-14 bg-gray-100 rounded-lg border border-gray-200 overflow-hidden">
                   <div class="w-full h-full flex items-center justify-center text-[10px] text-gray-400 bg-gray-50 font-bold">
                     {{ item.product_name.substring(0, 2) }}
                   </div>
                 </div>
                 <span class="absolute -bottom-2 -right-2 bg-white text-[10px] shadow border rounded-full px-1.5 py-0.5 text-gray-500">x{{item.quantity}}</span>
               </div>
               <div v-if="(order.items?.length || 0) > 4" class="w-14 h-14 bg-gray-50 rounded-lg border border-gray-200 border-dashed flex items-center justify-center text-xs text-gray-400 font-bold hover:bg-gray-100">
                 +{{ order.items.length - 4 }}
               </div>
             </div>

             <div class="text-right w-full sm:w-auto">
               <div class="text-xs text-gray-400 mb-1">共 {{ order.items?.length }} 种规格，合计 (含税)</div>
               <div class="text-2xl font-bold text-gray-900 font-mono">¥{{ Number(order.final_total_price).toLocaleString() }}</div>
               <div class="mt-2 text-xs text-indigo-600 font-medium hover:underline">查看详情 & 下载单据</div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <transition enter-active-class="transition duration-300 ease-out" enter-from-class="translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition duration-200 ease-in" leave-from-class="translate-x-0" leave-to-class="translate-x-full">
      <div v-if="selectedOrder" class="fixed inset-y-0 right-0 z-[100] w-full md:w-[600px] bg-white shadow-2xl flex flex-col">
        
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <div>
            <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              订单详情 #{{ selectedOrder.id }}
              <span class="text-xs font-normal px-2 py-0.5 rounded border" :class="getStatusClass(selectedOrder.status)">{{ formatStatus(selectedOrder.status) }}</span>
            </h2>
            <p class="text-xs text-gray-500 mt-1">下单时间: {{ new Date(selectedOrder.created_at).toLocaleString() }}</p>
          </div>
          <button @click="closeDetail" class="text-gray-400 hover:text-gray-700 bg-white border border-gray-200 p-2 rounded-full hover:shadow-sm transition-all">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-8 bg-white">
          
          <div class="grid grid-cols-2 gap-3">
            <button @click="downloadInvoice" class="flex items-center justify-center gap-2 px-4 py-3 bg-white border border-gray-300 rounded-xl text-sm font-bold text-gray-700 hover:bg-gray-50 hover:border-indigo-300 transition-colors shadow-sm">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
              下载合同/发票
            </button>
            <button @click="reorderItems" class="flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-xl text-sm font-bold hover:bg-indigo-700 transition-colors shadow-md shadow-indigo-200">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              再次购买 (Reorder)
            </button>
          </div>

          <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              收货工地信息
            </h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">联系人:</span>
                <span class="font-bold text-gray-900">{{ selectedOrder.contact_name || '陈经理' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">联系电话:</span>
                <span class="font-mono font-bold text-gray-900">{{ selectedOrder.contact_phone || '012-***-***' }}</span>
              </div>
              <div class="flex justify-between items-start">
                <span class="text-gray-500 shrink-0">工地地址:</span>
                <span class="text-gray-900 text-right">{{ selectedOrder.shipping_address || '金边市堆谷区俄罗斯大道...' }}</span>
              </div>
            </div>
          </div>

          <div v-if="['delivering', 'completed'].includes(selectedOrder.status)">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">物流配送状态</h3>
            
            <div v-if="selectedOrder.shipping_method !== 'third_party'" class="border border-gray-200 rounded-xl overflow-hidden">
              <div class="bg-blue-50 p-3 border-b border-blue-100 flex justify-between items-center">
                <span class="text-xs font-bold text-blue-800 flex items-center">
                  <span class="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
                  厂商专车直送
                </span>
                <span class="text-[10px] text-blue-600">预计今日送达</span>
              </div>
              
              <div class="p-4 bg-white flex items-center gap-4 border-b border-gray-100">
                <div class="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-500">
                  <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                </div>
                <div class="flex-1">
                  <div class="font-bold text-gray-900 text-sm">司机: 张师傅</div>
                  <div class="text-xs text-gray-500">车牌: 2A-8821 (金边)</div>
                </div>
                <a href="tel:012345678" class="bg-green-100 text-green-700 p-2 rounded-full hover:bg-green-200 transition-colors">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                </a>
              </div>

              <div id="map" class="h-48 w-full bg-gray-100 relative">
                 <div v-if="!mapLoaded" class="absolute inset-0 flex items-center justify-center text-gray-400 text-xs">正在定位车辆...</div>
              </div>
            </div>

            <div v-else class="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <div class="flex justify-between items-center mb-2">
                <span class="font-bold text-gray-900">J&T 极兔速递</span>
                <span class="font-mono text-sm text-gray-600 select-all bg-white px-2 py-0.5 rounded border">8829102931</span>
              </div>
              <p class="text-xs text-gray-500">最新轨迹: 包裹已到达 [金边堆谷分拨中心]，派送员正在派送中...</p>
            </div>
          </div>

          <div>
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">采购清单明细</h3>
            <div class="border border-gray-200 rounded-xl overflow-hidden">
              <table class="min-w-full text-sm">
                <thead class="bg-gray-50 text-xs uppercase text-gray-500 font-medium">
                  <tr>
                    <th class="px-4 py-3 text-left">品名/规格</th>
                    <th class="px-4 py-3 text-center">数量</th>
                    <th class="px-4 py-3 text-right">小计</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in selectedOrder.items" :key="item.id" class="bg-white">
                    <td class="px-4 py-3">
                      <div class="font-bold text-gray-900 text-sm">{{ item.product_name }}</div>
                      <div class="text-xs text-gray-500 mt-0.5">{{ item.spec || item.product_spec }} <span class="mx-1">|</span> {{ item.color || '默认' }}</div>
                    </td>
                    <td class="px-4 py-3 text-center text-gray-600 font-mono">x{{ item.quantity }}</td>
                    <td class="px-4 py-3 text-right font-bold text-gray-900 font-mono">¥{{ item.subtotal }}</td>
                  </tr>
                </tbody>
                <tfoot class="bg-gray-50">
                  <tr>
                    <td colspan="2" class="px-4 py-3 text-right text-gray-500 text-xs">运费</td>
                    <td class="px-4 py-3 text-right font-mono text-gray-700">¥0.00</td>
                  </tr>
                  <tr>
                    <td colspan="2" class="px-4 py-3 text-right font-bold text-gray-900">实付总额</td>
                    <td class="px-4 py-3 text-right font-mono font-black text-orange-600 text-lg">¥{{ selectedOrder.final_total_price }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <div v-if="selectedOrder.delivery_photo_url" class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center">
              <svg class="w-4 h-4 mr-1 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              电子回单 (POD)
            </h3>
            <div class="relative group overflow-hidden rounded-lg border border-gray-300">
              <img :src="selectedOrder.delivery_photo_url" class="w-full h-48 object-cover cursor-zoom-in hover:scale-105 transition-transform duration-500" onclick="window.open(this.src)">
              <div class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-[10px] p-1 text-center backdrop-blur-sm">
                点击查看大图
              </div>
            </div>
          </div>

        </div>
        
        <div class="p-4 border-t border-gray-200 bg-white">
          <button @click="closeDetail" class="w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl transition-colors">
            关闭详情
          </button>
        </div>

      </div>
    </transition>

    <transition enter-active-class="transition-opacity duration-300" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition-opacity duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="selectedOrder" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[90]" @click="closeDetail"></div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import api from '../api/axios';
import { useCart } from '../composables/useCart'; // 引入购物车逻辑
import { useRouter } from 'vue-router';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// 修复 Leaflet 图标
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
const mapLoaded = ref(false);
const { addToCart } = useCart();
const router = useRouter();

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
  // 仅在配送中且自主配送时初始化地图
  if (['delivering'].includes(order.status) && order.shipping_method !== 'third_party') {
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

// --- 功能函数 ---

// 1. 再来一单 (Reorder)
const reorderItems = async () => {
  if (!selectedOrder.value) return;
  if (!confirm('确定将该订单的所有商品重新加入购物车吗？')) return;
  
  try {
    // 遍历订单项加入购物车
    for (const item of selectedOrder.value.items) {
      // 注意：这里假设 item 包含 variant_id，如果没有可能需要后端配合调整
      await addToCart(item.variant_id || item.product_id, item.quantity);
    }
    closeDetail();
    router.push('/products'); // 跳转去购物车/产品页
  } catch (e) {
    alert('操作失败，部分商品可能已下架');
  }
};

// 2. 下载单据 (模拟)
const downloadInvoice = () => {
  alert("正在生成 PDF 合同与发票...\n(此功能需对接后端 PDF 生成服务)");
  // 实际逻辑：window.open(api.defaults.baseURL + `/orders/${selectedOrder.value.id}/invoice_pdf`);
};

// --- 地图逻辑 ---
const initMap = (order) => {
  const container = document.getElementById('map');
  if (!container) return;

  const lat = order.driver_lat || 11.5564; 
  const lng = order.driver_lng || 104.9282;

  mapInstance = L.map('map', { zoomControl: false }).setView([lat, lng], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '' }).addTo(mapInstance);
  markerInstance = L.marker([lat, lng]).addTo(mapInstance).bindPopup('配送车辆位置').openPopup();
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
  } catch (e) { console.error("GPS同步失败", e); }
};

// --- 状态样式 ---
const formatStatus = (s) => {
  const map = { pending_confirmation: '待确认', confirmed: '备货中', delivering: '配送中', completed: '已送达', cancelled: '已取消' };
  return map[s] || s;
};

const getStatusClass = (s) => {
  const map = {
    pending_confirmation: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    confirmed: 'bg-blue-50 text-blue-700 border-blue-200',
    delivering: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    completed: 'bg-green-50 text-green-700 border-green-200',
    cancelled: 'bg-gray-100 text-gray-500 border-gray-200'
  };
  return map[s] || 'bg-gray-50 text-gray-700 border-gray-200';
};

const getStatusDotClass = (s) => {
  const map = { pending_confirmation: 'bg-yellow-500', confirmed: 'bg-blue-500', delivering: 'bg-indigo-500 animate-pulse', completed: 'bg-green-500', cancelled: 'bg-gray-400' };
  return map[s] || 'bg-gray-400';
};

onMounted(fetchMyOrders);
onUnmounted(() => { if (mapInterval) clearInterval(mapInterval); });
</script>

<style scoped>
/* 自定义滚动条，适应侧边栏弹窗 */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c7c7c7; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #a0a0a0; }

.dashed-border {
  background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='12' ry='12' stroke='%23E5E7EBFF' stroke-width='2' stroke-dasharray='8%2c8' stroke-dashoffset='0' stroke-linecap='square'/%3e%3c/svg%3e");
  border: none;
}
</style>