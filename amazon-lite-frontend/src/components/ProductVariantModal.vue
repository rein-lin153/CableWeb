<template>
  <div v-if="isOpen" class="fixed inset-0 z-[70] flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="close"></div>

    <div
      class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col md:flex-row overflow-hidden relative z-10 animate-fade-in-up">

      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 z-20 bg-white rounded-full p-1">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="w-full md:w-1/3 bg-gray-50 flex flex-col border-r border-gray-100">
        <div class="flex-1 flex items-center justify-center p-6">
            <img :src="product.image_url"
            class="max-h-64 object-contain mix-blend-multiply hover:scale-105 transition-transform duration-500">
        </div>
        <div class="p-6 border-t border-gray-100 bg-white">
            <h2 class="text-xl font-bold text-gray-900 leading-tight">{{ product.name }}</h2>
            <div class="mt-3 space-y-2">
                <div class="flex items-center text-xs text-gray-500">
                    <span class="w-20 text-gray-400">品牌/标准</span>
                    <span class="font-medium text-gray-900">国标纯铜 / 足米</span>
                </div>
                <div class="flex items-center text-xs text-gray-500">
                    <span class="w-20 text-gray-400">当前规格</span>
                    <span class="font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded">{{ selectedSpec || '请选择' }}</span>
                </div>
            </div>
        </div>
      </div>

      <div class="w-full md:w-2/3 flex flex-col h-[80vh] md:h-auto bg-white">
        
        <div class="p-6 border-b border-gray-100 pb-4">
          <h3 class="text-sm font-bold text-gray-900 mb-3 flex items-center">
            1. 选择规格 (截面平方)
            <span class="ml-2 text-[10px] font-normal text-gray-400 bg-gray-100 px-1.5 rounded">点击切换</span>
          </h3>
          <div class="flex flex-wrap gap-2">
            <button v-for="spec in uniqueSpecs" :key="spec" @click="selectedSpec = spec"
              class="px-3 py-1.5 rounded-md border text-sm font-bold transition-all" :class="selectedSpec === spec
                ? 'border-orange-500 bg-orange-600 text-white shadow-md transform scale-105'
                : 'border-gray-200 text-gray-600 hover:border-orange-300 hover:text-orange-600 bg-white'">
              {{ spec }}
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-0 bg-gray-50/30">
            <div v-if="selectedSpec" class="divide-y divide-gray-100">
                <div class="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-100/50 text-xs font-bold text-gray-500 sticky top-0 backdrop-blur-sm z-10 border-b border-gray-200">
                    <div class="col-span-4">颜色 / 变体</div>
                    <div class="col-span-3 text-center">库存状态</div>
                    <div class="col-span-5 text-right">采购数量</div>
                </div>

                <div v-for="variant in currentVariants" :key="variant.id" 
                     class="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-orange-50/30 transition-colors group"
                     :class="quantities[variant.id] > 0 ? 'bg-orange-50/50' : ''">
                    
                    <div class="col-span-4 flex items-center">
                        <span class="w-6 h-6 rounded-full mr-3 border border-gray-200 shadow-sm flex-shrink-0"
                            :style="{ backgroundColor: getColorCode(variant.color) }"></span>
                        <div class="flex flex-col">
                            <span class="text-sm font-bold text-gray-800">{{ variant.color }}</span>
                            <span class="text-[10px] text-gray-400">¥{{ variant.price }}</span>
                        </div>
                    </div>

                    <div class="col-span-3 text-center">
                         <span v-if="variant.stock > 100" class="text-[10px] font-bold text-green-600 bg-green-50 px-2 py-1 rounded-full border border-green-100">
                             现货足
                         </span>
                         <span v-else-if="variant.stock > 0" class="text-[10px] font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded-full border border-orange-100">
                             仅剩 {{ variant.stock }}
                         </span>
                         <span v-else class="text-[10px] font-bold text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
                             需订货
                         </span>
                    </div>

                    <div class="col-span-5 flex justify-end">
                        <div class="flex items-center border border-gray-300 rounded-lg bg-white h-9 overflow-hidden shadow-sm group-hover:border-orange-300 transition-colors">
                            <button @click="changeQty(variant.id, -1)" 
                                class="w-8 h-full flex items-center justify-center hover:bg-gray-100 text-gray-400 hover:text-gray-600 active:bg-gray-200 transition-colors">
                                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M20 12H4" /></svg>
                            </button>
                            <input type="number" v-model.number="quantities[variant.id]"
                                class="w-14 h-full text-center text-sm font-bold text-gray-900 border-x border-gray-100 focus:outline-none focus:bg-orange-50 transition-colors placeholder-gray-300"
                                placeholder="0" min="0" :max="99999">
                            <button @click="changeQty(variant.id, 1)" 
                                class="w-8 h-full flex items-center justify-center hover:bg-gray-100 text-gray-400 hover:text-gray-600 active:bg-gray-200 transition-colors">
                                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" /></svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-else class="h-full flex flex-col items-center justify-center text-gray-400 space-y-4 p-8">
                <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                    <svg class="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" /></svg>
                </div>
                <p class="text-sm">请先在上方选择一个线缆规格</p>
            </div>
        </div>

        <div class="p-4 md:p-6 border-t border-gray-200 bg-white flex justify-between items-center shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-20">
          <div class="flex flex-col">
            <span class="text-xs text-gray-500">已选总数量</span>
            <div class="flex items-baseline gap-1">
                <span class="text-2xl font-black text-gray-900 font-mono tracking-tight">{{ totalSelectedQty }}</span>
                <span class="text-xs font-bold text-gray-400">{{ dynamicUnit }}</span>
            </div>
            <div class="text-[10px] text-orange-600 font-medium mt-0.5" v-if="totalPrice > 0">
                预估总价: ¥{{ totalPrice.toFixed(2) }}
            </div>
          </div>
          
          <button @click="confirmAdd" :disabled="totalSelectedQty === 0"
            class="bg-gray-900 text-white px-6 md:px-10 py-3.5 rounded-xl font-bold hover:bg-orange-600 hover:shadow-lg hover:shadow-orange-500/30 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none flex items-center gap-2">
            <span>加入采购清单</span>
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  product: {
    type: Object,
    required: true,
    default: () => ({ variants: [] })
  }
});

const emit = defineEmits(['close', 'add-to-cart']);

// 状态
const selectedSpec = ref('');
const quantities = reactive({}); // { variant_id: quantity }

// 监听弹窗打开，重置
watch(() => props.isOpen, (val) => {
  if (val) {
    // 只有当没有选中规格时才重置，保留用户上次的选择习惯可能更好？
    // 这里还是选择重置数量，但保留规格如果可能的话
    // 为简单起见，先清空数量
    for (const key in quantities) delete quantities[key];
    
    // 默认选中第一个规格（如果未选中）
    if (!selectedSpec.value && uniqueSpecs.value.length > 0) {
        selectedSpec.value = uniqueSpecs.value[0];
    }
  }
});

// 监听规格变化，清空数量（防止切到另一个规格时，原来的ID对应的数量还在，虽然不可见但逻辑上可能出错）
watch(selectedSpec, () => {
    for (const key in quantities) delete quantities[key];
});

// 计算所有不重复的规格
const uniqueSpecs = computed(() => {
  if (!props.product.variants) return [];
  const specs = props.product.variants.map(v => v.spec);
  return [...new Set(specs)].sort((a, b) => 
    a.localeCompare(b, undefined, { numeric: true })
  );
});

// 当前规格下的变体
const currentVariants = computed(() => {
  if (!selectedSpec.value || !props.product.variants) return [];
  return props.product.variants.filter(v => v.spec === selectedSpec.value);
});

// 计算总数
const totalSelectedQty = computed(() => {
  let total = 0;
  for (const vid in quantities) {
    if (quantities[vid]) total += quantities[vid];
  }
  return total;
});

// 计算总价
const totalPrice = computed(() => {
  let total = 0;
  for (const vid in quantities) {
    const qty = quantities[vid] || 0;
    if (qty > 0) {
        const variant = props.product.variants.find(v => v.id == vid);
        if (variant) {
            total += (variant.price * qty);
        }
    }
  }
  return total;
});

// 动态单位
const dynamicUnit = computed(() => {
  if (props.product.unit) return props.product.unit;
  if (props.product.variants && props.product.variants.length > 0) {
    return props.product.variants[0].unit || '卷';
  }
  return '卷';
});

const changeQty = (vid, delta) => {
  const current = quantities[vid] || 0;
  // 可以在这里加库存限制逻辑，暂时不做强限制，只做非负限制
  let next = current + delta;
  if (next < 0) next = 0;
  quantities[vid] = next;
};

// 颜色代码映射（建议后续由后端返回 hex code）
const getColorCode = (name) => {
  if (!name) return '#eeeeee';
  const map = {
    '红色': '#ef4444', '红': '#ef4444',
    '蓝色': '#3b82f6', '蓝': '#3b82f6',
    '黄色': '#eab308', '黄': '#eab308',
    '绿色': '#22c55e', '绿': '#22c55e',
    '双色': 'linear-gradient(135deg, #eab308 50%, #22c55e 50%)', // 特殊处理黄绿双色
    '黄绿': 'linear-gradient(135deg, #eab308 50%, #22c55e 50%)',
    '黑色': '#1f2937', '黑': '#1f2937',
    '白色': '#f3f4f6', '白': '#f3f4f6',
    '棕色': '#78350f', '棕': '#78350f',
    '灰色': '#9ca3af', '灰': '#9ca3af'
  };
  return map[name] || '#cbd5e1'; 
};

const close = () => emit('close');

const confirmAdd = () => {
  const itemsToAdd = [];
  for (const [vid, qty] of Object.entries(quantities)) {
    if (qty > 0) {
      itemsToAdd.push({ variantId: parseInt(vid), quantity: qty });
    }
  }
  emit('add-to-cart', itemsToAdd);
  close();
};
</script>

<style scoped>
/* 隐藏数字输入框箭头 */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number] {
  -moz-appearance: textfield;
}

.animate-fade-in-up {
  animation: fadeInUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>