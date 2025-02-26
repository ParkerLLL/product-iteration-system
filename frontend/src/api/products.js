import api from './config'

// 获取产品列表
export const getProducts = () => api.get('/products/')

// 创建产品
export const createProduct = (data) => api.post('/products/', data)

// 更新产品
export const updateProduct = (id, data) => api.put(`/products/${id}/`, data)

// 删除产品
export const deleteProduct = (id) => api.delete(`/products/${id}/`)

// 获取产品版本列表
export const getProductVersions = (productId) => api.get(`/products/${productId}/versions/`)

// 创建产品版本
export const createVersion = (productId, data) => api.post(`/products/${productId}/versions/`, data)

// 更新产品版本
export const updateVersion = (versionId, data) => api.put(`/versions/${versionId}/`, data)

// 删除产品版本
export const deleteVersion = (versionId) => api.delete(`/versions/${versionId}/`)

// 获取版本列表
export const getVersions = (productId) => api.get(`/versions/?product=${productId}`)

// 获取需求列表
export const getRequirements = (versionId) => api.get(`/requirements/?version=${versionId}`)

// 获取日历事件
export const getCalendarEvents = async () => {
  const response = await api.get('/products/calendar_events/?include=localprojects.department,localprojects.project_name,localprojects.project_code,products_localproject.department');
  return response.data; // 直接返回事件数据
};

// 获取项目空间信息
export const getProjectInfo = async (projectCode) => {
  try {
    const response = await api.get(`/products_localproject/?project_code=${projectCode}`);
    return response.data[0]; // 假设返回的是一个数组，取第一个元素
  } catch (error) {
    console.error(`Error fetching project info for code ${projectCode}:`, error);
    throw error; // 抛出错误以便在调用时处理
  }
}; 