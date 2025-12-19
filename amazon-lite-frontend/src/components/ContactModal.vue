<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[9999] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      
      <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

      <div class="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
        
        <div class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-3xl border-t-4 border-orange-600 z-[10000]">
          
          <div class="bg-gray-50 px-6 py-4 flex justify-between items-center border-b border-gray-100">
            <div>
              <h3 class="text-xl font-bold leading-6 text-gray-900" id="modal-title">获取出厂报价</h3>
              <p class="mt-1 text-sm text-gray-500">选择您方便的联系方式，经理将即时响应</p>
            </div>
            <button @click="$emit('close')" class="rounded-full p-2 hover:bg-gray-200 transition-colors group">
              <svg class="h-6 w-6 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="px-6 py-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              <div class="space-y-4">
                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">点击直接联系</h4>
                
                <a href="tel:+8613800000000" class="flex items-center p-4 rounded-xl border border-gray-200 bg-white hover:border-orange-500 hover:shadow-md hover:shadow-orange-100 transition-all group cursor-pointer">
                  <div class="flex-shrink-0 h-10 w-10 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center group-hover:bg-orange-600 group-hover:text-white transition-colors">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500 group-hover:text-orange-600">24h 销售热线</p>
                    <p class="text-lg font-bold text-gray-900">+855 0965809551</p>
                  </div>
                </a>

                <a href="https://wa.me/123456789" target="_blank" class="flex items-center p-4 rounded-xl border border-gray-200 bg-white hover:border-green-500 hover:shadow-md hover:shadow-green-100 transition-all group cursor-pointer">
                  <div class="flex-shrink-0 h-10 w-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center group-hover:bg-green-600 group-hover:text-white transition-colors">
                    <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500 group-hover:text-green-600">WhatsApp</p>
                    <p class="text-lg font-bold text-gray-900">Start Chat</p>
                  </div>
                </a>

                <a href="https://t.me/bright_cable" target="_blank" class="flex items-center p-4 rounded-xl border border-gray-200 bg-white hover:border-blue-500 hover:shadow-md hover:shadow-blue-100 transition-all group cursor-pointer">
                  <div class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 text-blue-500 flex items-center justify-center group-hover:bg-blue-500 group-hover:text-white transition-colors">
                    <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 11.944 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.638z"/></svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500 group-hover:text-blue-500">Telegram</p>
                    <p class="text-lg font-bold text-gray-900">@bright_cable</p>
                  </div>
                </a>
              </div>

              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-100 flex flex-col items-center justify-center text-center">
                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">WeChat / 微信</h4>
                
                <div class="bg-white p-3 rounded-xl shadow-sm border border-gray-200 mb-4">
                  <img src="/wechat.jpg" alt="WeChat QR" class="w-40 h-40 object-contain">
                </div>
                
                <p class="text-gray-900 font-bold">扫一扫加好友</p>
                <p class="text-sm text-gray-500">获取详细产品手册与报价单</p>
                <div class="mt-4 px-3 py-1 bg-green-100 text-green-700 text-xs rounded-full font-mono">
                  ID: Tini
                </div>
              </div>

            </div>
          </div>
          
          <div class="bg-gray-50 px-6 py-4 border-t border-gray-100 text-center sm:text-right rounded-b-2xl">
            <span class="text-xs text-gray-400">工作时间: 周一至周日 8:00 - 22:00 (UTC+8)</span>
          </div>

        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineEmits(['close']);
</script>