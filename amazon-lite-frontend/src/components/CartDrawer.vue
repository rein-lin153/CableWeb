<template>
  <div class="relative z-[100]" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">

    <transition enter-active-class="ease-in-out duration-500" enter-from-class="opacity-0" enter-to-class="opacity-100"
      leave-active-class="ease-in-out duration-500" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="isCartOpen" class="fixed inset-0 bg-gray-900/75 backdrop-blur-sm transition-opacity z-40"
        @click="closeCart"></div>
    </transition>

    <div v-if="isCartOpen" class="fixed inset-0 overflow-hidden z-50 pointer-events-none">
      <div class="absolute inset-0 overflow-hidden">
        <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">

          <transition enter-active-class="transform transition ease-in-out duration-500 sm:duration-700"
            enter-from-class="translate-x-full" enter-to-class="translate-x-0"
            leave-active-class="transform transition ease-in-out duration-500 sm:duration-700"
            leave-from-class="translate-x-0" leave-to-class="translate-x-full">
            <div class="pointer-events-auto w-screen max-w-md">
              <div class="flex h-full flex-col bg-white shadow-2xl">

                <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-gray-50">
                  <div>
                    <h2 class="text-lg font-bold text-gray-900">采购清单</h2>
                    <p class="text-xs text-gray-500 mt-0.5">共 {{ cartItems.length }} 种商品</p>
                  </div>
                  <button type="button"
                    class="text-gray-400 hover:text-gray-600 bg-white rounded-full p-2 hover:bg-gray-200 transition-all"
                    @click="closeCart">
                    <span class="sr-only">Close panel</span>
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div class="flex-1 overflow-y-auto bg-gray-50/30 px-4 py-4 sm:px-6">

                  <div v-if="cartItems.length === 0"
                    class="flex flex-col items-center justify-center h-full text-center">
                    <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                      <svg class="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                      </svg>
                    </div>
                    <h3 class="text-gray-900 font-medium">清单是空的</h3>
                    <p class="text-gray-500 text-sm mt-1 mb-6">还没有添加任何电缆产品</p>
                    <button @click="closeCart" class="text-orange-600 font-bold hover:underline">去选购 &rarr;</button>
                  </div>

                  <ul v-else class="space-y-4">
                    <li v-for="item in cartItems" :key="item.id"
                      class="bg-white rounded-xl p-3 shadow-sm border border-gray-100 relative group transition-all hover:shadow-md">

                      <div class="flex">
                        <div
                          class="h-24 w-24 flex-shrink-0 overflow-hidden rounded-lg border border-gray-100 bg-white p-1">
                          <img :src="item.image_url || 'https://via.placeholder.com/150'"
                            class="h-full w-full object-contain mix-blend-multiply" alt="Product">
                        </div>

                        <div class="ml-4 flex flex-1 flex-col justify-between">
                          <div>
                            <div class="flex justify-between items-start">
                              <h3 class="text-sm font-bold text-gray-900 line-clamp-2 pr-6">
                                {{ item.product_name }}
                              </h3>

                              <button @click="removeFromCart(item.id)"
                                class="text-gray-300 hover:text-red-500 transition-colors p-1 -mr-2 -mt-2">
                                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            </div>

                            <div class="mt-2 flex flex-wrap gap-2">
                              <span
                                class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600 border border-gray-200">
                                {{ item.spec }}
                              </span>
                              <span
                                class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-100">
                                {{ item.color }}
                              </span>
                            </div>
                            <div class="mt-1.5 flex items-center text-xs text-gray-400">
                              <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                              </svg>
                              单位: {{ item.unit || '卷' }}
                            </div>
                          </div>

                          <div class="flex items-end justify-between mt-3">
                            <div class="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded border border-gray-100">
                              数量: <span class="font-bold text-gray-900">{{ item.quantity }}</span>
                            </div>
                            <div class="text-right">
                              <p class="text-sm font-bold text-orange-600 font-mono">
                                ¥{{ item.subtotal ? item.subtotal.toLocaleString() : (item.price *
                                item.quantity).toFixed(2) }}
                              </p>

                              <p class="text-[10px] text-gray-400">单价: ¥{{ item.price }}</p>

                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>

                <div class="border-t border-gray-100 bg-white px-6 py-6 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-10">
                  <div class="flex justify-between text-base font-medium text-gray-900 mb-2">
                    <p>预估总额</p>
                    <p class="font-mono text-xl text-orange-600 font-bold">¥{{ cartTotal.toLocaleString() }}</p>
                  </div>

                  <p class="text-xs text-gray-400 mb-6 flex items-center">
                    <svg class="w-3 h-3 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clip-rule="evenodd" />
                    </svg>
                    最终价格以客户经理确认后的折扣价为准。
                  </p>
                  <button @click="submitOrder" :disabled="loading || cartItems.length === 0"
                    class="w-full flex items-center justify-center rounded-xl bg-gray-900 px-6 py-3.5 text-base font-bold text-white shadow-lg shadow-gray-900/20 hover:bg-orange-600 hover:shadow-orange-600/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group">
                    <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none"
                      viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                      </path>
                    </svg>
                    <span v-else class="flex items-center">
                      立即提交订单 (无需付款)
                      <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none"
                        viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </span>
                  </button>
                </div>

              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useCart } from '../composables/useCart';

const { cartItems, isCartOpen, removeFromCart, submitOrder, fetchCart, cartTotal, loading } = useCart();

const closeCart = () => {
  isCartOpen.value = false;
};

onMounted(() => {
  fetchCart();
});
</script>