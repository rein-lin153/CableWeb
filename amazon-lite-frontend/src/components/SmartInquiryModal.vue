<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0" enter-to="opacity-100" leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="duration-200 ease-in" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
            <DialogPanel class="w-full max-w-lg transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
              
              <div class="bg-gray-900 px-6 py-4 flex justify-between items-center">
                <h3 class="text-lg font-bold text-white flex items-center">
                  <svg class="w-5 h-5 mr-2 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  上传采购清单 (BOM)
                </h3>
                <button @click="closeModal" class="text-gray-400 hover:text-white"><svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
              </div>

              <div class="p-6">
                <p class="text-sm text-gray-500 mb-6">
                  无需逐个搜索产品。直接上传您的 Excel/PDF 采购清单，或拍摄手写单据。我们的技术团队将在 30 分钟内为您核算最优价格。
                </p>

                <div class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:bg-gray-50 hover:border-orange-400 transition-colors cursor-pointer group">
                  <div class="w-12 h-12 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                  </div>
                  <p class="text-sm font-bold text-gray-900">点击上传文件</p>
                  <p class="text-xs text-gray-400 mt-1">支持 Excel, PDF, JPG, PNG (Max 10MB)</p>
                </div>

                <div class="mt-6 space-y-4">
                  <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1">联系电话 <span class="text-red-500">*</span></label>
                    <input type="tel" placeholder="请输入您的手机号" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none">
                  </div>
                  <div>
                     <label class="block text-sm font-bold text-gray-700 mb-1">备注说明</label>
                     <textarea rows="2" placeholder="例如：急需现货，工地在金边..." class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 outline-none"></textarea>
                  </div>
                </div>

                <div class="mt-8">
                  <button type="button" class="w-full bg-orange-600 text-white font-bold py-3 rounded-xl shadow-lg hover:bg-orange-500 transition-all flex items-center justify-center">
                    立即获取报价
                  </button>
                </div>
              </div>

            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { Dialog, DialogPanel, TransitionRoot, TransitionChild } from '@headlessui/vue';
defineProps(['isOpen']);
const emit = defineEmits(['close']);
const closeModal = () => emit('close');
</script>