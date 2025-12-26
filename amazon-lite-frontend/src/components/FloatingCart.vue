<template>
  <div>
    <div 
      v-if="!isCartOpen"
      @click="isCartOpen = true"
      class="fixed bottom-8 right-8 z-50 cursor-pointer group"
    >
      <div class="relative bg-gray-900 text-white p-4 rounded-full shadow-2xl hover:bg-orange-600 transition-all duration-300 transform group-hover:scale-110">
        <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <span v-if="cartItems.length > 0" class="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold w-6 h-6 flex items-center justify-center rounded-full border-2 border-white">
          {{ cartItems.length }}
        </span>
      </div>
    </div>

    <div v-if="isCartOpen" class="fixed inset-0 z-50 flex justify-end">
      <div @click="isCartOpen = false" class="absolute inset-0 bg-black/30 backdrop-blur-sm transition-opacity"></div>
      
      <div class="relative w-full max-w-md bg-white h-full shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out">
        
        <div class="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div>
            <h2 class="text-lg font-bold text-gray-900">采购清单</h2>
            <p class="text-xs text-gray-500 mt-1">共 {{ cartItems.length }} 种商品</p>
          </div>
          <button @click="isCartOpen = false" class="p-2 text-gray-400 hover:text-gray-900 hover:bg-gray-200 rounded-full transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-6">
          <div v-if="cartItems.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400">
            <svg class="w-16 h-16 mb-4 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
            <p>清单是空的</p>
            <button @click="isCartOpen=false; $router.push('/products')" class="mt-4 text-orange-600 text-sm font-bold hover:underline">去添加商品</button>
          </div>

          <div v-for="item in cartItems" :key="item.id" class="flex gap-4 group">
            <div class="w-20 h-20 bg-gray-100 rounded-lg border border-gray-200 overflow-hidden flex-shrink-0 relative">
              <img :src="item.image_url" class="w-full h-full object-cover mix-blend-multiply">
            </div>

            <div class="flex-1 flex flex-col justify-between">
              <div>
                <div class="flex justify-between items-start">
                  <h3 class="text-sm font-bold text-gray-900 line-clamp-1" :title="item.product_name">{{ item.product_name }}</h3>
                  <button @click="removeFromCart(item.id)" class="text-gray-300 hover:text-red-500 transition-colors p-1 -mr-2">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
                <div class="text-xs text-gray-500 mt-1 flex items-center gap-2">
                  <span class="bg-gray-100 px-1.5 py-0.5 rounded border border-gray-200">{{ item.spec }}</span>
                  <span>{{ item.color }}</span>
                </div>
              </div>

              <div class="flex justify-between items-end mt-2">
                <div class="font-mono text-sm font-bold text-gray-900">¥{{ item.price }} <span class="text-xs text-gray-400 font-normal">/{{ item.unit }}</span></div>
                
                <div class="flex items-center border border-gray-300 rounded-lg overflow-hidden h-8">
                  <button 
                    @click="updateQuantity(item.id, item.quantity - 1)" 
                    class="w-8 h-full flex items-center justify-center bg-gray-50 hover:bg-gray-100 active:bg-gray-200 border-r border-gray-300 transition-colors"
                  >
                    <svg class="w-3 h-3 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" /></svg>
                  </button>
                  <input 
                    type="number" 
                    v-model.number="item.quantity" 
                    @change="updateQuantity(item.id, item.quantity)"
                    class="w-10 h-full text-center text-sm border-none focus:ring-0 p-0"
                  >
                  <button 
                    @click="updateQuantity(item.id, item.quantity + 1)" 
                    class="w-8 h-full flex items-center justify-center bg-gray-50 hover:bg-gray-100 active:bg-gray-200 border-l border-gray-300 transition-colors"
                  >
                    <svg class="w-3 h-3 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="cartItems.length > 0" class="p-5 border-t border-gray-100 bg-gray-50 space-y-4">
          <div class="flex justify-between items-end">
            <span class="text-sm text-gray-500">预估总额 (不含税)</span>
            <span class="text-2xl font-black text-gray-900 font-mono">¥{{ cartTotal.toFixed(2) }}</span>
          </div>
          <button 
            @click="isCartOpen = false; $router.push('/checkout')"
            class="w-full py-3.5 bg-gray-900 hover:bg-orange-600 text-white rounded-xl font-bold text-base shadow-lg transition-all duration-300 flex justify-center items-center gap-2"
          >
            <span>去生成报价单</span>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useCart } from '../composables/useCart';
const { cartItems, isCartOpen, removeFromCart, updateQuantity, cartTotal } = useCart();
</script>