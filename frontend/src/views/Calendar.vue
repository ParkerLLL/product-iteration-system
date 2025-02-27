<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <h2 class="page-title">版本/迭代 预计发布日历</h2>
      <div class="calendar-legend">
        <div class="legend-item">
          <div class="legend-color today-color"></div>
          <span>今天</span>
        </div>
        <div class="legend-item">
          <div class="legend-color selected-color"></div>
          <span>选中的日期</span>
        </div>
        <div class="date-picker-wrapper">
          <el-date-picker
            v-model="currentDate"
            type="date"
            placeholder="选择日期"
            format="YYYY年MM月DD日"
            value-format="YYYY-MM-DD"
            :clearable="false"
            @change="handleDateChange"
          />
        </div>
      </div>
    </div>
    
    <!-- 添加筛选器 -->
    <div class="calendar-toolbar">
      <el-select v-model="selectedDepartment" placeholder="选择一级部门" @change="handleDepartmentChange">
        <el-option v-for="dept in departments" :key="dept.value" :label="dept.label" :value="dept.value" />
      </el-select>

      <el-select v-model="selectedSubDepartment" placeholder="选择二级部门" :disabled="!selectedDepartment" @change="handleSubDepartmentChange">
        <el-option v-for="subDept in subDepartments" :key="subDept.value" :label="subDept.label" :value="subDept.value" />
      </el-select>

      <el-select v-model="selectedProduct" placeholder="选择项目空间" :disabled="!selectedDepartment" @change="handleProductChange">
        <el-option v-for="product in filteredProducts" :key="product.code" :label="product.project_name" :value="product.code" />
      </el-select>

      <el-select v-model="releaseType" placeholder="选择发布类型" :disabled="!selectedRequirement">
        <el-option label="迭代" value="iteration" />
        <el-option label="版本" value="version" />
      </el-select>

      <el-select v-model="selectedVersionNumber" :placeholder="releaseType === 'iteration' ? '选择迭代' : '选择版本'" :disabled="!releaseType || !selectedRequirement" @change="handleVersionChange">
        <el-option v-for="ver in filteredVersionNumbers" :key="ver.id" :label="ver.version_name" :value="ver.id">
          <span>{{ ver.version_name }}</span>
          <span class="version-date">{{ formatDate(ver.release_date) }}</span>
          <el-tag size="small" :type="getStatusType(ver.status)">{{ ver.status }}</el-tag>
        </el-option>
      </el-select>

      <el-button type="primary" @click="handleSearch" :disabled="!selectedVersionNumber || !selectedRequirement">查询</el-button>
    </div>

    <!-- 版本明细表 -->
    <div v-if="currentDate" class="version-details">  
      <h3>{{ formatDate(currentDate) }}的版本计划</h3>
      <div v-if="currentDateVersionplan.length">
        <el-collapse v-model="activeProducts">
          <el-collapse-item 
            v-for="group in groupedVersions" 
            :key="group.productId"
            :title="group.productName"
            :name="group.productId"
          >
            <el-table 
              :data="group.versions"  
              style="width: 100%"
              :header-cell-style="{ 
                backgroundColor: '#f5f7fa',
                color: '#606266',
                fontWeight: 'bold',
                textAlign: 'center'
              }"
              :cell-style="{ textAlign: 'center' }"
            >
              <el-table-column prop="version_number" label="版本号" width="150" align="center" />
              <el-table-column prop="release_date" label="发布日期" width="150" align="center" />
              <el-table-column prop="status" label="状态" width="120" align="center">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
      <el-empty 
        v-else 
        description="当天没有版本发布" 
        :image-size="100"
      >
        <template #description>
          <p class="empty-text">{{ formatDate(currentDate) }} 没有版本发布计划</p>
        </template>
      </el-empty>
    </div>

    <!-- 添加统计信息卡片 -->
    <div class="statistics-cards">
      <el-card class="stat-card" style="flex: 1 1 100%;">
        <div class="stat-value">{{ statistics[0].value }}</div>
        <div class="stat-label">{{ statistics[0].label }}</div>
      </el-card>
    </div>
    <div class="statistics-cards">
      <el-card v-for="stat in statistics.slice(1)" :key="stat.label" class="stat-card">
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </el-card>
    </div>

    <FullCalendar 
      ref="calendarRef"
      :options="calendarOptions"
      class="calendar"
      @dateClick="handleDateClick"
      @error="handleError"
    />

    <!-- 弹窗 -->
    <el-dialog :visible.sync="dialogVisible" title="选中日期的版本计划">
      <template #default>
        <div v-if="currentDateFilteredVersions.length">
          <el-table :data="currentDateFilteredVersions" style="width: 100%">
            <el-table-column prop="title" label="版本名称" />
            <el-table-column prop="start" label="发布日期" />
            <el-table-column prop="extendedProps.status" label="状态" />
          </el-table>
        </div>
        <div v-else>
          <p>该日期没有版本计划。</p>
        </div>
      </template>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import zhCnLocale from '@fullcalendar/core/locales/zh-cn'
import { ElMessageBox } from 'element-plus'
import tippy from 'tippy.js'
import { Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { getProducts, getCalendarEvents } from '../api/products' // 导入 API 方法

const store = useStore()
const calendarRef = ref(null)
const currentDate = ref(null)
const activeProducts = ref([]) // 当前展开的产品
const products = ref([]) // 存储产品数据
const events = computed(() => store.state.calendarEvents)
const calendarEvents = ref([]) // 存储日历事件
const dialogVisible = ref(false) // 控制弹窗的显示状态

// 确保只声明一次 currentDateFilteredVersions
const currentDateFilteredVersions = computed(() => {
  if (!currentDate.value) return [];
  return calendarEvents.value.filter(event => event.start === currentDate.value);
});

// 获取产品列表
const fetchProducts = async () => {
  try {
    const response = await getProducts() // 调用获取产品的 API
    products.value = response.data // 假设返回的数据结构是 { data: [...] }
    console.log('获取的产品数据:', products.value);
  } catch (error) {
    console.error('获取产品数据失败:', error);
  }
};

// 获取日历事件
const fetchCalendarEvents = async () => {
  try {
    const events = await getCalendarEvents() // 调用获取日历事件的 API
    calendarEvents.value = events // 假设返回的数据结构是 { data: [...] }
    console.log('获取的日历事件:', calendarEvents.value);
  } catch (error) {
    console.error('获取日历事件失败:', error);
  }
};

// 在组件挂载时获取数据
onMounted(() => {
  fetchProducts();
  fetchCalendarEvents();
});

// 过滤器处理
const selectedProducts = ref([]);
const selectedStatus = ref([]);
const statusOptions = ['规划中', '开发中', '测试中', '已发布'];

const filteredEvents = computed(() => {
  let filtered = events.value;
  if (selectedProducts.value.length) {
    filtered = filtered.filter(event => 
      selectedProducts.value.includes(event.extendedProps.productId)
    );
  }
  if (selectedStatus.value.length) {
    filtered = filtered.filter(event => 
      selectedStatus.value.includes(event.extendedProps.status)
    );
  }
  return filtered;
});

// 按产品分组的版本
const groupedVersions = computed(() => {
  const groups = {};
  currentDateFilteredVersions.value.forEach(version => {
    if (!groups[version.productId]) {
      groups[version.productId] = {
        productId: version.productId,
        productName: version.productName,
        versions: []
      };
    }
    groups[version.productId].versions.push(version);
  });
  return Object.values(groups);
});

const getStatusType = (status) => {
  const types = {
    '规划中': 'warning',
    '开发中': 'primary',
    '测试中': 'success',
    '已发布': 'info'
  }
  return types[status] || 'default'
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

// 添加日期变化处理函数
const handleDateChange = (value) => {
  // 更新日历视图
  const calendarApi = calendarRef.value.getApi()
  calendarApi.gotoDate(value)
  
  // 移除之前的选中样式
  document.querySelectorAll('.fc-day-selected').forEach(el => {
    el.classList.remove('fc-day-selected')
  })
  
  // 添加新的选中样式
  const dayEl = document.querySelector(`[data-date="${value}"]`)
  if (dayEl) {
    dayEl.classList.add('fc-day-selected')
  }
}

// 获取版本/迭代的发布数据
const versions = computed(() => {
  return store.state.versions || []; // 假设版本数据存储在 Vuex 的 state 中
});

// 定义 selectedRequirement
const selectedRequirement = ref(null); // 或者根据需要使用 computed

// 递归函数来计算每个部门的版本总数
const calculateVersionCounts = (departments) => {
  const counts = {};
  departments.forEach(department => {
    const departmentName = department.name; // 获取一级部门名称
    const projects = department.projects || []; // 获取项目列表

    // 统计该部门的版本数量
    let versionCount = 0;
    projects.forEach(project => {
      versionCount += (project.versions ? project.versions.length : 0); // 统计版本数量
    });

    counts[departmentName] = versionCount; // 保存部门名称和版本数量
  });
  return counts;
};

// 计算每个部门的版本总数
const versionCountsByDepartment = computed(() => {
  return calculateVersionCounts(products.value); // 使用递归函数计算版本数量
});

const calendarOptions = {
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: zhCnLocale,
  events: events.value, // 确保这里是 events.value
  dateClick: (info) => {
    currentDate.value = info.dateStr;
    document.querySelectorAll('.fc-day-selected').forEach(el => {
      el.classList.remove('fc-day-selected');
    });
    info.dayEl.classList.add('fc-day-selected');
  },
  eventContent: (arg) => {
    const releaseDate = arg.event.extendedProps.release_date; // 获取事件的发布日期
    const versionCount = versionCountsByDepartment.value[releaseDate] || 0; // 获取该日期的版本总数

  
    return {
      html: `<div class='fc-event-main-content'>\n      
          <div class='event-title'>\n          
            <span>预计发布版本/迭代: ${versionCount} </span>\n      
              </div>\n      </div>`
    };
  },
  eventDidMount: (info) => {
    try {
      if (info.event.extendedProps?.status) {
        info.el.classList.add(`status-${info.event.extendedProps.status}`)
      }
      tippy(info.el, {
        content: `${info.event.extendedProps.productName} ${info.event.extendedProps.version_number}`,
        placement: 'top',
        theme: 'light-border'
      })
    } catch (error) {
      console.error('Error in eventDidMount:', error)
    }
  },
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  height: 'auto',
  dayMaxEvents: false,
  displayEventTime: false,
  eventOrder: 'title',
  dayCellDidMount: (arg) => {
    try {
      arg.el.style.height = '120px'
    } catch (error) {
      console.error('Error in dayCellDidMount:', error)
    }
  },
  handleWindowResize: true,
  windowResizeDelay: 200,
  eventClick: (info) => {
    // 点击事件时显示详细信息
    ElMessageBox.alert(
      `<div class="event-detail">
        <h4>${info.event.extendedProps.productName}</h4>
        <div class="detail-item">
          <span class="label">版本号：</span>
          <span>${info.event.extendedProps.version_number}</span>
        </div>
        <div class="detail-item">
          <span class="label">发布日期：</span>
          <span>${info.event.start.toLocaleDateString()}</span>
        </div>
        <div class="detail-item">
          <span class="label">当前状态：</span>
          <span class="status-${info.event.extendedProps.status}">${info.event.extendedProps.status}</span>
        </div>
      </div>`,
      '版本详情',
      {
        dangerouslyUseHTMLString: true,
        customClass: 'version-detail-dialog'
      }
    )
  }
}

// 添加错误处理
const handleError = (error) => {
  console.error('Calendar error:', error)
}

// 添加产品过滤处理
const handleProductFilter = (value) => {
  // 实现产品过滤逻辑
}

// 添加状态过滤处理
const handleStatusFilter = (value) => {
  // 实现状态过滤逻辑
}

// 添加统计计算
const statistics = computed(() => {
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();

  const totalVersions = calendarEvents.value.filter(event => {
    const eventDate = new Date(event.date);
    return eventDate.getMonth() === currentMonth && eventDate.getFullYear() === currentYear;
  }).length;

  const unopenedCount = calendarEvents.value.filter(event => event.extendedProps.status === 'UNOPENED').length;
  const publishedCount = calendarEvents.value.filter(event => event.extendedProps.status === 'PUBLISHED').length;
  const inProgressCount = calendarEvents.value.filter(event => event.extendedProps.status === 'UNPUBLISH').length;
  const notStartedIterations = calendarEvents.value.filter(event => event.extendedProps.type === 'iteration' && event.extendedProps.status === 'NOT_STARTED').length;
  const activeIterations = calendarEvents.value.filter(event => event.extendedProps.type === 'iteration' && event.extendedProps.status === 'ACTIVE').length;
  const completedIterations = calendarEvents.value.filter(event => event.extendedProps.type === 'iteration' && event.extendedProps.status === 'COMPLETE').length;

  return [
    { label: '预计发布日期的版本/迭代数量', value: totalVersions },
    { label: '未开始版本数', value: unopenedCount },
    { label: '已发布版本数', value: publishedCount },
    { label: '进行中版本数', value: inProgressCount },
    { label: '未开始迭代数', value: notStartedIterations },
    { label: '进行中迭代数', value: activeIterations },
    { label: '已完成迭代数', value: completedIterations },
  ];
});

const exportCalendar = () => {
  const data = events.value.map(event => ({
    '产品名称': event.extendedProps.productName,
    '版本号': event.extendedProps.version_number,
    '发布日期': event.date,
    '状态': event.extendedProps.status
  }))

  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '发布计划')
  XLSX.writeFile(wb, '产品发布日历.xlsx')
}

const selectedDepartment = ref(null);
const selectedSubDepartment = ref(null);
const selectedProduct = ref(null);
const releaseType = ref(null);
const selectedVersionNumber = ref(null);

const departments = computed(() => store.state.departments || []);
const subDepartments = computed(() => {
  return selectedDepartment.value ? store.state.subDepartments[selectedDepartment.value] || [] : [];
});
const filteredProducts = computed(() => {
  return selectedDepartment.value ? store.state.products.filter(product => product.department === selectedDepartment.value) : [];
});

const handleDepartmentChange = () => {
  selectedSubDepartment.value = null; // Reset sub-department when department changes
  selectedProduct.value = null; // Reset product when department changes
};

const handleSubDepartmentChange = () => {
  selectedProduct.value = null; // Reset product when sub-department changes
};

const handleProductChange = () => {
  // 处理产品变化逻辑
};

const handleVersionChange = () => {
  // 处理版本变化逻辑
};

const handleSearch = () => {
  // 根据选择的筛选器更新日历事件
};

// 定义 filteredVersionNumbers
const filteredVersionNumbers = computed(() => {
  return versions.value.filter(version => {
    // 根据需要添加过滤条件，例如根据 selectedProduct 或 releaseType
    return true; // 这里可以根据实际需求进行过滤
  });
});

// 处理日期点击事件
const handleDateClick = (info) => {
  currentDate.value = info.dateStr; // 获取选中的日期
  dialogVisible.value = true; // 显示弹窗
};
</script>

<style>
/* 基础样式重置 */
.calendar-view .fc {
  background: white;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  border-radius: 8px;
  padding: 20px;
}

/* 表格样式 */
.calendar-view .fc-theme-standard td,
.calendar-view .fc-theme-standard th {
  border: 1px solid #ddd;
}

/* 标题和按钮样式 */
.calendar-view .fc .fc-toolbar-title {
  color: #333;
  font-size: 1.5em;
}

.calendar-view .fc .fc-button {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.calendar-view .fc .fc-button:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.calendar-view .fc .fc-button-active {
  background-color: #337ecc !important;
  border-color: #337ecc !important;
}

/* 日期格子样式 */
.calendar-view .fc .fc-daygrid-day {
  min-height: 120px;
}

/* 事件样式 */
.calendar-view .fc-event {
  margin: 2px 0;
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.calendar-view .event-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.calendar-view .product-name {
  font-weight: bold;
  color: #333;
  font-size: 0.9em;
}

.calendar-view .version-number {
  color: #666;
  font-size: 0.85em;
  background: #f5f7fa;
  padding: 1px 4px;
  border-radius: 3px;
}

.calendar-view .event-status {
  display: flex;
  justify-content: flex-end;
}

.calendar-view .status-badge {
  font-size: 0.75em;
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

/* 状态样式 */
.calendar-view .status-规划中 {
  background-color: rgba(230, 162, 60, 0.1);
  border-left: 3px solid #e6a23c;
  color: #b88230;
}

.calendar-view .status-开发中 {
  background-color: rgba(64, 158, 255, 0.1);
  border-left: 3px solid #409eff;
  color: #2b88da;
}

.calendar-view .status-测试中 {
  background-color: rgba(103, 194, 58, 0.1);
  border-left: 3px solid #67c23a;
  color: #529b2e;
}

.calendar-view .status-已发布 {
  background-color: rgba(144, 147, 153, 0.1);
  border-left: 3px solid #909399;
  color: #606266;
}

/* 今天和选中日期样式 */
.calendar-view .fc-day-today {
  background-color: rgba(64, 158, 255, 0.1) !important;
}

.calendar-view .fc-day-selected {
  background-color: rgba(64, 158, 255, 0.2) !important;
}

/* 日期格子样式优化 */
.calendar-view .fc .fc-daygrid-day-frame {
  min-height: 120px;
  padding: 8px;
}

.calendar-view .fc .fc-daygrid-day-top {
  flex-direction: row;
  margin-bottom: 4px;
}

.calendar-view .fc .fc-daygrid-day-number {
  font-size: 0.9em;
  color: #606266;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 今天日期样式 */
.calendar-view .fc-day-today .fc-daygrid-day-number {
  background-color: #409eff;
  color: white;
}

/* 版本详情弹窗样式 */
.version-detail-dialog {
  max-width: 400px;
}

.event-detail {
  padding: 10px;
}

.event-detail h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.detail-item {
  margin: 8px 0;
  display: flex;
  align-items: center;
}

.detail-item .label {
  width: 80px;
  color: #666;
}
</style>

<style scoped>
.calendar-view {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  padding: 24px;
  min-height: calc(100vh - 40px);
  width: 100%;
  box-sizing: border-box;
}

.calendar-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.page-title {
  color: #000;
  font-weight: bold;
  text-align: center;
  font-size: 24px;
  margin: 0;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.calendar-legend {
  display: flex;
  align-items: center;
  gap: 24px;
  background: white;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-item span {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.today-color {
  background-color: rgba(64, 158, 255, 0.1);
  border: 2px solid #409eff;
}

.selected-color {
  background-color: rgba(255, 126, 34, 0.2);
}

.current-date {
  font-size: 14px;
  color: #606266;
  padding-left: 24px;
  border-left: 1px solid #dcdfe6;
}

.calendar {
  height: calc(100vh - 140px);
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.version-details {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.version-details h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
  font-size: 18px;
}

.empty-text {
  color: #909399;
  font-size: 14px;
  line-height: 1.5;
  margin: 10px 0;
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: bold;
  background-color: #f5f7fa;
  padding: 0 20px;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
}

:deep(.el-table) {
  margin-bottom: 10px;
}

:deep(.el-table__header) {
  font-weight: bold;
}

:deep(.el-tag) {
  min-width: 80px;
  text-align: center;
  font-size: 12px;
  padding: 0 12px;
  height: 24px;
  line-height: 24px;
}

:deep(.fc-event) {
  cursor: pointer;
  padding: 4px;
  margin: 2px 0;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

:deep(.fc-daygrid-event) {
  white-space: normal;
  background-color: #fff;
}

:deep(.event-title) {
  font-weight: bold;
  margin-bottom: 4px;
  font-size: 0.9em;
  line-height: 1.3;
  color: #333;
}

:deep(.event-status) {
  font-size: 0.8em;
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

:deep(.status-规划中) {
  background-color: rgba(230, 162, 60, 0.2);
  border-left: 3px solid #e6a23c;
  color: #b88230;
}

:deep(.status-开发中) {
  background-color: rgba(64, 158, 255, 0.2);
  border-left: 3px solid #409eff;
  color: #2b88da;
}

:deep(.status-测试中) {
  background-color: rgba(103, 194, 58, 0.2);
  border-left: 3px solid #67c23a;
  color: #529b2e;
}

:deep(.status-已发布) {
  background-color: rgba(144, 147, 153, 0.2);
  border-left: 3px solid #909399;
  color: #606266;
}

:deep(.fc-daygrid-day) {
  min-height: 120px !important;
}

:deep(.fc-daygrid-day-frame) {
  height: 100%;
  min-height: 120px;
}

:deep(.fc-daygrid-day-events) {
  padding: 4px;
  margin: 0 !important;
}

:deep(.fc-event) {
  margin: 2px 0 !important;
  border: none !important;
  background: white !important;
}

:deep(.fc-daygrid-event-harness) {
  margin: 2px 0 !important;
}

:deep(.fc-day-selected) {
  background-color: rgba(64, 158, 255, 0.2) !important;
}

/* 修改日历今天的样式 */
:deep(.fc-day-today) {
  background-color: rgba(64, 158, 255, 0.1) !important;
  position: relative;
}

:deep(.fc-day-today)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px solid #409eff;
  pointer-events: none;
}

/* 选中日期的样式 */
:deep(.fc-day-selected) {
  background-color: rgba(255, 179, 64, 0.2) !important;
}

.date-picker-wrapper {
  padding-left: 24px;
  border-left: 1px solid #dcdfe6;
}

:deep(.el-date-picker) {
  --el-datepicker-border-color: #dcdfe6;
  --el-datepicker-text-color: #606266;
  --el-datepicker-off-text-color: #909399;
  --el-datepicker-header-text-color: #303133;
}

:deep(.el-input__wrapper) {
  background-color: transparent;
  box-shadow: none !important;
}

:deep(.el-input__inner) {
  color: #606266;
  font-size: 14px;
  text-align: center;
}

:deep(.el-input__prefix) {
  color: #409eff;
}

.calendar-toolbar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.statistics-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.stat-card {
  flex: 1 1 200px; /* 自适应宽度 */
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style> 