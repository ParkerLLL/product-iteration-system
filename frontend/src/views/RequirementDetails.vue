<template>
  <div class="requirement-details-container">
    <div class="requirement-details">
      <!-- 头部选择区 -->
      <div class="header-section">
        <h2>需求明细查看</h2>
        <div class="filters">
          <el-select 
            v-model="selectedProduct" 
            placeholder="选择产品"
            @change="handleProductChange"
          >
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            />
          </el-select>

          <el-select
            v-model="releaseType"
            placeholder="选择发布类型"
            :disabled="!selectedProduct"
          >
            <el-option label="迭代" value="iteration" />
            <el-option label="版本" value="version" />
          </el-select>

          <el-select
            v-model="selectedVersionNumber"
            :placeholder="releaseType === 'iteration' ? '选择迭代号' : '选择版本号'"
            :disabled="!releaseType"
          >
            <el-option
              v-for="ver in filteredVersionNumbers"
              :key="ver.id"
              :label="releaseType === 'iteration' ? ver.iteration_number : ver.version_number"
              :value="ver.id"
            >
              <span>{{ releaseType === 'iteration' ? ver.iteration_number : ver.version_number }}</span>
              <span class="version-date">{{ ver.release_date }}</span>
              <el-tag size="small" :type="getStatusType(ver.status)">
                {{ ver.status }}
              </el-tag>
            </el-option>
          </el-select>
        </div>
      </div>

      <!-- 版本信息展示区 -->
      <div v-if="selectedVersionNumber" class="version-info">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="发布类型">
            {{ releaseType === 'iteration' ? '迭代' : '版本' }}
          </el-descriptions-item>
          <el-descriptions-item :label="releaseType === 'iteration' ? '迭代号' : '版本号'">
            {{ releaseType === 'iteration' ? currentVersionInfo?.iteration_number : currentVersionInfo?.version_number }}
          </el-descriptions-item>
          <el-descriptions-item label="计划发布日期">
            {{ currentVersionInfo?.release_date }}
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusType(currentVersionInfo?.status)">
              {{ currentVersionInfo?.status }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 修改版本概述部分 -->
        <div class="version-summary">
          <h4>版本概述</h4>
          <el-input
            type="textarea"
            :model-value="currentVersionInfo?.summary || ''"
            :rows="3"
            readonly
            placeholder="暂无版本概述"
            class="summary-textarea"
          />
        </div>
      </div>

      <!-- 需求列表区域 -->
      <div v-if="selectedVersionNumber" class="requirements-section">
        <!-- 当前版本需求 -->
        <div class="requirement-group">
          <h3>
            <el-tag type="success" effect="dark">当前版本需求</el-tag>
            <span class="requirement-count">
              (共 {{ currentRequirements.length }} 项)
            </span>
          </h3>
          <div class="table-wrapper">
            <el-table :data="currentRequirements">
              <el-table-column prop="issue_id" label="需求ID" width="120" />
              <el-table-column prop="title" label="需求标题" min-width="300">
                <template #default="scope">
                  <div class="requirement-title">
                    <span>{{ scope.row.title }}</span>
                    <el-tag 
                      v-if="scope.row.is_key_feature" 
                      type="danger" 
                      effect="plain" 
                      size="small"
                    >
                      核心功能
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="120">
                <template #default="scope">
                  <el-tag :type="getRequirementStatusType(scope.row.status)">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="优先级" width="100">
                <template #default="scope">
                  <el-tag 
                    :type="getPriorityType(scope.row.priority)"
                    effect="plain"
                  >
                    P{{ scope.row.priority }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 移除/变更的需求 -->
        <div class="requirement-group">
          <h3>
            <el-tag type="warning" effect="dark">移除/变更的需求</el-tag>
            <span class="requirement-count">
              (共 {{ removedRequirements.length }} 项)
            </span>
          </h3>
          <div class="table-wrapper">
            <el-table :data="removedRequirements">
              <el-table-column prop="issue_id" label="需求ID" width="120" />
              <el-table-column prop="title" label="需求标题" min-width="300" />
              <el-table-column prop="change_type" label="变更类型" width="120">
                <template #default="scope">
                  <el-tag 
                    :type="getChangeType(scope.row.change_type)"
                    effect="dark"
                  >
                    {{ scope.row.change_type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="change_reason" label="变更原因" min-width="200" />
            </el-table>
          </div>
        </div>
      </div>

      <!-- 未选择版本时的提示 -->
      <el-empty 
        v-else
        description="请选择产品和版本查看需求明细"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const selectedProduct = ref(null)
const releaseType = ref(null)
const selectedVersionNumber = ref(null)

// 从 store 获取产品列表
const products = computed(() => store.state.products || [])

// 根据选中的产品和发布类型过滤版本
const filteredVersionNumbers = computed(() => {
  if (!selectedProduct.value || !releaseType.value) return []
  const product = products.value.find(p => p.id === selectedProduct.value)
  if (!product?.versions) return []
  
  // 根据发布类型筛选
  if (releaseType.value === 'iteration') {
    return product.versions.filter(v => v.iteration_number)
  } else {
    return product.versions.filter(v => v.version_number)
  }
})

// 获取当前选中的版本信息
const currentVersionInfo = computed(() => {
  if (!selectedVersionNumber.value || !filteredVersionNumbers.value.length) return null
  const versionInfo = filteredVersionNumbers.value.find(v => v.id === selectedVersionNumber.value)
  if (!versionInfo) return null
  
  return versionInfo
})

// 获取当前版本的需求数据
const currentRequirements = computed(() => {
  if (!currentVersionInfo.value) return []
  return currentVersionInfo.value.requirements || []
})

// 获取移除/变更的需求数据
const removedRequirements = computed(() => {
  if (!currentVersionInfo.value) return []
  return currentVersionInfo.value.removedRequirements || []
})

// 处理产品选择变化
const handleProductChange = () => {
  releaseType.value = null
  selectedVersionNumber.value = null
}

// 状态样式映射
const getStatusType = (status) => {
  if (!status) return 'default'
  switch (status) {
    case '规划中': return 'warning'
    case '开发中': return 'primary'
    case '测试中': return 'success'
    case '已发布': return 'info'
    default: return 'default'
  }
}

const getRequirementStatusType = (status) => {
  if (!status) return 'info'
  switch (status) {
    case '开发完成': return 'success'
    case '开发中': return 'primary'
    case '待开发': return 'warning'
    default: return 'info'
  }
}

const getPriorityType = (priority) => {
  if (!priority) return 'info'
  const priorityNum = Number(priority)
  switch (priorityNum) {
    case 1: return 'danger'
    case 2: return 'warning'
    case 3: return 'info'
    default: return 'info'
  }
}

const getChangeType = (type) => {
  if (!type) return 'info'
  switch (type) {
    case '移除': return 'danger'
    case '推迟': return 'warning'
    case '变更': return 'info'
    default: return 'info'
  }
}
</script>

<style scoped>
.requirement-details-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  padding: 24px;
  height: calc(100vh - 108px);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  min-width: 1000px;
}

.requirement-details {
  width: 100%;
  height: 100%;
  background: white;
  padding: 0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

/* 固定头部区域 */
.header-section {
  flex-shrink: 0;
  margin-bottom: 24px;
}

/* 固定版本信息区域 */
.version-info {
  flex-shrink: 0;
  margin-bottom: 24px;
}

/* 需求列表可滚动区域 */
.requirements-section {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  margin-right: -8px; /* 补偿padding-right造成的宽度增加 */
}

/* 设置滚动条样式 */
.requirements-section::-webkit-scrollbar {
  width: 6px;
}

.requirements-section::-webkit-scrollbar-thumb {
  background-color: #909399;
  border-radius: 3px;
}

.requirements-section::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

.filters {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.requirement-group {
  margin-bottom: 32px;
  width: 100%;
  min-width: 1000px;
}

.requirement-group h3 {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.requirement-count {
  color: #909399;
  font-size: 14px;
}

.requirement-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-select) {
  width: 200px;
}

:deep(.version-date) {
  margin: 0 8px;
  color: #909399;
}

:deep(.el-descriptions) {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: 20px;
}

:deep(.el-table) {
  width: 100%;
  min-width: 1000px;
}

:deep(.el-table .cell) {
  white-space: nowrap;
}

:deep(.el-table .el-table__cell[data-col-index="0"]) {
  width: 120px !important;
  min-width: 120px !important;
}

:deep(.el-table .el-table__cell[data-col-index="1"]) {
  width: 300px !important;
  min-width: 300px !important;
}

:deep(.el-table .el-table__cell[data-col-index="2"]) {
  width: 120px !important;
  min-width: 120px !important;
}

:deep(.el-table .el-table__cell[data-col-index="3"]) {
  width: 100px !important;
  min-width: 100px !important;
}

.version-summary {
  margin-top: 16px;
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 4px;
}

.version-summary h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
}

.summary-textarea {
  width: 100%;
}

:deep(.el-textarea__inner) {
  background-color: #fff;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.el-empty) {
  padding: 120px 0;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 24px 0;
  width: 100%;
  min-width: 1000px;
  box-sizing: border-box;
}

:deep(.el-empty__description) {
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.main-content {
  overflow-x: auto;
  width: 100%;
}
</style> 