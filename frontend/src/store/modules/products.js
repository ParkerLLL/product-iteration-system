import { getProducts } from '../../api/products'

export default {
  state: {
    products: []
  },
  mutations: {
    SET_PRODUCTS(state, products) {
      state.products = products
    }
  },
  actions: {
    async fetchProducts({ commit }) {
      try {
        const response = await getProducts()
        commit('SET_PRODUCTS', response.data)
      } catch (error) {
        console.error('获取产品列表失败:', error)
      }
    }
  }
} 