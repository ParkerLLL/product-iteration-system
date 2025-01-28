<template>
  <div class="product-list-container">
    <div class="product-list">
      <div class="header">
        <h2>产品迭代管理</h2>
        <el-button type="primary" @click="showCreateDialog">新增产品</el-button>
      </div>

      <el-table :data="products" style="width: 100%">
        <el-table-column prop="name" label="产品名称" width="180" />
        <el-table-column prop="description" label="产品描述" width="250" />
        <el-table-column label="最新版本" width="200">
          <template #default="scope">
            <div v-if="scope.row.versions?.length">
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
          <el-form-item label="版本号" required>
            <el-input v-model="versionForm.version_number" placeholder="请输入版本号" />
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
  version_number: '',
  release_date: '',
  status: '规划中'
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
    version_number: '',
    release_date: '',
    status: '规划中'
  }
  versionDialogVisible.value = true
}

const saveVersion = async () => {
  try {
    if (!versionForm.value.version_number || !versionForm.value.release_date) {
      return ElMessage.warning('请填写完整信息')
    }

    // 在实际项目中，这里会调用后端 API
    // 现在我们直接更新前端状态
    const product = products.value.find(p => p.id === currentProductId.value)
    if (product) {
      if (!product.versions) {
        product.versions = []
      }
      product.versions.unshift({
        id: Date.now(), // 模拟 ID
        ...versionForm.value
      })
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
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 20px;
}

.product-list {
  width: 80%;
  min-height: 70vh;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.operation-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-table .cell) {
  padding: 8px;
  line-height: 1.5;
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