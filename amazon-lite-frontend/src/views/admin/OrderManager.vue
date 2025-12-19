<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">

    <div class="p-4 md:p-6 border-b border-gray-100 flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-blue-600 rounded-full mr-3"></span>
        订单全流程管理
      </h2>
      <div class="flex-1 max-w-sm mx-4"> <input v-model="searchQuery" @keyup.enter="fetchOrders" type="text"
          placeholder="输入订单号或邮箱回车搜索..."
          class="w-full px-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none">
      </div>
      <button @click="fetchOrders" class="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>


    <div class="flex-1 overflow-auto bg-gray-50 md:bg-white">

      <table class="hidden md:table min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0 z-10">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">订单号/时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">客户</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">物流/凭证</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase w-64">流程操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-if="loading">
            <td colspan="5" class="p-10 text-center text-gray-500">加载中...</td>
          </tr>
          <tr v-else v-for="order in orders" :key="order.id" class="hover:bg-gray-50 transition-colors">

            <td class="px-6 py-4">
              <div class="font-bold text-gray-900">#{{ order.id }}</div>
              <div class="text-xs text-gray-500">{{ new Date(order.created_at).toLocaleString() }}</div>
            </td>

            <td class="px-6 py-4">
              <div class="flex flex-col">
                <span class="text-sm text-gray-700 font-bold">{{ order.user_email }}</span>
                <span class="text-xs text-gray-400">¥{{ order.final_total_price }}</span>
              </div>
            </td>

            <td class="px-6 py-4">
              <span class="px-2 py-1 text-xs rounded-full font-bold border" :class="getStatusClass(order.status)">
                {{ formatStatus(order.status) }}
              </span>
            </td>

            <td class="px-6 py-4">
              <div v-if="order.driver_id" class="flex items-center text-xs text-indigo-600 mb-1" title="派送员">
                <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>已指派</span>
              </div>
              <div v-else-if="order.status === 'delivering'" class="text-xs text-gray-400">派送中</div>

              <div v-if="order.delivery_photo_url" class="flex items-center text-xs text-green-600" title="已上传凭证">
                <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                有到货图
              </div>
            </td>

            <td class="px-6 py-4 text-right space-x-2">
              <button @click="openDetail(order)"
                class="text-gray-500 hover:text-blue-600 text-sm font-medium">详情</button>

              <template v-if="order.status === 'pending_confirmation'">
                <button @click="handleConfirm(order)"
                  class="bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700">确认</button>
              </template>

              <template v-if="order.status === 'confirmed'">
                <button @click="openShipModal(order)"
                  class="bg-indigo-600 text-white px-2 py-1 rounded text-xs hover:bg-indigo-700">指派发货</button>
              </template>

              <template v-if="order.status === 'delivering'">
                <button @click="openCompleteModal(order)"
                  class="bg-gray-800 text-white px-2 py-1 rounded text-xs hover:bg-gray-900">强制完成</button>
              </template>

              <template v-if="!['completed', 'cancelled'].includes(order.status)">
                <button @click="handleCancel(order)" class="text-red-400 hover:text-red-600 text-xs ml-2">作废</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="md:hidden p-4 space-y-4">
        <div v-if="loading" class="text-center py-10 text-gray-400">加载中...</div>

        <div v-else v-for="order in orders" :key="order.id"
          class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

          <div class="px-4 py-3 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
            <span class="font-mono font-bold text-gray-800">#{{ order.id }}</span>
            <span class="px-2 py-0.5 text-xs rounded-full font-bold border" :class="getStatusClass(order.status)">
              {{ formatStatus(order.status) }}
            </span>
          </div>

          <div class="p-4">
            <div class="flex justify-between items-start mb-3">
              <div class="flex-1 mr-2">
                <p class="text-[10px] text-gray-400 uppercase">客户邮箱</p>
                <p class="text-sm font-medium text-gray-800 break-all">{{ order.user_email }}</p>
              </div>
              <div class="text-right">
                <p class="text-[10px] text-gray-400 uppercase">总金额</p>
                <p class="text-lg font-black text-gray-900">¥{{ order.final_total_price }}</p>
              </div>
            </div>

            <div class="flex flex-wrap gap-2 text-xs text-gray-500 mb-4">
              <div class="flex items-center">
                <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ new Date(order.created_at).toLocaleDateString() }}
              </div>

              <div v-if="order.driver_id"
                class="flex items-center text-indigo-600 font-bold bg-indigo-50 px-1.5 py-0.5 rounded">
                <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                已派单
              </div>

              <div v-if="order.delivery_photo_url"
                class="flex items-center text-green-600 font-bold bg-green-50 px-1.5 py-0.5 rounded">
                <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                有回单
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2 border-t border-gray-100 pt-3">
              <button @click="openDetail(order)"
                class="py-2 bg-gray-50 text-gray-600 rounded text-sm font-bold hover:bg-gray-100">
                查看详情
              </button>

              <button v-if="order.status === 'pending_confirmation'" @click="handleConfirm(order)"
                class="py-2 bg-green-600 text-white rounded text-sm font-bold hover:bg-green-700 shadow-sm">
                确认订单
              </button>

              <button v-if="order.status === 'confirmed'" @click="openShipModal(order)"
                class="py-2 bg-indigo-600 text-white rounded text-sm font-bold hover:bg-indigo-700 shadow-sm">
                指派发货
              </button>

              <button v-if="order.status === 'delivering'" @click="openCompleteModal(order)"
                class="py-2 bg-gray-800 text-white rounded text-sm font-bold hover:bg-gray-900 shadow-sm">
                强制完成
              </button>

              <button
                v-if="!['completed', 'cancelled', 'pending_confirmation', 'confirmed', 'delivering'].includes(order.status)"
                class="hidden"></button>

              <button
                v-if="!['completed', 'cancelled'].includes(order.status) && order.status !== 'pending_confirmation' && order.status !== 'confirmed' && order.status !== 'delivering'"
                @click="handleCancel(order)"
                class="py-2 border border-red-200 text-red-500 rounded text-sm font-bold hover:bg-red-50">
                作废订单
              </button>
            </div>

            <div v-if="!['completed', 'cancelled'].includes(order.status)" class="mt-2 text-center">
              <button @click="handleCancel(order)"
                class="text-xs text-red-400 underline decoration-red-200">作废此订单</button>
            </div>

          </div>
        </div>
      </div>
    </div>

    <div v-if="showShipDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
        <h3 class="text-lg font-bold mb-4">指派派送员发货</h3>

        <div v-if="drivers.length === 0" class="text-red-500 text-xs mb-4 p-2 bg-red-50 rounded">
          提示：暂无可用派送员，请先在用户管理中创建角色为 "driver" 的用户。
        </div>

        <label class="block text-sm text-gray-700 mb-2">选择派送员</label>
        <select v-model="shipForm.driverId"
          class="w-full border border-gray-300 rounded p-2 text-sm mb-4 bg-white outline-none focus:ring-2 focus:ring-indigo-500">
          <option :value="null">-- 请选择 --</option>
          <option v-for="d in drivers" :key="d.id" :value="d.id">
            {{ d.email }} ({{ d.username || '师傅' }})
          </option>
        </select>

        <div class="flex justify-end gap-2">
          <button @click="showShipDialog = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">取消</button>
          <button @click="submitShip" :disabled="!shipForm.driverId"
            class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed">
            确认指派
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCompleteDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
        <h3 class="text-lg font-bold mb-4">确认送达</h3>
        <p class="text-xs text-gray-500 mb-4">管理员手动确认送达，通常此步骤由派送员在手机端完成。</p>

        <label class="block text-sm text-gray-700 mb-2">补充到货照片 (可选)</label>
        <input type="file" ref="fileInput" accept="image/*"
          class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 mb-4">

        <div class="flex justify-end gap-2">
          <button @click="showCompleteDialog = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">取消</button>
          <button @click="submitComplete" class="px-4 py-2 bg-gray-900 text-white rounded hover:bg-black">确认完成</button>
        </div>
      </div>
    </div>

    <div v-if="viewingOrder"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h3 class="text-lg font-bold">订单详情 #{{ viewingOrder.id }}</h3>
          <button @click="viewingOrder = null" class="text-gray-400 hover:text-gray-600 p-2">✕</button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div class="mb-4">
            <h4 class="font-bold text-gray-800 mb-2">商品清单</h4>
            <div class="border rounded-lg overflow-hidden">
              <table class="min-w-full">
                <thead class="bg-gray-50 text-xs uppercase text-gray-500">
                  <tr>
                    <th class="px-4 py-2 text-left">商品</th>
                    <th class="px-4 py-2 text-right">数量</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                  <tr v-for="item in viewingOrder.items" :key="item.id">
                    <td class="px-4 py-2">{{ item.product_name }}</td>
                    <td class="px-4 py-2 text-right">x{{ item.quantity }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="viewingOrder.delivery_photo_url" class="border p-4 rounded-lg bg-gray-50">
            <p class="text-sm font-bold mb-2">到货凭证：</p>
            <img :src="viewingOrder.delivery_photo_url" class="max-w-full md:max-w-xs rounded border shadow-sm"
              alt="送达照片">
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api/axios';

const orders = ref([]);
const drivers = ref([]); // 派送员列表
const loading = ref(false);
const viewingOrder = ref(null);

// 弹窗状态
const showShipDialog = ref(false);
const showCompleteDialog = ref(false);
const activeOrderId = ref(null);
const shipForm = reactive({ driverId: null }); // 修改为 driverId
const fileInput = ref(null);

const searchQuery = ref(''); // 1. 新增变量

const fetchOrders = async () => {
  loading.value = true;
  try {
    // 2. 修改 API 调用，传入 q 参数
    const res = await api.get('/orders/', {
      params: { q: searchQuery.value || undefined }
    });
    orders.value = res.data;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};
// 获取派送员列表 (需要后端支持 GET /users/drivers)
const fetchDrivers = async () => {
  try {
    const res = await api.get('/users/drivers');
    drivers.value = res.data;
  } catch (e) { console.error("获取派送员失败", e); }
};

const formatStatus = (s) => {
  const map = { pending_confirmation: '待确认', confirmed: '已确认', delivering: '派送中', completed: '已送达', cancelled: '已作废' };
  return map[s] || s;
};

const getStatusClass = (s) => {
  const map = {
    pending_confirmation: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    confirmed: 'bg-green-50 text-green-700 border-green-200',
    delivering: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    completed: 'bg-gray-800 text-white border-gray-900',
    cancelled: 'bg-gray-100 text-gray-400 border-gray-200 line-through'
  };
  return map[s] || 'bg-gray-100 text-gray-500';
};

// 1. 确认订单
const handleConfirm = async (order) => {
  if (!confirm('确定确认订单并扣减库存吗？')) return;
  try { await api.patch(`/orders/${order.id}/confirm`); fetchOrders(); } catch (e) { alert('失败'); }
};

// 2. 发货逻辑 (打开弹窗并获取司机)
const openShipModal = (order) => {
  activeOrderId.value = order.id;
  shipForm.driverId = null;
  showShipDialog.value = true;
  fetchDrivers(); // 获取最新司机列表
};

// 提交指派
const submitShip = async () => {
  if (!shipForm.driverId) return;
  try {
    // ✅ 修复后的写法 (把对象作为第二个参数，即 Request Body 发送)
    await api.patch(`/orders/${activeOrderId.value}/assign`, {
      driver_id: shipForm.driverId
    });

    showShipDialog.value = false;
    fetchOrders();
    alert('指派成功，订单已进入派送状态');
  } catch (e) {
    console.error(e);
    // 加上详细的错误提示，方便调试
    alert('指派失败: ' + (e.response?.data?.detail || '未知错误'));
  }
};

// 3. 完成逻辑 (上传图片)
const openCompleteModal = (order) => {
  activeOrderId.value = order.id;
  showCompleteDialog.value = true;
};
const submitComplete = async () => {
  try {
    const formData = new FormData();
    if (fileInput.value && fileInput.value.files[0]) {
      formData.append('file', fileInput.value.files[0]);
    }
    await api.post(`/orders/${activeOrderId.value}/complete`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    showCompleteDialog.value = false;
    fetchOrders();
  } catch (e) { alert('操作失败'); }
};

// 4. 作废逻辑
const handleCancel = async (order) => {
  if (!confirm('确定作废吗？库存将自动返还。')) return;
  try { await api.patch(`/orders/${order.id}/cancel`); fetchOrders(); } catch (e) { alert('失败'); }
};

const openDetail = (order) => { viewingOrder.value = order; };

onMounted(fetchOrders);
</script>