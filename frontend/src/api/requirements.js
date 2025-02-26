import api from './config'

// 获取需求列表
export const getRequirements = () => api.get('/requirements/')

// 获取指定版本的需求列表
export const getVersionRequirements = (versionId) => api.get(`/versions/${versionId}/requirements/`)

// 创建需求
export const createRequirement = (data) => api.post('/requirements/', data)

// 更新需求
export const updateRequirement = (id, data) => api.put(`/requirements/${id}/`, data)

// 删除需求
export const deleteRequirement = (id) => api.delete(`/requirements/${id}/`)

// 批量更新需求
export const batchUpdateRequirements = (data) => api.post('/requirements/batch-update/', data)

// 获取需求变更历史
export const getRequirementHistory = (requirementId) => api.get(`/requirements/${requirementId}/history/`) 