<template>
  <div class="product-list-container">
    <div class="product-list">
      <div class="header">
        <h2>产品迭代管理</h2>
        <el-button type="primary" @click="showCreateDialog">新增产品</el-button>
      </div>
      <div class="table-container">
        <el-table :data="products" style="width: 100%">
          <el-table-column prop="name" label="产品名称" width="180" />
          <el-table-column prop="description" label="产品描述" width="250" />
          <el-table-column label="最新版本" width="200">
            <template #default="scope">
              <div v-if="scope.row.versions?.length">
                <div>迭代号: {{ scope.row.versions[0].iteration_number }}</div>
                <div>版本号: {{ scope.row.versions[0].version_number }}</div>
                <div>发布日期: {{ scope.row.versions[0].release_date }}</div>
                <div>状态: {{ scope.row.versions[0].status }}</div>
              </div>
              <span v-else>暂无版本</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="380">
            <template #default="scope">
              <div class="operation-buttons">
                <el-button @click="showVersions(scope.row)">版本</el-button>
                <el-button type="success" @click="addVersion(scope.row)">新增版本</el-button>
                <el-button type="primary" @click="editProduct(scope.row)">编辑</el-button>
                <el-button type="danger" @click="handleDelete(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑产品' : '新增产品'">
        <el-form :model="form" label-width="100px">
          <el-form-item label="产品名称" required>
            <el-input v-model="form.name" placeholder="请输入产品名称" />
          </el-form-item>
          <el-form-item label="产品描述">
            <el-input type="textarea" v-model="form.description" placeholder="请输入产品描述" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveProduct">确定</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="versionDialogVisible" :title="isEditVersion ? '编辑版本' : '新增版本'">
        <el-form :model="versionForm" label-width="100px">
          <el-form-item label="发布类型" required>
            <el-select v-model="versionForm.type">
              <el-option label="迭代" value="iteration" />
              <el-option label="版本" value="version" />
            </el-select>
          </el-form-item>
          <el-form-item label="迭代号" required>
            <el-input v-model="versionForm.iteration_number" placeholder="请输入迭代号，如: Sprint 2024-01" />
          </el-form-item>
          <el-form-item label="版本号" required>
            <el-input v-model="versionForm.version_number" placeholder="请输入版本号，如: v1.2.0" />
          </el-form-item>
          <el-form-item label="发布日期" required>
            <el-date-picker
              v-model="versionForm.release_date"
              type="date"
              placeholder="选择发布日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="状态" required>
            <el-select v-model="versionForm.status">
              <el-option label="规划中" value="规划中" />
              <el-option label="开发中" value="开发中" />
              <el-option label="测试中" value="测试中" />
              <el-option label="已发布" value="已发布" />
            </el-select>
          </el-form-item>
          <el-form-item label="版本概述">
            <el-input 
              type="textarea" 
              v-model="versionForm.summary" 
              :rows="3"
              placeholder="请输入版本概述"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="versionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveVersion">确定</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useStore()
const products = computed(() => store.state.products)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  name: '',
  description: ''
})
const currentId = ref(null)
const versionDialogVisible = ref(false)
const isEditVersion = ref(false)
const currentProductId = ref(null)
const versionForm = ref({
  type: 'iteration',
  iteration_number: '',
  version_number: '',
  release_date: '',
  status: '规划中',
  summary: '',
  requirements: [],
  removedRequirements: []
})

onMounted(() => {
  store.dispatch('fetchProducts')
})

const showCreateDialog = () => {
  isEdit.value = false
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

const editProduct = (product) => {
  isEdit.value = true
  currentId.value = product.id
  form.value = { ...product }
  dialogVisible.value = true
}

const saveProduct = async () => {
  try {
    if (!form.value.name.trim()) {
      return ElMessage.warning('产品名称不能为空')
    }

    if (isEdit.value) {
      await store.dispatch('updateProduct', {
        id: currentId.value,
        data: form.value
      })
    } else {
      await store.dispatch('createProduct', form.value)
    }
    dialogVisible.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  }
}

const handleDelete = (product) => {
  ElMessageBox.confirm(
    `确定要删除产品"${product.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await store.dispatch('deleteProduct', product.id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    // 用户点击取消
  })
}

const showVersions = (product) => {
  console.log('查看版本:', product)
}

const addVersion = (product) => {
  isEditVersion.value = false
  currentProductId.value = product.id
  versionForm.value = {
    type: 'iteration',
    iteration_number: '',
    version_number: '',
    release_date: '',
    status: '规划中',
    summary: '',
    requirements: [],
    removedRequirements: []
  }
  versionDialogVisible.value = true
}

const generateMockVersions = (productId) => {
  const versions = []
  // 生成迭代版本
  for (let i = 1; i <= 3; i++) {
    versions.push({
      id: Date.now() + i,
      type: 'iteration',
      iteration_number: `Sprint 2024-0${i}`,
      version_number: `v1.${i}.0`,
      release_date: `2024-0${i+2}-15`,
      status: i === 1 ? '开发中' : (i === 2 ? '规划中' : '已发布'),
      summary: `2024年第${i}个迭代版本，包含核心功能更新和bug修复`,
      requirements: [
        {
          issue_id: `REQ-${productId}-${i}01`,
          title: `核心功能${i}：用户管理模块优化`,
          status: i === 1 ? '开发中' : (i === 2 ? '待开发' : '开发完成'),
          priority: i,
          is_key_feature: true
        },
        {
          issue_id: `REQ-${productId}-${i}02`,
          title: `性能优化${i}：系统响应速度提升`,
          status: i === 1 ? '开发中' : (i === 2 ? '待开发' : '开发完成'),
          priority: i + 1
        }
      ],
      removedRequirements: [
        {
          issue_id: `REQ-${productId}-${i}03`,
          title: `已移除的功能${i}`,
          change_type: i === 1 ? '移除' : (i === 2 ? '推迟' : '变更'),
          change_reason: `由于${i === 1 ? '技术风险' : (i === 2 ? '优先级调整' : '需求变更')}`
        }
      ]
    })
  }
  
  // 生成正式版本
  versions.push({
    id: Date.now() + 4,
    type: 'version',
    iteration_number: 'Sprint 2024-Q1',
    version_number: 'v2.0.0',
    release_date: '2024-03-31',
    status: '规划中',
    summary: '2024年第一季度正式版本发布，包含重大功能更新',
    requirements: [
      {
        issue_id: `REQ-${productId}-401`,
        title: '新版本核心功能：AI助手集成',
        status: '待开发',
        priority: 1,
        is_key_feature: true
      }
    ],
    removedRequirements: []
  })
  
  return versions
}

const saveVersion = async () => {
  try {
    if (!versionForm.value.iteration_number || !versionForm.value.version_number || !versionForm.value.release_date) {
      return ElMessage.warning('请填写完整信息')
    }

    // 在实际项目中，这里会调用后端 API
    // 现在我们直接更新前端状态
    const product = products.value.find(p => p.id === currentProductId.value)
    if (product) {
      if (!product.versions) {
        product.versions = []
      }
      
      // 添加新版本到数组开头
      product.versions.unshift({
        id: Date.now(),
        ...versionForm.value,
        requirements: [],
        removedRequirements: []
      })

      // 如果是第一次添加版本，生成一些模拟数据
      if (product.versions.length === 1) {
        product.versions = generateMockVersions(product.id)
      }

      store.commit('SET_PRODUCTS', [...products.value])
    }

    versionDialogVisible.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}
</script>

<style scoped>
.product-list-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  padding: 24px;
  height: calc(100vh - 108px);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.product-list {
  width: 100%;
  height: 100%;
  background: white;
  padding: 0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-container {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-table .cell) {
  padding: 8px;
  line-height: 1.5;
  white-space: nowrap;
}

:deep(.el-table .el-table__cell[data-col-index="0"]) {
  width: 180px !important;
  min-width: 180px !important;
}

:deep(.el-table .el-table__cell[data-col-index="1"]) {
  width: 250px !important;
  min-width: 250px !important;
}

:deep(.el-table .el-table__cell[data-col-index="2"]) {
  width: 200px !important;
  min-width: 200px !important;
}

:deep(.el-table .el-table__cell[data-col-index="3"]) {
  width: 400px !important;
  min-width: 400px !important;
}

.operation-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
}

:deep(.el-button) {
  padding: 8px 15px;
  min-width: 80px;
}

/* 调整对话框样式 */
:deep(.el-dialog) {
  min-width: 500px;
}
</style> 