import { createStore } from 'vuex'

// 生成模拟数据的辅助函数
const generateMockData = () => {
    const products = []
    const productNames = ['智能家居系统', '移动支付平台', '企业协作工具', '数据分析平台']
    const requirementTitles = [
        '用户认证功能', '数据加密传输', '实时消息推送', '自动化部署',
        '性能监控面板', '多语言支持', '数据导出功能', '报表生成器',
        '用户行为分析', '权限管理系统', 'API网关集成', '自动化测试',
        '移动端适配', '离线模式支持', '数据同步功能', '自定义主题'
    ]
    const requirementStatus = ['待开发', '开发中', '开发完成']
    const changeTypes = ['移除', '推迟', '变更']
    const changeReasons = [
        '业务优先级调整',
        '技术方案需要重新评估',
        '资源配置调整',
        '客户需求变更',
        '合规性要求变更'
    ]

    // 生成产品
    productNames.forEach((name, productIndex) => {
        const versions = []
        // 每个产品生成7个版本
        for (let i = 0; i < 7; i++) {
            const versionNumber = `v${1 + Math.floor(i / 3)}.${i % 3}.${Math.floor(Math.random() * 5)}`
            const releaseDate = new Date(2024, 2 + Math.floor(i / 2), 1 + i * 5).toISOString().split('T')[0]

            // 生成当前版本的需求（8-12个）
            const requirements = []
            const requirementCount = 8 + Math.floor(Math.random() * 5)
            for (let j = 0; j < requirementCount; j++) {
                requirements.push({
                    id: `REQ-${productIndex + 1}-${i + 1}-${j + 1}`,
                    issue_id: `ISSUE-${1000 + j}`,
                    title: requirementTitles[Math.floor(Math.random() * requirementTitles.length)],
                    status: requirementStatus[Math.floor(Math.random() * requirementStatus.length)],
                    priority: 1 + Math.floor(Math.random() * 3),
                    is_key_feature: Math.random() > 0.7
                })
            }

            // 生成移除/变更的需求（2-4个）
            const removedRequirements = []
            const removedCount = 2 + Math.floor(Math.random() * 3)
            for (let j = 0; j < removedCount; j++) {
                removedRequirements.push({
                    id: `REM-${productIndex + 1}-${i + 1}-${j + 1}`,
                    issue_id: `ISSUE-${2000 + j}`,
                    title: requirementTitles[Math.floor(Math.random() * requirementTitles.length)],
                    change_type: changeTypes[Math.floor(Math.random() * changeTypes.length)],
                    change_reason: changeReasons[Math.floor(Math.random() * changeReasons.length)]
                })
            }

            const summaries = [
                '本版本主要关注用户体验优化和性能提升',
                '核心功能更新，提供更多自定义选项',
                '修复关键问题，提升系统稳定性',
                '新增多项创新功能，优化用户交互',
                '重要安全更新和功能增强'
            ]

            versions.push({
                id: productIndex * 10 + i + 1,
                version_number: versionNumber,
                release_date: releaseDate,
                status: i === 0 ? '已发布' :
                    i === 1 ? '测试中' :
                        i === 2 ? '开发中' : '规划中',
                requirements,
                removedRequirements,
                summary: summaries[Math.floor(Math.random() * summaries.length)] +
                    `，包含 ${requirements.length} 项新功能和改进，` +
                    `${removedRequirements.length} 项需求调整。`
            })
        }

        products.push({
            id: productIndex + 1,
            name: name,
            description: `这是${name}的产品描述，包含了核心功能特性介绍。`,
            created_at: '2024-01-01',
            updated_at: '2024-03-15',
            versions: versions
        })
    })

    return products
}

// 使用生成的模拟数据
const mockProducts = generateMockData()

// 从 localStorage 获取持久化的数据或使用默认数据
const getSavedProducts = () => {
    const saved = localStorage.getItem('products')
    return saved ? JSON.parse(saved) : mockProducts
}

export default createStore({
    state: {
        products: [],
        versions: [],
        requirements: [],
        calendarEvents: [] // 新增日历事件状态
    },
    mutations: {
        SET_PRODUCTS(state, products) {
            state.products = products
            // 保存到 localStorage
            localStorage.setItem('products', JSON.stringify(products))

            // 更新日历事件，确保所有版本都显示
            state.calendarEvents = products.flatMap(product =>
                (product.versions || []).map(version => ({
                    id: `${product.id}-${version.id}`,
                    title: `${product.name} ${version.version_number}`,
                    date: version.release_date,
                    extendedProps: {
                        productId: product.id,
                        productName: product.name,
                        versionId: version.id,
                        status: version.status,
                        version_number: version.version_number
                    },
                    allDay: true,
                    display: 'block'
                }))
            ).sort((a, b) => {
                // 首先按日期排序
                const dateCompare = new Date(a.date) - new Date(b.date)
                if (dateCompare !== 0) return dateCompare
                // 如果日期相同，按产品名和版本号排序
                const productCompare = a.extendedProps.productName.localeCompare(b.extendedProps.productName)
                if (productCompare !== 0) return productCompare
                return a.extendedProps.version_number.localeCompare(b.extendedProps.version_number)
            })
        },
        SET_VERSIONS(state, versions) {
            state.versions = versions
        },
        SET_REQUIREMENTS(state, requirements) {
            state.requirements = requirements
        }
    },
    actions: {
        // 模拟获取产品列表
        async fetchProducts({ commit }) {
            // 模拟 API 延迟
            await new Promise(resolve => setTimeout(resolve, 300))
            commit('SET_PRODUCTS', getSavedProducts())
        },
        async fetchVersions({ commit }, productId = null) {
            try {
                const url = productId ? `/versions/?product=${productId}` : '/versions/'
                const response = await api.get(url)
                commit('SET_VERSIONS', response.data)
            } catch (error) {
                console.error('Error fetching versions:', error)
            }
        },
        // 模拟创建产品
        async createProduct({ commit, state }, product) {
            await new Promise(resolve => setTimeout(resolve, 300))
            const newProduct = {
                id: state.products.length + 1,
                ...product,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            }
            commit('SET_PRODUCTS', [...state.products, newProduct])
            return newProduct
        },
        // 模拟更新产品
        async updateProduct({ commit, state }, { id, data }) {
            await new Promise(resolve => setTimeout(resolve, 300))
            const products = state.products.map(p =>
                p.id === id ? { ...p, ...data, updated_at: new Date().toISOString() } : p
            )
            commit('SET_PRODUCTS', products)
        },
        // 模拟删除产品
        async deleteProduct({ commit, state }, productId) {
            await new Promise(resolve => setTimeout(resolve, 300))
            const products = state.products.filter(p => p.id !== productId)
            commit('SET_PRODUCTS', products)
        }
    }
}) 