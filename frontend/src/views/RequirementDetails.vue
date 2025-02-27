<template>
  <div class="requirement-details-container">
    <div class="requirement-details">
      <!-- 头部选择区 -->
      <div class="header-section">
        <h2>版本/迭代 需求明细</h2>
        <div class="filter-container">
          <div class="filters">
            <el-select 
              v-model="selectedDepartment" 
              placeholder="选择一级部门"
              @change="handleDepartmentChange"
            >
              <el-option
                v-for="dept in departments"
                :key="dept.value"
                :label="dept.label"
                :value="dept.value"
              />
            </el-select>

            <el-select 
              v-model="selectedSubDepartment" 
              placeholder="选择二级部门"
              :disabled="!selectedDepartment"
              @change="handleSubDepartmentChange"
            >
              <el-option
                v-for="subDept in subDepartments"
                :key="subDept.value"
                :label="subDept.label"
                :value="subDept.value"
              />
            </el-select>

            <el-select 
              v-model="selectedProduct" 
              placeholder="选择项目空间"
              :disabled="!selectedSubDepartment"
              @change="handleProductChange"
            >
              <el-option
                v-for="product in filteredProducts"
                :key="product.code"
                :label="product.name || '未知产品'"
                :value="product.code"
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
              :placeholder="releaseType === 'iteration' ? '选择迭代' : '选择版本'"
              :disabled="!releaseType || !selectedProduct"
              @change="handleVersionChange"
            >
              <el-option
                v-for="ver in filteredVersionNumbers"
                :key="ver.id"
                :label="ver.version_name"
                :value="ver.id"
              >
                <span>{{ ver.version_name }}</span>
                <span class="version-date">{{ formatDate(ver.release_date) }}</span>
                <el-tag size="small" :type="getStatusType(ver.status)">
                  {{ ver.status }}
                </el-tag>
              </el-option>
            </el-select>

            <el-button 
              type="primary" 
              @click="handleSearch"
              :disabled="!selectedVersionNumber || !selectedProduct"
            >
              查询
            </el-button>

            <!-- 添加类型筛选复选框 -->
            <div class="type-filter">
              <el-checkbox v-model="showBugs" label="缺陷" />
              <el-checkbox v-model="showDemands" label="需求" />
            </div>

            <!-- 添加搜索框 -->
            <el-input
              v-model="searchKeyword"
              placeholder="搜索需求标题或ID"
              class="search-input"
              clearable
              @input="handleSearchInput"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </div>

      <!-- 版本信息展示区 -->
      <div v-if="selectedVersionNumber && shouldShowData" class="version-info">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="发布类型">
            {{ releaseType === 'iteration' ? '迭代' : '版本' }}
          </el-descriptions-item>
          <el-descriptions-item :label="releaseType === 'iteration' ? '迭代名称' : '版本名称'">
            {{ currentVersionInfo?.version_name }}
          </el-descriptions-item>
          <el-descriptions-item label="计划发布日期">
            {{ formatDate(currentVersionInfo?.release_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusType(currentVersionInfo?.status)">
              {{ getDisplayStatus(currentVersionInfo?.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 修改版本概述部分 -->
        <div class="version-summary">
          <h4>版本概述</h4>
          <el-input
            type="textarea"
            :model-value="currentVersionInfo?.description || ''"
            :rows="3"
            readonly
            placeholder="暂无版本概述"
            class="summary-textarea"
          />
        </div>
      </div>

      <!-- 需求列表区域 -->
      <div v-if="selectedVersionNumber && shouldShowData" class="requirements-section">
        <!-- 当前版本需求 -->
        <div class="requirement-group">
          <h3>
            <el-tag type="success" effect="dark">当前版本需求</el-tag>
            <span class="requirement-count">
              (共 {{ currentRequirements.length }} 项)
            </span>
            <!-- 添加导出按钮 -->
            <el-button 
              type="primary" 
              link
              @click="exportToExcel"
              :disabled="!currentRequirements.length"
            >
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
          </h3>
          <div class="table-wrapper">
            <el-table :data="currentRequirements">
              <el-table-column prop="number" label="需求ID" width="120" />
              <el-table-column prop="issue_type" label="类型" width="80">
                <template #default="scope">
                  <span>{{ getIssueTypeDisplay(scope.row.issue_type) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="需求标题" min-width="300">
                <template #default="scope">
                  <div class="requirement-title">
                    <span class="clickable-title" @click="showRequirementDetail(scope.row)">{{ scope.row.title }}</span>
                    <el-tag 
                      v-if="scope.row.priority === 'P1'" 
                      type="danger" 
                      effect="plain" 
                      size="small"
                    >
                      核心功能
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="status_cn" label="状态" width="120">
                <template #default="scope">
                  <span class="status-text">{{ scope.row.status_cn }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="priority_cn" label="优先级" width="100">
                <template #default="scope">
                  <el-tag 
                    :type="getPriorityType(scope.row.priority_cn)"
                    effect="plain"
                  >
                    {{ scope.row.priority_cn }}
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
              <el-table-column prop="number" label="需求ID" width="120" />
              <el-table-column prop="issue_type" label="类型" width="80">
                <template #default="scope">
                  <span>{{ getIssueTypeDisplay(scope.row.issue_type) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="需求标题" min-width="200" />
              <el-table-column prop="change_status" label="变更类型" width="120">
                <template #default="scope">
                  <el-tag 
                    :type="getChangeStatusType(scope.row.change_status)"
                    effect="dark"
                  >
                    {{ scope.row.change_status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="变更信息" min-width="200">
                <template #default="scope">
                  <div v-if="scope.row.previous_version">
                    从版本 {{ scope.row.previous_version }} 移出
                  </div>
                  <div v-if="scope.row.previous_sprint">
                    从迭代 {{ scope.row.previous_sprint }} 移出
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="当前位置" min-width="200">
                <template #default="scope">
                  <div v-if="scope.row.current_version">
                    当前在版本: {{ scope.row.current_version }}
                  </div>
                  <div v-if="scope.row.current_sprint">
                    当前在迭代: {{ scope.row.current_sprint }}
                  </div>
                  <div v-if="!scope.row.current_version && !scope.row.current_sprint">
                    未分配
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <!-- 未选择版本时的提示 -->
      <el-empty 
        v-else
        :description="selectedVersionNumber ? '请点击查询按钮查看需求明细' : '请选择产品和版本查看需求明细'"
      />
    </div>

    <!-- 添加需求详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="需求详情"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="requirement-detail-content">
        <div class="detail-item">
          <span class="label">标题：</span>
          <span class="value">{{ currentRequirement?.title }}</span>
        </div>
        <div class="detail-item">
          <span class="label">ISSUE ID：</span>
          <span class="value">{{ currentRequirement?.number }}</span>
        </div>
        <div class="detail-item">
          <span class="label">创建人：</span>
          <span class="value">{{ currentRequirement?.created_user}}</span>
        </div>
        <div class="detail-item">
          <span class="label">蓝鲸链接：</span>
          <el-button 
            type="primary" 
            link 
            @click="openDevopsLink(currentRequirement)"
          >
            请点击跳转到ISSUE详情页面
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElLoading } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'  // 添加 Download 图标
import { useRoute } from 'vue-router'
import * as XLSX from 'xlsx'  // 添加 XLSX 导入

const store = useStore()
const selectedProduct = ref(null)
const releaseType = ref(null)
const selectedVersionNumber = ref(null)
const selectedDepartment = ref(null)
const selectedSubDepartment = ref(null)

const route = useRoute()

// 从 store 获取产品列表
const departments = computed(() => {
  const rawData = store.state.products;
  if (!rawData || !rawData.data) return [];
  return rawData.data.map(dept => ({
    value: dept.name,
    label: dept.name
  }));
})

// 计算属性：获取子部门
const subDepartments = computed(() => {
  const rawData = store.state.products
  if (!rawData?.data || !selectedDepartment.value) return []

  const dept = rawData.data.find(d => d.name === selectedDepartment.value)
  return dept ? dept.sub_departments.map(subDept => ({
    value: subDept.name,
    label: subDept.name
  })) : []
})

// 计算属性：根据选择的子部门过滤项目空间
const filteredProducts = computed(() => {
  const rawData = store.state.products
  if (!rawData?.data || !selectedSubDepartment.value) return []

  const dept = rawData.data.find(d => d.name === selectedDepartment.value)
  if (!dept) return []

  const subDept = dept.sub_departments.find(sd => sd.name === selectedSubDepartment.value)
  return subDept ? subDept.projects.map(project => ({
    name: project.name, // 使用项目名称
    code: project.code,
    versions: project.versions || []
  })) : []
})

// 修改 products computed 属性为 allProducts
const allProducts = computed(() => {
  const rawData = store.state.products;
  if (!rawData?.data) return [];
  
  const processedProducts = [];
  rawData.data.forEach(department => {
    // 处理主部门下的项目
    department.projects?.forEach(project => {
      processedProducts.push({
        code: project.code,
        project_name: project.project_name,
        department: department.name,
        versions: project.versions
      });
    });

    // 处理子部门下的项目
    department.sub_departments?.forEach(subDept => {
      subDept.projects?.forEach(project => {
        processedProducts.push({
          code: project.code,
          project_name: project.project_name,
          department: `${department.name}-${subDept.name}`,
          versions: project.versions
        });
      });
    });
  });
  
  return processedProducts;
})

// 根据选中的产品和发布类型过滤版本
const filteredVersionNumbers = computed(() => {
  if (!selectedProduct.value || !releaseType.value) return [];
  
  const selectedProj = allProducts.value.find(p => p.code === selectedProduct.value);
  if (!selectedProj || !selectedProj.versions) return [];
  
  // 过滤版本
  return selectedProj.versions
    .filter(v => v.type === (releaseType.value === 'iteration' ? '迭代' : '版本'))
    .map(v => ({
      id: v.name,
      version_name: v.name,
      release_date: v.release_date,
      status: v.status,
      description: v.description,
      requirements: v.requirements || []
    }))
    .sort((a, b) => new Date(b.release_date) - new Date(a.release_date));
})

// 获取当前选中的版本信息
const currentVersionInfo = computed(() => {
  if (!selectedVersionNumber.value || !filteredVersionNumbers.value.length || !shouldShowData.value) return null;
  return filteredVersionNumbers.value.find(v => v.id === selectedVersionNumber.value);
})

// 修改计算属性，使用 store 中的状态
const shouldShowData = ref(false)

// 添加搜索相关的响应式变量和计算属性
const searchKeyword = ref('')

// 添加类型筛选的响应式变量
const showBugs = ref(true)
const showDemands = ref(true)

// 添加需求详情弹窗相关的响应式变量
const dialogVisible = ref(false)
const currentRequirement = ref(null)

// 获取当前版本的需求数据
const currentRequirements = computed(() => {
  if (!currentVersionInfo.value || !shouldShowData.value) return [];
  
  const requirements = currentVersionInfo.value.requirements || [];
  // console.log('原始需求数据:', requirements);  // 添加调试日志
  
  const filterCondition = releaseType.value === 'version' 
    ? ['存在版本中', '存在版本和迭代中']
    : ['存在迭代中', '存在版本和迭代中'];
  
  const filtered = requirements
    .filter(req => {
      const statusMatch = filterCondition.includes(req.change_status);
      const typeMatch = (showBugs.value && req.type === 'BUG') || 
                       (showDemands.value && req.type === 'DEMAND');
      return statusMatch && typeMatch;
    })
    .map(req => {
      console.log('处理需求:', req);  // 添加调试日志
      return {
        number: req.number,
        title: req.title,
        status: req.status,
        status_cn: req.status_cn || req.status,
        priority_cn: req.priority_cn || req.priority,
        priority: req.priority,
        issue_type: req.type,
        issue_id: req.id,  // 修改这里，使用 req.id 而不是 req.issue_id
        created_user: req.created_user
      };
    });

  console.log('处理后的需求列表:', filtered);  // 添加调试日志

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    return filtered.filter(req => 
      req.title.toLowerCase().includes(keyword) || 
      req.number.toLowerCase().includes(keyword)
    );
  }
    
  return filtered;
})

// 修改移除需求的获取逻辑
const removedRequirements = computed(() => {
  if (!currentVersionInfo.value || !shouldShowData.value) return [];
  
  const requirements = currentVersionInfo.value.requirements || [];
  const removedReqs = requirements.filter(req => {
    const hasPreviousVersion = req.previous_version === currentVersionInfo.value.version_name;
    const hasPreviousSprint = req.previous_sprint === currentVersionInfo.value.version_name;
    
    // 首先检查变更状态
    const statusMatch = releaseType.value === 'version'
      ? (hasPreviousVersion || req.change_status === '移出版本')
      : (hasPreviousSprint || req.change_status === '移出迭代');
      
    // 然后检查类型
    const typeMatch = (showBugs.value && req.type === 'BUG') || 
                     (showDemands.value && req.type === 'DEMAND');
    
    return statusMatch && typeMatch;
  });

  const mappedReqs = removedReqs.map(req => ({
    number: req.number,
    title: req.title,
    change_status: req.change_status,
    previous_version: req.previous_version,
    previous_sprint: req.previous_sprint,
    current_version: req.current_version,
    current_sprint: req.current_sprint,
    issue_type: req.type
  }));

  // 如果有搜索关键词，进行过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    return mappedReqs.filter(req => 
      req.title.toLowerCase().includes(keyword) || 
      req.number.toLowerCase().includes(keyword)
    );
  }

  return mappedReqs;
})

// 修改查询处理函数
const handleSearch = () => {
  if (!selectedVersionNumber.value) {
    ElMessage({
      message: '请选择版本或迭代',
      type: 'warning'
    })
    return
  }

  // 显示loading效果
  const loading = ElLoading.service({
    lock: true,
    text: '加载中...',
    background: 'rgba(255, 255, 255, 0.7)'
  })

  // 设置显示数据标志
  shouldShowData.value = true

  // 模拟异步操作
  setTimeout(() => {
    loading.close()
    ElMessage({
      message: '查询成功',
      type: 'success'
    })
  }, 500)
}

// 修改版本选择变化处理函数
const handleVersionChange = () => {
  shouldShowData.value = false;
}

// 修改处理部门选择变化的函数
const handleDepartmentChange = () => {
  selectedSubDepartment.value = null;
  selectedProduct.value = null;
  releaseType.value = null;
  selectedVersionNumber.value = null;
  shouldShowData.value = false;
  
  // 添加调试日志
  console.log('部门选择变化:', selectedDepartment.value);
}

// 修改处理二级部门选择变化的函数
const handleSubDepartmentChange = () => {
  selectedProduct.value = null;
  releaseType.value = null;
  selectedVersionNumber.value = null;
  shouldShowData.value = false;
}

// 修改处理产品选择变化
const handleProductChange = () => {
  console.log('产品选择变化:', selectedProduct.value); // 添加调试日志
  releaseType.value = null;
  selectedVersionNumber.value = null;
  shouldShowData.value = false;
}

// 修改状态样式映射
const getStatusType = (status) => {
  // 版本状态映射
  const versionStatusMap = {
    'UNPUBLISHED': '进行中',
    'UNOPENED': '未开启',
    'PUBLISHED': '已发布'
  };
  
  // 迭代状态映射
  const sprintStatusMap = {
    'COMPELETE': '已发布',
    'NOT_STARTED': '未开始',
    'ACTIVE': '进行中'
  };
  
  // 获取映射后的状态
  const mappedStatus = versionStatusMap[status] || sprintStatusMap[status] || status;
  
  // 状态样式映射
  const statusStyleMap = {
    '进行中': 'warning',
    '未开启': 'info',
    '已发布': 'success',
    '未开始': 'info'
  };
  
  return statusStyleMap[mappedStatus] || 'info';
}

// 添加状态显示转换函数
const getDisplayStatus = (status) => {
  const versionStatusMap = {
    'UNPUBLISHED': '进行中',
    'UNOPENED': '未开启',
    'PUBLISHED': '已发布'
  };
  
  const sprintStatusMap = {
    'COMPELETE': '已发布',
    'NOT_STARTED': '未开始',
    'ACTIVE': '进行中'
  };
  
  return versionStatusMap[status] || sprintStatusMap[status] || status;
}

const getRequirementStatusType = (status) => {
  const types = {
    '待开发': 'info',
    '开发中': 'warning',
    '开发完成': 'success',
    '已发布': 'success',
    '未开始': 'info'
  };
  return types[status] || 'info';
}

const getPriorityType = (priority) => {
  // 只保留基本的优先级映射
  if (priority?.includes('P0') || priority?.includes('紧急')) return 'danger';
  if (priority?.includes('P1') || priority?.includes('高')) return 'warning';
  if (priority?.includes('P2') || priority?.includes('中')) return 'primary';
  if (priority?.includes('P3') || priority?.includes('低')) return 'success';
  return 'info';
}

const getChangeStatusType = (status) => {
  const types = {
    '移除版本': 'danger',
    '移除迭代': 'warning',
    '存在版本中': 'success',
    '存在迭代中': 'success',
    '存在版本和迭代中': 'success',
    '不在版本和迭代中': 'info'
  };
  return types[status] || 'info';
}

const formatDate = (date) => {
  if (!date) return '';
  const formattedDate = new Date(date).toLocaleDateString();
  return formattedDate;
}

// 添加搜索输入处理函数
const handleSearchInput = () => {
  // 这里不需要额外的处理，因为我们使用了计算属性来过滤数据
  // 当 searchKeyword 改变时，计算属性会自动重新计算
}

// 添加类型显示转换函数
const getIssueTypeDisplay = (type) => {
  return type === 'BUG' ? '缺陷' : type === 'DEMAND' ? '需求' : type;
}

// 添加显示需求详情的方法
const showRequirementDetail = (requirement) => {
  currentRequirement.value = {
    ...requirement,
    created_user: requirement.created_user_display || requirement.created_user
  }
  dialogVisible.value = true
}

// 添加打开蓝鲸链接的方法
const openDevopsLink = (requirement) => {
  if (!requirement) return
  
  console.log('传入的requirement对象:', requirement)
  
  const projectCode = selectedProduct.value
  const baseUrl = 'https://devops.300624.cn/console/vteam/'
  let url = ''
  
  // 直接使用传入的 requirement 对象中的 issue_id
  const issueId = requirement.issue_id

  console.log('找到的issue_id:', issueId)

  if (!issueId) {
    console.log('未找到issue_id，当前requirement.number:', requirement.number)
    ElMessage.error('未找到对应的需求ID')
    return
  }
  
  if (requirement.issue_type === 'DEMAND') {
    url = `${baseUrl}${projectCode}/twDemand/demand?vmode=table&id=${issueId}`
  } else if (requirement.issue_type === 'BUG') {
    url = `${baseUrl}${projectCode}/twBug/IssueDetail?vmode=table&id=${issueId}`
  }
  
  console.log('生成的URL:', url)
  
  if (url) {
    window.open(url, '_blank')
  }
}

// 添加导出Excel功能
const exportToExcel = () => {
  try {
    // 准备导出数据
    const exportData = currentRequirements.value.map(req => {
      // 构建蓝鲸链接
      const baseUrl = 'https://devops.300624.cn/console/vteam/';
      let devopsUrl = '';
      if (req.issue_type === 'DEMAND') {
        devopsUrl = `${baseUrl}${selectedProduct.value}/twDemand/demand?vmode=table&id=${req.issue_id}`;
      } else if (req.issue_type === 'BUG') {
        devopsUrl = `${baseUrl}${selectedProduct.value}/twBug/IssueDetail?vmode=table&id=${req.issue_id}`;
      }

      return {
        '需求ID': req.number,
        '类型': getIssueTypeDisplay(req.issue_type),
        '需求标题': req.title,
        '状态': req.status_cn,
        '优先级': req.priority_cn,
        '创建人': req.created_user,
        '蓝鲸链接': devopsUrl
      };
    });

    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(exportData);

    // 设置列宽
    const colWidths = [
      { wch: 15 },  // 需求ID
      { wch: 8 },   // 类型
      { wch: 50 },  // 需求标题
      { wch: 12 },  // 状态
      { wch: 10 },  // 优先级
      { wch: 15 },  // 创建人
      { wch: 100 }  // 蓝鲸链接
    ];
    ws['!cols'] = colWidths;

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, '需求列表');

    // 生成文件名
    const fileName = `需求明细_${currentVersionInfo.value?.version_name || '未命名'}_${new Date().toLocaleDateString()}.xlsx`;

    // 下载文件
    XLSX.writeFile(wb, fileName);

    ElMessage({
      message: '导出成功',
      type: 'success'
    });
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败，请重试');
  }
}

onMounted(async () => {
  // 从路由参数中获取值
  const query = route.query;
  if (query.selectedDepartment) {
    selectedDepartment.value = query.selectedDepartment;
  }
  if (query.selectedSubDepartment) {
    selectedSubDepartment.value = query.selectedSubDepartment;
  }
  if (query.selectedProduct) {
    selectedProduct.value = query.selectedProduct;
  }
  if (query.releaseType) {
    releaseType.value = query.releaseType === 'iteration' ? 'iteration' : 'version';
  }
  if (query.selectedVersionNumber) {
    selectedVersionNumber.value = query.selectedVersionNumber;
  }
  
  // 添加对 fetchProducts 方法的调用
  try {
    await store.dispatch('fetchProducts');
    console.log('产品数据:', store.state.products);
  } catch (error) {
    console.error('获取产品数据失败:', error);
  }
  
  // 添加调试日志
  console.log('组件挂载时的部门:', selectedDepartment.value);
  
  // 如果有 autoSearch 参数，等待数据加载完成后自动触发查询
  if (query.autoSearch === 'true') {
    nextTick(() => {
      handleSearch();
    });
  }
});

// 监听路由变化
watch(
  () => route.query,
  (query) => {
    if (query.selectedDepartment) {
      selectedDepartment.value = query.selectedDepartment;
    }
    if (query.selectedSubDepartment) {
      selectedSubDepartment.value = query.selectedSubDepartment;
    }
    if (query.selectedProduct) {
      selectedProduct.value = query.selectedProduct;
    }
    if (query.releaseType) {
      releaseType.value = query.releaseType === 'iteration' ? 'iteration' : 'version';
    }
    if (query.selectedVersionNumber) {
      selectedVersionNumber.value = query.selectedVersionNumber;
    }
    
    if (query.autoSearch === 'true') {
      nextTick(() => {
        handleSearch();
      });
    }
  },
  { immediate: true }
);
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

.filter-container {
  /* background: #f8f9fa;
  padding: 16px;  */
  border-radius: 8px;
  margin-top: 16px;
}

.filters {
  display: flex;
  gap: 16px;
  align-items: flex-start;
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

.department-tag {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}

.version-date {
  margin: 0 8px;
  color: #909399;
  font-size: 12px;
}

:deep(.el-select) {
  width: 240px;
}

.filters {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.version-info {
  margin: 24px 0;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
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

:deep(.el-descriptions) {
  padding: 16px;
  background-color: white;
  border-radius: 4px;
}

:deep(.el-empty) {
  padding: 60px 0;
}

:deep(.el-button) {
  height: 32px;
  padding: 0 20px;
}

/* 添加搜索框样式 */
.search-input {
  width: 240px;
  margin-left: auto;  /* 将搜索框推到右侧 */
}

:deep(.el-input__prefix) {
  color: #909399;
}

/* 调整筛选器容器样式以适应搜索框 */
.filters {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

/* 添加类型筛选样式 */
.type-filter {
  display: flex;
  gap: 16px;
  align-items: center;
}

:deep(.el-checkbox) {
  margin-right: 0;
}

:deep(.el-checkbox__label) {
  font-size: 14px;
  color: #606266;
}

/* 添加需求详情弹窗样式 */
.requirement-detail-content {
  padding: 20px;
}

.detail-item {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}

.detail-item .label {
  width: 100px;
  color: #606266;
  font-size: 14px;
}

.detail-item .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
}

.clickable-title {
  cursor: pointer;
  color: #409eff;
}

.clickable-title:hover {
  text-decoration: underline;
}

:deep(.el-dialog__body) {
  padding: 0;
}
</style> 





