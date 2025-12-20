<template>
  <div class="fixed top-6 right-6 z-[9999] flex flex-col gap-4 pointer-events-none w-full max-w-sm">
    <TransitionGroup 
      enter-active-class="transition ease-out duration-300"
      enter-from-class="transform translate-x-8 opacity-0 scale-95"
      enter-to-class="transform translate-x-0 opacity-100 scale-100"
      leave-active-class="transition ease-in duration-200 absolute w-full" 
      leave-from-class="transform translate-x-0 opacity-100"
      leave-to-class="transform translate-x-8 opacity-0 scale-90"
      move-class="transition ease-in-out duration-300"
    >
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="pointer-events-auto relative overflow-hidden rounded-2xl bg-white/90 backdrop-blur-xl border border-white/20 shadow-[0_8px_30px_rgb(0,0,0,0.08)] ring-1 ring-black/5 p-4 flex items-start gap-4 cursor-pointer hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group"
        @click="remove(toast.id)"
      >
        <div class="absolute left-0 top-0 bottom-0 w-1" :class="getTypeColor(toast.type)"></div>

        <div 
          class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-sm border border-black/5"
          :class="getIconBg(toast.type)"
        >
          <svg v-if="toast.type === 'success'" class="w-5 h-5" :class="getIconColor(toast.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-if="toast.type === 'error'" class="w-5 h-5" :class="getIconColor(toast.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-if="toast.type === 'warning'" class="w-5 h-5" :class="getIconColor(toast.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <svg v-if="toast.type === 'info'" class="w-5 h-5" :class="getIconColor(toast.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <div class="flex-1 min-w-0 py-0.5">
          <h3 class="text-sm font-bold text-gray-900 leading-tight mb-1">
            {{ getTitle(toast.type) }}
          </h3>
          <p class="text-xs text-gray-500 font-medium leading-relaxed break-words opacity-90">
            {{ toast.message }}
          </p>
        </div>

        <button 
          @click.stop="remove(toast.id)"
          class="flex-shrink-0 text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-1 rounded-full transition-colors opacity-0 group-hover:opacity-100"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div 
          class="absolute bottom-0 left-0 h-0.5 bg-current opacity-20 animate-shrink origin-left"
          :class="getIconColor(toast.type)"
          style="width: 100%; animation-duration: 4s;"
        ></div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast';

const { toasts, remove } = useToast();

const getTitle = (type) => {
  switch (type) {
    case 'success': return '操作成功';
    case 'error': return '发生错误';
    case 'warning': return '请注意';
    case 'info': return '新消息';
    default: return '提示';
  }
};

// 各种颜色的配置
const getTypeColor = (type) => {
  const map = {
    success: 'bg-emerald-500',
    error: 'bg-rose-500',
    warning: 'bg-amber-500',
    info: 'bg-blue-500',
  };
  return map[type] || 'bg-gray-500';
};

const getIconBg = (type) => {
  const map = {
    success: 'bg-emerald-50',
    error: 'bg-rose-50',
    warning: 'bg-amber-50',
    info: 'bg-blue-50',
  };
  return map[type] || 'bg-gray-50';
};

const getIconColor = (type) => {
  const map = {
    success: 'text-emerald-500',
    error: 'text-rose-500',
    warning: 'text-amber-500',
    info: 'text-blue-500',
  };
  return map[type] || 'text-gray-500';
};
</script>

<style scoped>
/* 定义进度条收缩动画 */
@keyframes shrink {
  from { width: 100%; }
  to { width: 0%; }
}
.animate-shrink {
  animation-timing-function: linear;
  animation-fill-mode: forwards;
}
</style>