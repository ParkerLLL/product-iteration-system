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
            v-model="selectedVersion"
            placeholder="选择版本"
            :disabled="!selectedProduct"
          >
            <el-option
              v-for="version in filteredVersions"
              :key="version.id"
              :label="version.version_number"
              :value="version.id"
            >
              <span>{{ version.version_number }}</span>
              <span class="version-date">{{ version.release_date }}</span>
              <el-tag size="small" :type="getStatusType(version.status)">
                {{ version.status }}
              </el-tag>
            </el-option>
          </el-select>
        </div>
      </div>

      <!-- 版本信息展示区 -->
      <div v-if="selectedVersion" class="version-info">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="版本号">
            {{ currentVersion?.version_number }}
          </el-descriptions-item>
          <el-descriptions-item label="计划发布日期">
            {{ currentVersion?.release_date }}
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusType(currentVersion?.status)">
              {{ currentVersion?.status }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 修改版本概述部分 -->
        <div class="version-summary">
          <h4>版本概述</h4>
          <el-input
            type="textarea"
            :model-value="currentVersion?.summary || ''"
            :rows="3"
            readonly
            placeholder="暂无版本概述"
            class="summary-textarea"
          />
        </div>
      </div>

      <!-- 需求列表区域 -->
      <div v-if="selectedVersion" class="requirements-section">
        <!-- 当前版本需求 -->
        <div class="requirement-group">
          <h3>
            <el-tag type="success" effect="dark">当前版本需求</el-tag>
            <span class="requirement-count">
              (共 {{ currentRequirements.length }} 项)
            </span>
          </h3>
          <el-table :data="currentRequirements" style="width: 100%">
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

        <!-- 移除/变更的需求 -->
        <div class="requirement-group">
          <h3>
            <el-tag type="warning" effect="dark">移除/变更的需求</el-tag>
            <span class="requirement-count">
              (共 {{ removedRequirements.length }} 项)
            </span>
          </h3>
          <el-table :data="removedRequirements" style="width: 100%">
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
const selectedVersion = ref(null)

// 从 store 获取产品列表
const products = computed(() => store.state.products || [])

// 根据选中的产品过滤版本
const filteredVersions = computed(() => {
  if (!selectedProduct.value) return []
  const product = products.value.find(p => p.id === selectedProduct.value)
  return product?.versions || []
})

// 获取当前选中的版本信息
const currentVersion = computed(() => {
  if (!selectedVersion.value || !filteredVersions.value.length) return null
  const version = filteredVersions.value.find(v => v.id === selectedVersion.value)
  return version || null
})

// 获取当前版本的需求数据
const currentRequirements = computed(() => {
  if (!currentVersion.value) return []
  return currentVersion.value.requirements || []
})

// 获取移除/变更的需求数据
const removedRequirements = computed(() => {
  if (!currentVersion.value) return []
  return currentVersion.value.removedRequirements || []
})

// 处理产品选择变化
const handleProductChange = () => {
  selectedVersion.value = null
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
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 20px;
}

.requirement-details {
  width: 90%;
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 16px;
}

.version-info {
  margin-bottom: 24px;
}

.requirement-group {
  margin-bottom: 32px;
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

:deep(.el-table) {
  margin-top: 8px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: bold;
}

:deep(.el-empty) {
  padding: 40px 0;
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
</style> 