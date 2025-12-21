// src/api/product.js
// 1. 修改导入路径，指向统一的 axios 实例
import api from './axios'; 

// 获取产品列表 (对应后端 GET /products/)
export function getProducts() {
  return api.get('/products/');
}

// 更新库存 (对应后端 PUT /products/{id})
export function updateProductStock(id, data) {
  return api.put(`/products/${id}`, data);
}