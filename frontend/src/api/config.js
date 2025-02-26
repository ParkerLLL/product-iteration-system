import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
    baseURL: 'http://localhost:8000/api',  // 后端API的基础URL
    timeout: 30000,  // 增加超时时间到30秒
    headers: {
        'Content-Type': 'application/json',
    },
    // 允许跨域请求携带cookie
    withCredentials: true
})

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 在这里可以添加token等认证信息
        return config
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
api.interceptors.response.use(
    response => {
        return response
    },
    error => {
        console.error('API Error:', error)
        
        // 处理错误响应
        if (error.response) {
            // 服务器返回了错误状态码
            switch (error.response.status) {
                case 400:
                    ElMessage.error('请求参数错误')
                    break
                case 401:
                    ElMessage.error('未授权，请登录')
                    break
                case 403:
                    ElMessage.error('拒绝访问')
                    break
                case 404:
                    ElMessage.error('请求的资源不存在')
                    break
                case 500:
                    ElMessage.error('服务器内部错误')
                    break
                default:
                    ElMessage.error(`未知错误: ${error.response.status}`)
            }
        } else if (error.request) {
            // 请求已发出，但没有收到响应
            ElMessage.error('网络错误，请检查后端服务是否正常运行')
        } else {
            // 请求配置出错
            ElMessage.error('请求配置错误')
        }
        return Promise.reject(error)
    }
)

export default api 