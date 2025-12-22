<template>
  <div v-if="isOpen" class="fixed inset-0 z-[70] flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="close"></div>

    <div
      class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col md:flex-row overflow-hidden relative z-10 animate-fade-in-up">

      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 z-20">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="w-full md:w-1/3 bg-gray-50 flex items-center justify-center p-6 border-r border-gray-100">
        <img :src="product.image_url"
          class="max-h-64 object-contain mix-blend-multiply hover:scale-105 transition-transform duration-500">
      </div>

      <div class="w-full md:w-2/3 flex flex-col h-[80vh] md:h-auto">
        <div class="p-6 border-b border-gray-100">
          <h2 class="text-2xl font-bold text-gray-900">{{ product.name }}</h2>
          <p class="text-sm text-gray-500 mt-1">国标保检 / 纯铜制造</p>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-8">

          <div>
            <h3 class="text-sm font-bold text-gray-900 mb-3">选择规格 (截面平方)</h3>
            <div class="flex flex-wrap gap-3">
              <button v-for="spec in uniqueSpecs" :key="spec" @click="selectedSpec = spec"
                class="px-4 py-2 rounded-lg border text-sm font-medium transition-all" :class="selectedSpec === spec
                  ? 'border-orange-500 bg-orange-50 text-orange-700 ring-1 ring-orange-500'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'">
                {{ spec }}
              </button>
            </div>
          </div>

          <div v-if="selectedSpec">
            <div class="flex justify-between items-end mb-3">
              <h3 class="text-sm font-bold text-gray-900">选择颜色 & 数量</h3>
              <span class="text-xs text-orange-600 font-mono">单价: ¥{{ currentPrice }}</span>
            </div>

            <div class="bg-gray-50 rounded-xl p-4 border border-gray-100 space-y-3">
              <div v-for="variant in currentVariants" :key="variant.id" class="flex items-center justify-between group">
                <div class="flex items-center w-1/3">
                  <span class="w-4 h-4 rounded-full mr-2 border border-gray-200 shadow-sm"
                    :style="{ backgroundColor: getColorCode(variant.color) }"></span>
                  <span class="text-sm text-gray-700 font-medium">{{ variant.color }}</span>
                </div>

                <div class="w-1/3 text-center">
                  <span v-if="variant.stock > 100"
                    class="text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded-full">现货</span>
                  <span v-else-if="variant.stock > 0"
                    class="text-xs text-orange-600 bg-orange-100 px-2 py-0.5 rounded-full">剩 {{ variant.stock }}</span>
                  <span v-else class="text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full font-bold">可预订
                    (3天)</span>
                </div>

                <div class="w-1/3 flex justify-end">
                  <div class="flex items-center border border-gray-300 rounded-lg bg-white h-8 overflow-hidden">
                    <button @click="changeQty(variant.id, -1)"
                      class="w-8 h-full hover:bg-gray-100 text-gray-500">-</button>
                    <input type="number" v-model.number="quantities[variant.id]"
                      class="w-12 h-full text-center text-sm border-x border-gray-100 focus:outline-none"
                      placeholder="0" min="0" :max="99999">
                    <button @click="changeQty(variant.id, 1)"
                      class="w-8 h-full hover:bg-gray-100 text-gray-500">+</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else
            class="text-center py-8 text-gray-400 text-sm bg-gray-50 rounded-xl border border-dashed border-gray-200">
            请先选择一种电线规格
          </div>

        </div>

        <div class="p-6 border-t border-gray-100 bg-white flex justify-between items-center">
          <div>
            <p class="text-xs text-gray-500">已选总数</p>
            <p class="text-xl font-bold text-gray-900 font-mono">{{ totalSelectedQty }} <span
                class="text-sm font-normal text-gray-400">卷/盘</span></p>
          </div>
          <button @click="confirmAdd" :disabled="totalSelectedQty === 0"
            class="bg-gray-900 text-white px-8 py-3 rounded-xl font-bold hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center">
            加入清单
            <svg class="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
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
    default: () => ({ variants: [] }) // 防止报错
  }
});

const emit = defineEmits(['close', 'add-to-cart']);

// 状态
const selectedSpec = ref('');
const quantities = reactive({}); // { variant_id: quantity }

// 监听弹窗打开，重置状态
watch(() => props.isOpen, (val) => {
  if (val) {
    selectedSpec.value = '';
    // 清空数量
    for (const key in quantities) delete quantities[key];
    // 默认选中第一个规格（如果有）
    if (uniqueSpecs.value.length > 0) selectedSpec.value = uniqueSpecs.value[0];
  }
});

// 计算所有不重复的规格
const uniqueSpecs = computed(() => {
  if (!props.product.variants) return [];
  const specs = props.product.variants.map(v => v.spec);
  // 【修复】使用 localeCompare 进行数字模式排序
  return [...new Set(specs)].sort((a, b) =>
    a.localeCompare(b, undefined, { numeric: true })
  );
});

// 计算当前选中规格下的所有变体（颜色）
const currentVariants = computed(() => {
  if (!selectedSpec.value || !props.product.variants) return [];
  return props.product.variants.filter(v => v.spec === selectedSpec.value);
});

// 获取当前规格的单价 (假设同一规格不同颜色价格一致)
const currentPrice = computed(() => {
  if (currentVariants.value.length > 0) return currentVariants.value[0].price;
  return 0;
});

// 计算已选总数
const totalSelectedQty = computed(() => {
  let total = 0;
  for (const vid in quantities) {
    total += (quantities[vid] || 0);
  }
  return total;
});

// 辅助函数
const changeQty = (vid, delta) => {
  const current = quantities[vid] || 0;
  const variant = props.product.variants.find(v => v.id === vid);
  const max = variant ? variant.stock : 999;

  let next = current + delta;
  if (next < 0) next = 0;
  if (next > max) next = max;

  quantities[vid] = next;
};

// 简单的颜色映射，仅用于视觉展示
const getColorCode = (name) => {
  const map = {
    '红色': '#ef4444', '红': '#ef4444',
    '蓝色': '#3b82f6', '蓝': '#3b82f6',
    '黄色': '#eab308', '黄': '#eab308',
    '绿色': '#22c55e', '绿': '#22c55e',
    '双色': '#84cc16', // 黄绿
    '黑色': '#1f2937', '黑': '#1f2937',
    '白色': '#f3f4f6', '白': '#f3f4f6'
  };
  return map[name] || '#cbd5e1'; // 默认灰
};

const close = () => emit('close');

// 【新增】智能获取单位
const dynamicUnit = computed(() => {
  // 1. 尝试读取产品主表的 unit
  if (props.product.unit) return props.product.unit;
  // 2. 如果主表没单位，尝试读取第一个规格的 unit (如果后端把单位放在变体里)
  if (props.product.variants && props.product.variants.length > 0) {
    return props.product.variants[0].unit || '单位'; // 如果还取不到，显示通用占位符
  }
  return '单位';
});

const confirmAdd = () => {
  // 提取所有数量 > 0 的项
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
/* 隐藏 Chrome, Safari, Edge 的数字输入框箭头 */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type=number] {
  -moz-appearance: textfield;
}

.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>