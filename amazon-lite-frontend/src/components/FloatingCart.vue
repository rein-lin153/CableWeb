<template>
  <div class="fixed bottom-8 right-8 z-40 print:hidden">
    <button 
      @click="toggleCart"
      class="relative group bg-gray-900 hover:bg-orange-600 text-white w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95"
    >
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
      
      <span v-if="totalCount > 0" class="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold w-5 h-5 flex items-center justify-center rounded-full border-2 border-white animate-bounce">
        {{ totalCount }}
      </span>

      <span class="absolute right-full mr-3 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
        采购清单
      </span>
    </button>

    <CartDrawer />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useCart } from '../composables/useCart';
import CartDrawer from './CartDrawer.vue';

const { isCartOpen, cartItems } = useCart();

const totalCount = computed(() => cartItems.value.length);

const toggleCart = () => {
  isCartOpen.value = !isCartOpen.value;
};
</script>