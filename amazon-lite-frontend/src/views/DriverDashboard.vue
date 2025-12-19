<template>
  <div class="min-h-screen bg-gray-100 pb-24">
    <div class="bg-indigo-600 text-white p-4 shadow-md sticky top-0 z-20">
      <div class="flex justify-between items-center">
        <h1 class="text-lg font-bold flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          派送员工作台
        </h1>
        <button @click="logout" class="text-xs bg-indigo-800/50 hover:bg-indigo-800 px-3 py-1.5 rounded transition-colors">退出</button>
      </div>
      
      <div class="mt-3 flex justify-between items-end text-xs opacity-90 bg-indigo-700/30 p-2 rounded-lg">
        <div>
          <div class="flex items-center mb-1">
            <span class="relative flex h-2 w-2 mr-2">
              <span v-if="isTracking" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2" :class="isTracking ? 'bg-green-400' : 'bg-red-400'"></span>
            </span>
            <span class="font-mono">{{ lastUpdateTime || '等待定位...' }}</span>
          </div>
          <div>精度: {{ accuracy }} 米</div>
        </div>
        <div class="text-right">
          <div v-if="wakeLock" class="text-green-300">⚡ 屏幕常亮中</div>
          <div v-else class="text-yellow-300">⚠️ 请保持屏幕开启</div>
        </div>
      </div>
    </div>

    <div class="p-4 space-y-4">
      <div v-if="loading" class="text-center py-10 text-gray-500">正在加载任务...</div>
      
      <div v-else-if="tasks.length === 0" class="flex flex-col items-center justify-center py-16 text-gray-400">
        <svg class="w-16 h-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
        <p>暂无待派送任务</p>
        <button @click="fetchTasks" class="mt-4 text-indigo-600 text-sm font-bold">刷新列表</button>
      </div>

      <div v-else v-for="task in tasks" :key="task.id" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 relative overflow-hidden">
        <div class="absolute top-0 right-0 -mt-2 -mr-2 w-16 h-16 bg-indigo-50 rounded-full blur-xl"></div>

        <div class="flex justify-between items-start mb-4 relative z-10">
          <div>
            <div class="flex items-center">
              <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-0.5 rounded mr-2">#{{ task.id }}</span>
              <span class="text-sm text-gray-500">{{ new Date(task.created_at).toLocaleTimeString() }}</span>
            </div>
            <p class="font-bold text-gray-900 mt-1">{{ task.user_email }}</p>
          </div>
          <a href="tel:10086" class="bg-green-50 text-green-600 w-10 h-10 rounded-full flex items-center justify-center shadow-sm hover:bg-green-100 transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
          </a>
        </div>

        <div class="border-t border-dashed border-gray-200 py-3 relative z-10">
          <ul class="text-sm space-y-1">
            <li v-for="item in task.items" :key="item.id" class="flex justify-between">
              <span class="text-gray-700 truncate w-3/4">{{ item.product_name }}</span>
              <span class="text-gray-900 font-medium">x{{ item.quantity }}</span>
            </li>
          </ul>
        </div>

        <div class="mt-2 bg-gray-50 p-3 rounded-lg border border-gray-100 relative z-10">
          <label class="flex items-center justify-center w-full h-12 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors" :class="{'border-green-400 bg-green-50': task.uploadFile}">
            <input type="file" accept="image/*" capture="environment" class="hidden" @change="(e) => handleFileSelect(e, task)">
            <span v-if="!task.uploadFile" class="text-xs text-gray-500 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              点击拍摄到货凭证
            </span>
            <span v-else class="text-xs text-green-600 font-bold flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
              照片已就绪 (点击重拍)
            </span>
          </label>
          
          <button 
            @click="completeTask(task)" 
            :disabled="!task.uploadFile"
            class="mt-3 w-full bg-gray-900 text-white py-3 rounded-lg font-bold shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100 flex justify-center items-center"
          >
            确认送达
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

// 1. 获取任务
const fetchTasks = async () => {
  loading.value = true;
  try {
    const res = await api.get('/orders/driver/tasks');
    // 保留之前已选的文件（如果有），防止刷新列表时丢失
    const oldTasksMap = new Map(tasks.value.map(t => [t.id, t.uploadFile]));
    tasks.value = res.data.map(t => ({ 
      ...t, 
      uploadFile: oldTasksMap.get(t.id) || null 
    }));
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

// 2. 发送位置的核心函数 (单次)
const sendLocation = () => {
  if (!navigator.geolocation) return;

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      isTracking.value = true;
      const { latitude, longitude, accuracy: acc } = position.coords;
      
      accuracy.value = Math.round(acc);
      lastUpdateTime.value = new Date().toLocaleTimeString();

      // 只更新那些状态是 'delivering' 的订单
      const activeTasks = tasks.value.filter(t => t.status === 'delivering' || true); // 简化：所有任务都更新，后端会过滤

      if (activeTasks.length > 0) {
        for (const task of activeTasks) {
          try {
            // 【关键修改】使用 POST Body 发送数据，而不是 URL params
            await api.post(`/orders/${task.id}/location`, { 
              lat: latitude, 
              lng: longitude 
            });
          } catch (e) { console.error('位置上传失败', e); }
        }
      }
    },
    (err) => {
      console.error('定位失败', err);
      isTracking.value = false;
      lastUpdateTime.value = '定位失败';
    },
    // 【关键修改】强制高精度，超时时间设为10秒
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
};

// 3. 申请屏幕常亮 (防止手机锁屏导致JS停止)
const requestWakeLock = async () => {
  if ('wakeLock' in navigator) {
    try {
      wakeLock.value = await navigator.wakeLock.request('screen');
      console.log('屏幕常亮已开启');
    } catch (err) {
      console.error(`${err.name}, ${err.message}`);
    }
  }
};

// 4. 处理图片
const handleFileSelect = (event, task) => {
  const file = event.target.files[0];
  if (file) task.uploadFile = file;
};

// 5. 完成订单
const completeTask = async (task) => {
  if (!task.uploadFile) return alert('请先拍摄到货照片');
  if (!confirm(`确认订单 #${task.id} 已安全送达？`)) return;

  try {
    const formData = new FormData();
    formData.append('file', task.uploadFile);
    await api.post(`/orders/${task.id}/complete`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert('任务完成，辛苦了！');
    fetchTasks();
  } catch (e) { 
    alert('提交失败: ' + (e.response?.data?.detail || '未知错误')); 
  }
};

const logout = () => {
  authLogout();
  router.push('/login');
};

onMounted(() => {
  fetchTasks();
  
  // 1. 立即获取一次位置
  sendLocation();
  
  // 2. 开启轮询：每 5 秒强制获取并上传一次
  // 相比 watchPosition，setInterval 在手机浏览器中更稳定
  intervalId = setInterval(() => {
    sendLocation();
    // 顺便静默刷新任务列表，查看有没有新指派的单
    // fetchTasks(); // 如果担心流量可以注释掉这行
  }, 5000);

  // 3. 申请屏幕常亮
  requestWakeLock();
  
  // 监听可见性变化，如果切回来，重新申请锁
  document.addEventListener('visibilitychange', async () => {
    if (wakeLock.value !== null && document.visibilityState === 'visible') {
      requestWakeLock();
    }
  });
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
  if (wakeLock.value) wakeLock.value.release();
});
</script>