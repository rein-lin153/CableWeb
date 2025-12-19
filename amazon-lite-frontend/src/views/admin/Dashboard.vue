<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      
      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-orange-500">
        <div class="text-gray-500 text-sm font-medium uppercase tracking-wider">总注册客户</div>
        <div class="mt-2 flex items-baseline">
          <div class="text-3xl font-bold text-gray-900">1,248</div>
          <div class="ml-2 text-sm text-green-600 font-semibold">+12%</div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-blue-500">
        <div class="text-gray-500 text-sm font-medium uppercase tracking-wider">上架产品 SKU</div>
        <div class="mt-2 text-3xl font-bold text-gray-900">108</div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-red-500">
        <div class="text-gray-500 text-sm font-medium uppercase tracking-wider">库存告急 (<500m)</div>
        <div class="mt-2 text-3xl font-bold text-red-600">3</div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-500">
        <div class="text-gray-500 text-sm font-medium uppercase tracking-wider">今日询价数</div>
        <div class="mt-2 text-3xl font-bold text-gray-900">24</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white p-6 rounded-xl shadow-sm">
        <h3 class="font-bold text-gray-800 mb-4">近 7 天访问趋势</h3>
        <div class="h-64 bg-gray-50 rounded flex items-center justify-center text-gray-400 border border-dashed border-gray-200">
          [ 访问量折线图区域 ]
        </div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm">
        <h3 class="font-bold text-gray-800 mb-4">热销品类占比</h3>
        <div class="h-64 bg-gray-50 rounded flex items-center justify-center text-gray-400 border border-dashed border-gray-200">
          [ 饼图区域: 电力电缆 60%, 家装线 30% ]
        </div>
      </div>
    </div>
  </div>
</template>