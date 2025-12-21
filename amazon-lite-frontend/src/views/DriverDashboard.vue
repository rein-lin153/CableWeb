<template>
  <div class="min-h-screen bg-gray-900 pb-24 font-sans text-gray-100">
    <div class="bg-gray-800 border-b border-gray-700 p-4 sticky top-0 z-30 shadow-xl">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-lg font-bold flex items-center text-white">
          <div class="w-8 h-8 rounded-lg bg-orange-600 flex items-center justify-center mr-3 shadow-lg shadow-orange-600/20">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          配送任务终端
        </h1>
        <button @click="logout" class="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1.5 rounded-lg transition-colors border border-gray-600">
          下班/退出
        </button>
      </div>
      
      <div class="flex justify-between items-center text-xs bg-black/30 p-3 rounded-xl border border-gray-700/50 backdrop-blur-sm">
        <div class="flex items-center gap-3">
          <div class="relative flex h-3 w-3">
            <span v-if="isTracking" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3" :class="isTracking ? 'bg-green-500' : 'bg-red-500'"></span>
          </div>
          <div>
            <div class="font-mono text-gray-300">{{ lastUpdateTime || '等待 GPS 信号...' }}</div>
            <div class="text-[10px] text-gray-500">精度范围: ±{{ accuracy }}米</div>
          </div>
        </div>
        <div class="text-right">
          <div v-if="wakeLock" class="text-green-400 font-bold flex items-center gap-1">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            屏幕保持常亮
          </div>
          <div v-else class="text-yellow-400 flex items-center gap-1 animate-pulse">
            ⚠️ 请点击页面激活常亮
          </div>
        </div>
      </div>
    </div>

    <div class="p-4 space-y-6">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-4"></div>
        <span class="text-gray-500 text-sm">正在同步任务列表...</span>
      </div>
      
      <div v-else-if="tasks.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-500">
        <div class="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mb-4">
          <svg class="w-10 h-10 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
        </div>
        <p class="font-medium">暂无待配送任务</p>
        <p class="text-xs text-gray-600 mt-2">金边市区如有新单将自动推送</p>
        <button @click="fetchTasks" class="mt-6 px-6 py-2 bg-gray-800 rounded-full text-sm font-bold text-gray-300 hover:bg-gray-700">刷新列表</button>
      </div>

      <div v-else v-for="task in tasks" :key="task.id" class="bg-gray-800 rounded-2xl p-5 shadow-lg border border-gray-700 relative overflow-hidden group">
        <div class="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

        <div class="flex justify-between items-start mb-5 relative z-10">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="bg-orange-900/50 text-orange-400 border border-orange-500/30 text-xs font-bold px-2 py-0.5 rounded">#{{ task.id }}</span>
              <span class="bg-blue-900/30 text-blue-400 border border-blue-500/30 text-xs font-bold px-2 py-0.5 rounded">金边专送</span>
            </div>
            <p class="font-bold text-lg text-white mt-2">{{ task.contact_name || '客户' }} <span class="text-gray-400 text-sm font-normal">{{ task.contact_phone }}</span></p>
            <p class="text-gray-400 text-xs mt-1 max-w-[80%] truncate">{{ task.shipping_address || '金边市堆谷区...' }}</p>
          </div>
          <div class="flex flex-col gap-2">
            <a :href="`tel:${task.contact_phone}`" class="bg-green-600 text-white w-10 h-10 rounded-xl flex items-center justify-center shadow-lg hover:bg-green-500 transition-all active:scale-95">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
            </a>
            <a :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(task.shipping_address)}`" target="_blank" class="bg-blue-600 text-white w-10 h-10 rounded-xl flex items-center justify-center shadow-lg hover:bg-blue-500 transition-all active:scale-95">
               <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </a>
          </div>
        </div>

        <div class="bg-gray-900/50 rounded-xl p-4 mb-5 border border-gray-700">
          <ul class="text-sm space-y-2">
            <li v-for="item in task.items" :key="item.id" class="flex justify-between items-center">
              <span class="text-gray-300 truncate w-3/4">{{ item.product_name }}</span>
              <span class="text-white font-mono font-bold">x{{ item.quantity }}</span>
            </li>
          </ul>
        </div>

        <div class="relative z-10">
          <label class="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-gray-600 rounded-xl cursor-pointer hover:bg-gray-700/50 transition-all mb-3 group-hover:border-gray-500" :class="{'border-green-500/50 bg-green-900/20': task.uploadFile}">
            <input type="file" accept="image/*" capture="environment" class="hidden" @change="(e) => handleFileSelect(e, task)">
            
            <div v-if="!task.uploadFile" class="text-center">
              <svg class="w-6 h-6 mx-auto text-gray-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              <span class="text-xs text-gray-400">拍摄现场/签收单照片</span>
            </div>
            <div v-else class="text-center">
              <svg class="w-6 h-6 mx-auto text-green-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
              <span class="text-xs text-green-400 font-bold">照片已就绪 (点击重拍)</span>
            </div>
          </label>
          
          <button 
            @click="completeTask(task)" 
            :disabled="!task.uploadFile"
            class="w-full bg-orange-600 hover:bg-orange-500 disabled:bg-gray-700 disabled:text-gray-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg transition-all active:scale-95 flex justify-center items-center"
          >
            确认送达 (Complete)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../api/axios';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const tasks = ref([]);
const loading = ref(true);
const router = useRouter();
const { logout: authLogout } = useAuth();

// 状态监控
const lastUpdateTime = ref('');
const accuracy = ref(0);
const isTracking = ref(false);
const wakeLock = ref(null);
let intervalId = null;

const fetchTasks = async () => {
  loading.value = true;
  try {
    const res = await api.get('/orders/driver/tasks');
    // 保留文件缓存逻辑
    const oldTasksMap = new Map(tasks.value.map(t => [t.id, t.uploadFile]));
    tasks.value = res.data.map(t => ({ 
      ...t, 
      uploadFile: oldTasksMap.get(t.id) || null 
    }));
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

const sendLocation = () => {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      isTracking.value = true;
      const { latitude, longitude, accuracy: acc } = position.coords;
      accuracy.value = Math.round(acc);
      lastUpdateTime.value = new Date().toLocaleTimeString('en-GB');

      // 仅当有任务时才上传位置
      const activeTasks = tasks.value; 
      if (activeTasks.length > 0) {
        // 批量通知所有正在进行的订单，或者只通知后端“司机”位置
        // 这里假设是基于订单维度的更新
        for (const task of activeTasks) {
          try {
            await api.post(`/orders/${task.id}/location`, { lat: latitude, lng: longitude });
          } catch (e) { console.error('位置上传失败', e); }
        }
      }
    },
    (err) => {
      console.error('定位失败', err);
      isTracking.value = false;
      lastUpdateTime.value = 'GPS丢失';
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
};

const requestWakeLock = async () => {
  if ('wakeLock' in navigator) {
    try {
      wakeLock.value = await navigator.wakeLock.request('screen');
    } catch (err) { console.error(err); }
  }
};

const handleFileSelect = (event, task) => {
  const file = event.target.files[0];
  if (file) task.uploadFile = file;
};

const completeTask = async (task) => {
  if (!task.uploadFile) return;
  if (!confirm(`确认送达 #${task.id} ？`)) return;

  try {
    const formData = new FormData();
    formData.append('file', task.uploadFile);
    await api.post(`/orders/${task.id}/complete`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    alert('✅ 送达成功');
    fetchTasks();
  } catch (e) { alert('提交失败: ' + (e.response?.data?.detail || '未知错误')); }
};

const logout = () => {
  authLogout();
  router.push('/login');
};

onMounted(() => {
  fetchTasks();
  sendLocation();
  // 缩短轮询间隔，提升“看着车在地图上跑”的体验
  intervalId = setInterval(() => { sendLocation(); }, 5000); 
  requestWakeLock();
  document.addEventListener('visibilitychange', async () => {
    if (wakeLock.value !== null && document.visibilityState === 'visible') requestWakeLock();
  });
  // 点击页面任意位置尝试激活 WakeLock (应对浏览器限制)
  document.addEventListener('click', requestWakeLock, { once: true });
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
  if (wakeLock.value) wakeLock.value.release();
});
</script>