<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeModal"></div>
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        
        <div class="bg-indigo-600 px-4 py-3 sm:px-6 flex justify-between items-center">
          <h3 class="text-lg leading-6 font-medium text-white">
            {{ isEditMode ? '🛠️ 编辑复杂规格' : '💰 新增多维核算' }}
          </h3>
          <button @click="closeModal" class="text-indigo-200 hover:text-white">✕</button>
        </div>

        <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4 bg-gray-50 max-h-[70vh] overflow-y-auto">
          
          <div class="grid grid-cols-2 gap-4 mb-4">
             <div>
               <label class="lbl-mini">规格名称 (如 YJV 3*10+1*6)</label>
               <input v-model="form.spec_name" type="text" class="input-std" placeholder="必填">
             </div>
             <div>
               <label class="lbl-mini">分类 (影响加工费计算)</label>
               <input v-model="form.category" list="cat-options" type="text" class="input-std" placeholder="如 BVR / RVV">
               <datalist id="cat-options">
                 <option value="BV"></option>
                 <option value="BVR"></option>
                 <option value="RVV"></option>
                 <option value="YJV"></option>
               </datalist>
             </div>
          </div>

          <div class="mb-4 bg-white p-4 rounded border border-gray-200 shadow-sm">
             <div class="flex justify-between items-center mb-2">
               <label class="lbl-mini font-bold text-gray-700">线芯结构 (Core Structure)</label>
               <select v-model="form.material" class="text-xs border rounded px-2 py-1 bg-indigo-50 text-indigo-700 font-bold outline-none">
                 <option value="Cu">🟤 铜 (Cu)</option>
                 <option value="Al">⚪ 铝 (Al)</option>
               </select>
             </div>

             <div v-for="(group, index) in form.core_structure" :key="index" class="flex gap-2 mb-2 items-end bg-gray-50 p-2 rounded">
               <div class="w-16">
                 <label class="text-[10px] text-gray-400">芯数</label>
                 <input v-model.number="group.cores" type="number" class="input-std text-center font-bold text-indigo-600">
               </div>
               <div class="flex items-center pb-2 text-gray-400">×</div>
               <div class="flex-1">
                 <label class="text-[10px] text-gray-400">每芯根数</label>
                 <input v-model.number="group.strands" type="number" class="input-std">
               </div>
               <div class="flex items-center pb-2 text-gray-400">×</div>
               <div class="flex-1">
                 <label class="text-[10px] text-gray-400">丝号(mm)</label>
                 <input v-model.number="group.gauge" type="number" step="0.01" class="input-std">
               </div>
               <button @click="removeGroup(index)" v-if="form.core_structure.length > 1" class="mb-1 p-2 text-red-400 hover:text-red-600">🗑️</button>
             </div>

             <button @click="addGroup" class="w-full py-2 border-2 border-dashed border-gray-300 rounded text-gray-500 text-xs hover:border-indigo-400 hover:text-indigo-600 transition">
               + 添加副线芯
             </button>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="lbl-mini">整卷实际总重 (kg)</label>
              <input v-model.number="form.total_weight" type="number" step="0.01" class="input-std" placeholder="称重重量">
            </div>
            <div>
              <label class="lbl-mini text-indigo-700 font-bold">实际米数 (m)</label>
              <input v-model.number="form.length" type="number" class="input-std bg-white border-indigo-300" placeholder="默认100">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4 border-t pt-4">
             <div class="col-span-1 relative">
               <label class="lbl-mini font-bold text-indigo-600 flex justify-between">
                 <span>导体单价 ($/kg)</span>
                 <span v-if="priceTip" class="text-[10px] text-green-600 font-normal">{{ priceTip }}</span>
               </label>
               <div class="flex gap-2">
                 <input v-model.number="form.copper_price" type="number" step="0.0001" class="input-std border-indigo-300">
                 <button 
                   @click="autoGetPrice" 
                   :disabled="calculating"
                   type="button"
                   class="mt-1 px-3 py-1 bg-yellow-500 hover:bg-yellow-600 text-white text-xs rounded shadow transition flex items-center whitespace-nowrap"
                   title="根据今日铜价和分类自动计算"
                 >
                   {{ calculating ? '...' : '⚡ 按今日铜价' }}
                 </button>
               </div>
             </div>
             
             <div class="grid grid-cols-2 gap-2">
               <div>
                 <label class="lbl-mini">非导体均价</label>
                 <input v-model.number="form.pvc_price" type="number" step="0.1" class="input-std">
               </div>
               <div>
                 <label class="lbl-mini">人工成本</label>
                 <input v-model.number="form.labor_cost" type="number" step="0.1" class="input-std">
               </div>
             </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4 mb-4">
             <div>
               <label class="lbl-mini">绝缘类型</label>
               <select v-model="form.insulation_type" class="input-std">
                 <option value="PVC">PVC</option>
                 <option value="XLPE">XLPE (交联)</option>
               </select>
             </div>
             <div>
               <label class="lbl-mini">备注</label>
               <input v-model="form.remark" class="input-std">
             </div>
          </div>

          <div class="bg-gray-800 text-white rounded-lg p-4 flex justify-between items-center">
            <div class="text-xs space-y-1 text-gray-300">
              <div>导体: <span class="text-yellow-400 font-bold">{{ preview.copper_weight }}</span> kg</div>
              <div>非导体: <span class="text-blue-300 font-bold">{{ preview.pvc_weight }}</span> kg</div>
            </div>
            <div class="text-right">
              <div class="text-xs text-gray-400 uppercase">Total Cost</div>
              <div class="text-3xl font-bold text-green-400">${{ preview.total_cost }}</div>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t border-gray-200">
          <button @click="handleSave" :disabled="loading" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700 sm:ml-3 sm:w-auto sm:text-sm">
            {{ loading ? '保存中...' : '保存记录' }}
          </button>
          <button @click="closeModal" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-gray-700 hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import axios from '../../api/axios';

const props = defineProps({
  isOpen: Boolean,
  editData: Object
});
const emit = defineEmits(['close', 'saved']);
const loading = ref(false);
const calculating = ref(false);
const priceTip = ref(''); // 显示行情提示
const isEditMode = computed(() => !!props.editData);

// 默认结构
const defaultGroup = { cores: 3, strands: 7, gauge: 1.0 };
const defaultForm = {
  spec_name: '',
  category: '',
  remark: '',
  material: 'Cu',
  insulation_type: 'PVC',
  core_structure: [ { ...defaultGroup } ], 
  total_weight: 0.0,
  length: 100.0,
  copper_price: 0.0, // 默认为0，等待计算
  pvc_price: 1.5,
  labor_cost: 0.5
};

const form = reactive(JSON.parse(JSON.stringify(defaultForm)));

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    priceTip.value = '';
    if (props.editData) {
      Object.assign(form, JSON.parse(JSON.stringify(props.editData)));
      if(!form.core_structure) form.core_structure = [{...defaultGroup}];
    } else {
      Object.assign(form, JSON.parse(JSON.stringify(defaultForm)));
    }
  }
});

// 🟢 [新增] 自动获取今日铜价
const autoGetPrice = async () => {
  if (form.material === 'Al') {
    alert("自动算价目前仅支持【铜】，铝价请手动输入。");
    return;
  }
  
  calculating.value = true;
  try {
    // 调用后端新接口
    const res = await axios.get('/admin/costs/calculate-unit-price', {
      params: { category: form.category }
    });
    
    // 填入价格
    form.copper_price = res.data.price;
    priceTip.value = `基于: ¥${res.data.market_cny} | 汇率: ${res.data.rate}`;
    
  } catch (e) {
    alert("获取失败: " + (e.response?.data?.detail || e.message));
  } finally {
    calculating.value = false;
  }
};

const addGroup = () => {
  form.core_structure.push({ cores: 1, strands: 1, gauge: 1.0 });
};
const removeGroup = (index) => {
  form.core_structure.splice(index, 1);
};

const preview = computed(() => {
  const coeff = form.material === 'Al' ? 0.214 : 0.7;
  let totalConductorW = 0;

  form.core_structure.forEach(g => {
    const w = (g.gauge * g.gauge * g.strands * g.cores * coeff * form.length) / 100;
    totalConductorW += w;
  });

  const condA = totalConductorW * form.copper_price;
  const pvcW = Math.max(0, form.total_weight - totalConductorW);
  const pvcA = pvcW * form.pvc_price;
  const total = condA + pvcA + form.labor_cost;

  return {
    copper_weight: totalConductorW.toFixed(3),
    pvc_weight: pvcW.toFixed(3),
    total_cost: total.toFixed(2)
  };
});

const closeModal = () => emit('close');
const handleSave = async () => {
  if(!form.spec_name) return alert("请填写规格");
  if(form.copper_price <= 0) if(!confirm("导体单价为 0，确定要保存吗？")) return;
  
  loading.value = true;
  try {
    if (isEditMode.value) {
      await axios.put(`/admin/costs/${props.editData.id}`, form);
    } else {
      await axios.post('/admin/costs/', form);
    }
    emit('saved');
    closeModal();
  } catch (e) {
    alert('错误: ' + (e.response?.data?.detail || e.message));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.input-std {
  @apply mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:ring-indigo-500 focus:border-indigo-500 text-xs;
}
.lbl-mini {
  @apply block text-xs font-medium text-gray-500 mb-1;
}
</style>