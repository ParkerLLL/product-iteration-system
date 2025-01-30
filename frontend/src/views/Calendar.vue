<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <h2 class="page-title">产品发布日历</h2>
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
    
    <!-- 版本明细表 -->
    <div v-if="currentDate" class="version-details">  
      <h3>{{ formatDate(currentDate) }}的版本计划</h3>
      <div v-if="currentDateVersions.length">
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

    <!-- 添加视图切换和过滤器 -->
    <div class="calendar-toolbar">
      <el-select
        v-model="selectedProducts"
        multiple
        collapse-tags
        placeholder="选择产品"
        @change="handleProductFilter"
      >
        <el-option
          v-for="product in products"
          :key="product.id"
          :label="product.name"
          :value="product.id"
        />
      </el-select>

      <el-select
        v-model="selectedStatus"
        multiple
        collapse-tags
        placeholder="选择状态"
        @change="handleStatusFilter"
      >
        <el-option
          v-for="status in statusOptions"
          :key="status"
          :label="status"
          :value="status"
        />
      </el-select>

      <el-button @click="exportCalendar">
        <el-icon><Download /></el-icon>
        导出日历
      </el-button>
    </div>

    <!-- 添加统计信息卡片 -->
    <div class="statistics-cards">
      <el-card v-for="stat in statistics" :key="stat.label" class="stat-card">
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </el-card>
    </div>

    <FullCalendar 
      ref="calendarRef"
      :options="calendarOptions"
      class="calendar"
      @error="handleError"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import zhCnLocale from '@fullcalendar/core/locales/zh-cn'
import { ElMessageBox } from 'element-plus'
import tippy from 'tippy.js'
import { Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

const store = useStore()
const calendarRef = ref(null)
const currentDate = ref(null)
const activeProducts = ref([]) // 当前展开的产品
const events = computed(() => store.state.calendarEvents)

// 获取当前选中日期的所有版本
const currentDateVersions = computed(() => {
  if (!currentDate.value) return []
  return store.state.products.flatMap(product => 
    (product.versions || [])
      .filter(version => version.release_date === currentDate.value)
      .map(version => ({
        ...version,
        productId: product.id,
        productName: product.name
      }))
  )
})

// 按产品分组的版本
const groupedVersions = computed(() => {
  const groups = {}
  currentDateVersions.value.forEach(version => {
    if (!groups[version.productId]) {
      groups[version.productId] = {
        productId: version.productId,
        productName: version.productName,
        versions: []
      }
    }
    groups[version.productId].versions.push(version)
  })
  return Object.values(groups)
})

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

// 添加过滤状态
const selectedProducts = ref([])
const selectedStatus = ref([])
const statusOptions = ['规划中', '开发中', '测试中', '已发布']

// 过滤事件
const filteredEvents = computed(() => {
  let filtered = events.value
  if (selectedProducts.value.length) {
    filtered = filtered.filter(event => 
      selectedProducts.value.includes(event.extendedProps.productId)
    )
  }
  if (selectedStatus.value.length) {
    filtered = filtered.filter(event => 
      selectedStatus.value.includes(event.extendedProps.status)
    )
  }
  return filtered
})

const calendarOptions = {
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: zhCnLocale,
  events: filteredEvents,
  dateClick: (info) => {
    currentDate.value = info.dateStr
    document.querySelectorAll('.fc-day-selected').forEach(el => {
      el.classList.remove('fc-day-selected')
    })
    info.dayEl.classList.add('fc-day-selected')
  },
  eventContent: (arg) => {
    try {
      return {
        html: `
          <div class="fc-event-main-content">
            <div class="event-title">
              <span class="product-name">${arg.event.extendedProps?.productName || ''}</span>
              <span class="version-number">${arg.event.extendedProps?.version_number || ''}</span>
            </div>
            <div class="event-status">
              <span class="status-badge status-${arg.event.extendedProps?.status || ''}">${arg.event.extendedProps?.status || ''}</span>
            </div>
          </div>
        `
      }
    } catch (error) {
      console.error('Error rendering event:', error)
      return {
        html: '<div class="fc-event-main-content">Error rendering event</div>'
      }
    }
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
const statistics = computed(() => [
  {
    label: '本月发布计划',
    value: events.value.filter(event => {
      const date = new Date(event.date)
      const now = new Date()
      return date.getMonth() === now.getMonth()
    }).length
  },
  {
    label: '规划中版本',
    value: events.value.filter(event => 
      event.extendedProps.status === '规划中'
    ).length
  },
  {
    label: '开发中版本',
    value: events.value.filter(event => 
      event.extendedProps.status === '开发中'
    ).length
  }
])

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
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  margin-top: 8px;
  color: #666;
}
</style> 