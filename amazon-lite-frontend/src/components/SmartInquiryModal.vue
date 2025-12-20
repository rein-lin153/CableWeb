<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-[9999] overflow-y-auto" role="dialog" aria-modal="true">

      <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" @click="close"></div>

      <div class="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">

        <div
          class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-5xl border-t-4 border-orange-600 z-[10000] flex flex-col md:flex-row">

          <button @click="close"
            class="absolute top-4 right-4 z-20 rounded-full p-2 bg-gray-100 hover:bg-gray-200 transition-colors group">
            <svg class="h-5 w-5 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div class="w-full md:w-3/5 p-6 md:p-8 flex flex-col">
            <div class="mb-6">
              <h3 class="text-2xl font-bold leading-6 text-gray-900">获取出厂报价</h3>
              <p class="mt-2 text-sm text-gray-500">上传清单或描述需求，工程团队将在 30 分钟内为您核算底价。</p>
            </div>

            <div class="flex space-x-6 mb-6 border-b border-gray-100">
              <button @click="activeTab = 'upload'" class="pb-3 text-sm font-bold transition-all relative"
                :class="activeTab === 'upload' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-400 hover:text-gray-600'">
                📄 上传文件 (Excel/PDF/图纸)
              </button>
              <button @click="activeTab = 'text'" class="pb-3 text-sm font-bold transition-all relative"
                :class="activeTab === 'text' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-400 hover:text-gray-600'">
                📝 文字描述需求
              </button>
            </div>

            <div v-if="activeTab === 'upload'" class="flex-1 flex flex-col min-h-[200px]">
              <div
                class="border-2 border-dashed border-orange-200 rounded-xl bg-orange-50/30 hover:bg-orange-50 transition-colors flex flex-col items-center justify-center py-8 cursor-pointer relative flex-1"
                @dragover.prevent @drop.prevent="handleDrop">
                <input type="file" multiple class="absolute inset-0 opacity-0 cursor-pointer" @change="handleFileSelect"
                  accept=".jpg,.png,.pdf,.xlsx,.xls,.doc,.docx" />

                <div v-if="files.length === 0" class="text-center">
                  <div
                    class="w-12 h-12 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p class="text-gray-900 font-medium">点击或拖拽上传</p>
                  <p class="text-gray-400 text-xs mt-1">支持图片、Excel、PDF、Word</p>
                </div>

                <div v-else class="w-full px-6 space-y-2 max-h-[200px] overflow-y-auto custom-scrollbar">
                  <div v-for="(file, index) in files" :key="index"
                    class="flex items-center justify-between bg-white p-2 rounded border border-gray-200 text-sm shadow-sm">
                    <div class="flex items-center truncate">
                      <svg class="w-4 h-4 text-gray-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd"
                          d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                          clip-rule="evenodd" />
                      </svg>
                      <span class="truncate max-w-[180px] text-gray-700">{{ file.name }}</span>
                    </div>
                    <button @click.stop="removeFile(index)"
                      class="text-gray-400 hover:text-red-500 ml-2 transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <div class="text-center mt-2">
                    <span class="text-orange-600 text-xs font-bold hover:underline">+ 继续添加</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'text'" class="flex-1 flex flex-col min-h-[200px]">
              <textarea v-model="textRemark"
                class="w-full flex-1 border border-gray-200 rounded-xl p-4 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none resize-none bg-gray-50 text-sm"
                placeholder="请描述您需要的电缆型号、规格、电压等级及大概长度。&#10;例如：YJV22 3*240 高压电缆 500米，需要含税含运费..."></textarea>
            </div>

            <div class="mt-6">
              <label class="block text-xs font-bold text-gray-700 mb-1.5">接收报价的联系方式 <span
                  class="text-red-500">*</span></label>
              <div class="flex gap-3">
                <input v-model="contactInfo" type="text"
                  class="flex-1 border border-gray-300 rounded-lg p-3 focus:ring-orange-500 outline-none text-sm"
                  placeholder="您的 手机号 / 微信 / WhatsApp / 邮箱">

                <button @click="handleSubmit" :disabled="submitting || !contactInfo"
                  class="bg-gray-900 text-white px-6 py-3 rounded-lg font-bold hover:bg-orange-600 transition-all shadow-lg shadow-orange-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center whitespace-nowrap">
                  <svg v-if="submitting" class="animate-spin h-4 w-4 mr-2 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  {{ submitting ? '提交中...' : '提交询价' }}
                </button>
              </div>
            </div>
          </div>

          <div
            class="w-full md:w-2/5 bg-gray-50 border-l border-gray-100 p-6 md:p-8 flex flex-col overflow-y-auto max-h-[600px] custom-scrollbar">
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">或者，直接联系经理</h4>

            <div class="space-y-3">

              <a href="tel:+8550965809551"
                class="flex items-center p-3 rounded-xl border border-gray-200 bg-white hover:border-orange-500 hover:shadow-md hover:shadow-orange-100 transition-all group cursor-pointer">
                <div
                  class="flex-shrink-0 h-10 w-10 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center group-hover:bg-orange-600 group-hover:text-white transition-colors">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <div class="ml-3 min-w-0">
                  <p class="text-xs font-medium text-gray-500 group-hover:text-orange-600">24h 销售热线</p>
                  <p class="text-sm font-bold text-gray-900 truncate">+855 0965809551</p>
                </div>
              </a>

              <a href="https://wa.me/123456789" target="_blank"
                class="flex items-center p-3 rounded-xl border border-gray-200 bg-white hover:border-green-500 hover:shadow-md hover:shadow-green-100 transition-all group cursor-pointer">
                <div
                  class="flex-shrink-0 h-10 w-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center group-hover:bg-green-600 group-hover:text-white transition-colors">
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path
                      d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-xs font-medium text-gray-500 group-hover:text-green-600">WhatsApp</p>
                  <p class="text-sm font-bold text-gray-900">Start Chat</p>
                </div>
              </a>

              <a href="https://t.me/bright_cable" target="_blank"
                class="flex items-center p-3 rounded-xl border border-gray-200 bg-white hover:border-blue-500 hover:shadow-md hover:shadow-blue-100 transition-all group cursor-pointer">
                <div
                  class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 text-blue-500 flex items-center justify-center group-hover:bg-blue-500 group-hover:text-white transition-colors">
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path
                      d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 11.944 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.638z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-xs font-medium text-gray-500 group-hover:text-blue-500">Telegram</p>
                  <p class="text-sm font-bold text-gray-900">@bright_cable</p>
                </div>
              </a>
            </div>

            <div
              class="mt-4 bg-white rounded-xl p-4 border border-gray-200 text-center shadow-sm flex-1 flex flex-col justify-center">
              <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">WeChat / 微信</h4>
              <div class="flex justify-center mb-3">
                <img src="/wechat.jpg" alt="WeChat QR" class="w-28 h-28 object-contain bg-gray-50 rounded"
                  onerror="this.src='https://ui-avatars.com/api/?name=We+Chat&background=059669&color=fff&size=128'">
              </div>
              <p class="text-gray-900 font-bold text-sm">扫一扫加好友</p>
              <div
                class="mt-2 inline-block px-3 py-1 bg-green-50 text-green-700 text-xs rounded-full font-mono border border-green-100">
                ID: Tini
              </div>
            </div>

            <div class="mt-auto pt-4 text-center">
              <span class="text-[10px] text-gray-300">工作时间: 8:00 - 22:00 (UTC+8)</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useToast } from '../composables/useToast';
import api from '../api/axios';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);
const { success, error } = useToast();

const activeTab = ref('upload');
const files = ref([]);
const textRemark = ref('');
const contactInfo = ref('');
const submitting = ref(false);

const close = () => emit('close');

// 文件处理
const handleFileSelect = (e) => {
  const selected = Array.from(e.target.files);
  files.value = [...files.value, ...selected];
};
const handleDrop = (e) => {
  const dropped = Array.from(e.dataTransfer.files);
  files.value = [...files.value, ...dropped];
};
const removeFile = (index) => {
  files.value.splice(index, 1);
};

// 提交逻辑
const handleSubmit = async () => {
  if (!contactInfo.value) return error('请填写您的联系方式');
  if (activeTab.value === 'upload' && files.value.length === 0) return error('请上传文件');
  if (activeTab.value === 'text' && !textRemark.value) return error('请填写需求描述');

  submitting.value = true;

  // 模拟 FormData (如果后端支持 upload/Inquiry)
  const formData = new FormData();
  formData.append('contact', contactInfo.value);
  formData.append('type', activeTab.value);
  if (activeTab.value === 'text') {
    formData.append('remark', textRemark.value);
  } else {
    files.value.forEach(f => formData.append('files', f));
  }

  try {
    // 模拟提交过程
    await new Promise(r => setTimeout(r, 1500));

    success('询价提交成功！经理将在 30 分钟内联系您。');

    // 重置
    files.value = [];
    textRemark.value = '';
    contactInfo.value = '';
    close();
  } catch (e) {
    error('提交失败，请尝试直接联系右侧方式');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>