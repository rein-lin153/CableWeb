<template>
  <div>
    <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <div class="bg-orange-100 p-2 rounded-lg text-orange-600">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
        </div>
        <div>
          <div class="text-xs text-gray-500 uppercase font-bold tracking-wider">今日基准铜价</div>
          <div class="text-xl font-mono font-bold text-gray-900 flex items-center gap-2">
            ¥72,300 <span class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-medium">+1.2%</span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-3 w-full md:w-auto">
        <button class="flex-1 md:flex-none bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors">
          调整全站售价
        </button>
        <button class="flex-1 md:flex-none bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors">
          下载昨日报表
        </button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">待处理询价 (BOM)</div>
        <div class="flex justify-between items-end">
          <span class="text-3xl font-bold text-gray-900">5</span>
          <span class="text-xs text-orange-600 font-medium bg-orange-50 px-2 py-1 rounded">急需报价</span>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">待发货订单</div>
        <div class="flex justify-between items-end">
          <span class="text-3xl font-bold text-gray-900">12</span>
          <span class="text-xs text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded">2 单超时</span>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">本月销售额</div>
        <div class="flex justify-between items-end">
          <span class="text-2xl font-bold text-gray-900">¥1.2M</span>
          <span class="text-xs text-green-600 font-medium">↑ 8%</span>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div class="text-gray-400 text-xs font-bold uppercase mb-2">活跃配送车辆</div>
        <div class="flex justify-between items-end">
          <span class="text-3xl font-bold text-gray-900">4</span>
          <span class="text-xs text-gray-400">/ 6 辆</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <h3 class="font-bold text-gray-800">最新询价与订单</h3>
          <router-link to="/admin/orders" class="text-xs text-orange-600 hover:underline">查看全部</router-link>
        </div>
        <div class="divide-y divide-gray-100">
          <div class="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
                BOM
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">金边大厦三期项目 - 清单询价</p>
                <p class="text-xs text-gray-500">客户: 陈经理 (138****0000) • 10分钟前</p>
              </div>
            </div>
            <button class="px-3 py-1.5 bg-orange-600 text-white text-xs rounded hover:bg-orange-500">立即报价</button>
          </div>
          <div class="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold text-xs">
                ORD
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">#ORD-20250501-8821</p>
                <p class="text-xs text-gray-500">金额: ¥45,000 • 待确认合同</p>
              </div>
            </div>
            <button class="px-3 py-1.5 border border-gray-300 text-gray-600 text-xs rounded hover:bg-gray-50">查看详情</button>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200 bg-red-50/50">
          <h3 class="font-bold text-red-800">库存预警 (Low Stock)</h3>
        </div>
        <div class="p-4 space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div>
              <div class="text-sm font-bold text-gray-900">YJV 4x240mm²</div>
              <div class="text-xs text-gray-500">当前: 120米</div>
            </div>
            <span class="text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded">缺货</span>
          </div>
           <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div>
              <div class="text-sm font-bold text-gray-900">BV 2.5mm² 红色</div>
              <div class="text-xs text-gray-500">当前: 20卷</div>
            </div>
            <span class="text-xs font-bold text-orange-600 bg-orange-100 px-2 py-1 rounded">紧张</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>