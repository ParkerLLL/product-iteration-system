import axios from 'axios'

const state = {
  data: [],
  loading: false,
  error: null
}

const mutations = {
  SET_REQUIREMENTS(state, requirements) {
    state.data = requirements
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  }
}

const actions = {
  async fetchVersionRequirements({ commit }, { versionName, releaseType }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      // 根据发布类型选择不同的 API 端点
      const endpoint = releaseType === 'version' 
        ? `/api/requirements/version/${versionName}/`
        : `/api/requirements/sprint/${versionName}/`
      
      const response = await axios.get(endpoint)
      commit('SET_REQUIREMENTS', response.data)
    } catch (error) {
      console.error('获取需求数据失败:', error)
      commit('SET_ERROR', error.message)
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  getRequirementsByVersion: (state) => (versionName) => {
    return state.data.filter(req => 
      req.current_version === versionName || 
      req.previous_version === versionName
    )
  },
  
  getRequirementsBySprint: (state) => (sprintName) => {
    return state.data.filter(req => 
      req.current_sprint === sprintName || 
      req.previous_sprint === sprintName
    )
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 