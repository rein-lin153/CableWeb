<template>
  <div class="fixed bottom-24 right-4 z-40 flex flex-col items-end print:hidden">
    
    <transition 
      enter-active-class="transition duration-200 ease-out" 
      enter-from-class="transform translate-y-4 opacity-0 scale-95" 
      enter-to-class="transform translate-y-0 opacity-100 scale-100" 
      leave-active-class="transition duration-150 ease-in" 
      leave-from-class="transform translate-y-0 opacity-100 scale-100" 
      leave-to-class="transform translate-y-4 opacity-0 scale-95"
    >
      <div v-if="isOpen" class="mb-4 w-80 bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden ring-1 ring-black/5">
        <div class="bg-gray-900 px-4 py-3 flex justify-between items-center">
          <span class="text-white font-bold text-sm flex items-center">
             <svg class="w-4 h-4 mr-2 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
             采购清单 ({{ cartItems.length }})
          </span>
          <button @click="clearCart" class="text-xs text-gray-400 hover:text-white transition-colors">清空</button>
        </div>
        
        <div class="max-h-64 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          <div v-if="cartItems.length === 0" class="py-10 text-center text-gray-400 text-xs flex flex-col items-center">
            <svg class="w-8 h-8 mb-2 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
            清单是空的
          </div>
          <div v-else v-for="item in cartItems" :key="item.variantId" class="flex justify-between items-center p-2 hover:bg-gray-50 rounded-lg group transition-colors">
            <div class="flex-1 min-w-0 pr-2">
              <div class="text-xs font-bold text-gray-900 truncate">{{ item.product_name }}</div>
              <div class="text-[10px] text-gray-500 mt-0.5">{{ item.spec }} <span class="mx-1">·</span> {{ item.color }}</div>
            </div>
            <div class="text-right">
              <div class="text-xs font-bold text-orange-600 font-mono">¥{{ (item.price * item.quantity).toFixed(2) }}</div>
              <div class="text-[10px] text-gray-400">x{{ item.quantity }}</div>
            </div>
          </div>
        </div>

        <div class="p-4 bg-gray-50 border-t border-gray-100">
          <div class="flex justify-between items-end mb-4">
            <span class="text-xs text-gray-500">预估总额 (不含运费)</span>
            <span class="text-xl font-bold text-gray-900 font-mono">¥{{ total.toFixed(2) }}</span>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <button @click="generatePDF" class="px-3 py-2.5 bg-white border border-gray-300 text-gray-700 font-bold rounded-lg text-xs hover:bg-gray-50 hover:text-orange-600 hover:border-orange-200 transition-colors flex items-center justify-center shadow-sm">
              <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              下载报价单
            </button>
            <button @click="$router.push('/checkout')" class="px-3 py-2.5 bg-orange-600 text-white font-bold rounded-lg text-xs hover:bg-orange-500 transition-colors shadow-md shadow-orange-200">
              立即结算
            </button>
          </div>
        </div>
      </div>
    </transition>

    <button 
      @click="isOpen = !isOpen"
      class="relative bg-gray-900 hover:bg-orange-600 text-white w-14 h-14 rounded-full shadow-xl flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 group"
    >
      <svg v-if="!isOpen" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
      <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      
      <span v-if="cartItems.length > 0 && !isOpen" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full border-2 border-white animate-bounce">
        {{ cartItems.length }}
      </span>
      
      <span class="absolute right-full mr-3 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none shadow-lg">
        {{ isOpen ? '关闭清单' : '采购清单' }}
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useCart } from '../composables/useCart';
import { useRouter } from 'vue-router';

const { cartItems, clearCart } = useCart();
const router = useRouter();
const isOpen = ref(false);

const total = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0);
});

// 纯前端生成 PDF 报价单 (利用浏览器打印功能)
const generatePDF = () => {
  if (cartItems.value.length === 0) return alert('请先添加商品到清单');

  const printWindow = window.open('', '_blank');
  const dateStr = new Date().toLocaleDateString();
  const timeStr = new Date().toLocaleTimeString();
  
  const itemsHtml = cartItems.value.map((item, idx) => `
    <tr style="border-bottom: 1px solid #eee;">
      <td style="padding: 12px 8px; text-align: center;">${idx + 1}</td>
      <td style="padding: 12px 8px;">
        <div style="font-weight: bold; color: #111;">${item.product_name}</div>
        <div style="font-size: 12px; color: #666; margin-top: 4px;">规格: ${item.spec} | 颜色: ${item.color}</div>
      </td>
      <td style="padding: 12px 8px; text-align: center;">${item.quantity}</td>
      <td style="padding: 12px 8px; text-align: right; font-family: monospace;">¥${item.price}</td>
      <td style="padding: 12px 8px; text-align: right; font-weight: bold; font-family: monospace;">¥${(item.price * item.quantity).toFixed(2)}</td>
    </tr>
  `).join('');

  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>报价单 - Amazon Cable</title>
        <style>
          body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; max-width: 800px; margin: 0 auto; }
          .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; border-bottom: 2px solid #000; padding-bottom: 20px; }
          .logo { font-size: 28px; font-weight: 800; color: #ea580c; letter-spacing: -1px; }
          .logo span { color: #1f2937; }
          .info { text-align: right; font-size: 13px; line-height: 1.6; color: #555; }
          .title { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 30px; letter-spacing: 2px; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
          th { text-align: left; background: #f9fafb; padding: 12px 8px; font-size: 12px; text-transform: uppercase; color: #666; border-bottom: 2px solid #e5e7eb; font-weight: 600; }
          .total-box { display: flex; justify-content: flex-end; margin-top: 20px; }
          .total-row { display: flex; justify-content: space-between; width: 250px; padding: 8px 0; }
          .total-final { font-size: 20px; font-weight: bold; color: #ea580c; border-top: 2px solid #000; padding-top: 10px; margin-top: 5px; }
          .footer { margin-top: 60px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 20px; line-height: 1.6; }
          @media print {
            body { padding: 0; }
            button { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="logo">Amazon<span>Cable</span></div>
          <div class="info">
            <strong>Amazon Cable Co., Ltd.</strong><br>
            金边市堆谷区工业园 A8 栋<br>
            Tel: 400-888-8888 | Email: sales@amazoncable.com
          </div>
        </div>

        <div class="title">报价单 QUOTATION</div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px; font-size: 13px;">
          <div><strong>客户:</strong> 访客 (Guest)</div>
          <div style="text-align: right;">
            <strong>日期:</strong> ${dateStr}<br>
            <strong>时间:</strong> ${timeStr}
          </div>
        </div>
        
        <table>
          <thead>
            <tr>
              <th width="5%" style="text-align: center;">#</th>
              <th width="45%">产品描述 (Description)</th>
              <th width="10%" style="text-align: center;">数量 (Qty)</th>
              <th width="15%" style="text-align: right;">单价 (Unit Price)</th>
              <th width="25%" style="text-align: right;">小计 (Amount)</th>
            </tr>
          </thead>
          <tbody>
            ${itemsHtml}
          </tbody>
        </table>

        <div class="total-box">
          <div>
            <div class="total-row">
              <span>小计 Subtotal:</span>
              <span>¥${total.value.toFixed(2)}</span>
            </div>
            <div class="total-row">
              <span>税费 Tax (0%):</span>
              <span>¥0.00</span>
            </div>
            <div class="total-row total-final">
              <span>总计 Total:</span>
              <span>¥${total.value.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div class="footer">
          此报价单由系统自动生成，有效期为 3 天。<br>
          This quotation is automatically generated by the system and is valid for 3 days.<br>
          实际库存与价格以最终合同签署为准。
        </div>
        
        <script>
          setTimeout(function() { window.print(); }, 500);
        <\/script>
      </body>
    </html>
  `);
  printWindow.document.close();
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
</style>