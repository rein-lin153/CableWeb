import { ref } from 'vue';

// 全局状态，保证所有组件共享
const toasts = ref([]);

export function useToast() {
  // 添加通知
  const add = (message, type = 'info', duration = 3000) => {
    const id = Date.now();
    toasts.value.push({ id, message, type });

    // 自动消失
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }
  };

  // 移除通知
  const remove = (id) => {
    toasts.value = toasts.value.filter(t => t.id !== id);
  };

  // 快捷方法
  const success = (msg) => add(msg, 'success');
  const error = (msg) => add(msg, 'error', 5000); // 错误多停留一会
  const warning = (msg) => add(msg, 'warning');
  const info = (msg) => add(msg, 'info');

  return {
    toasts,
    add,
    remove,
    success,
    error,
    warning,
    info
  };
}