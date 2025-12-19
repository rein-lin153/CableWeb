// src/api/product.js
import request from './request';

// 获取产品列表 (对应后端 GET /products/)
export function getProducts() {
  return request({
    url: '/products/',
    method: 'get'
  });
}

// 更新库存 (对应后端 PUT /products/{id})
export function updateProductStock(id, data) {
  return request({
    url: `/products/${id}`,
    method: 'put',
    data // data 格式应为 { stock: 100 } 或 { price: 200 }
  });
}