<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <h2>产品发布日历</h2>
      <div class="current-date" v-if="currentDate">
        当前选择: {{ formatDate(currentDate) }}
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

    <FullCalendar 
      ref="calendarRef"
      :options="calendarOptions"
      class="calendar"
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

const calendarOptions = {
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: zhCnLocale,
  events: events,
  dateClick: (info) => {
    currentDate.value = info.dateStr
    document.querySelectorAll('.fc-day-selected').forEach(el => {
      el.classList.remove('fc-day-selected')
    })
    info.dayEl.classList.add('fc-day-selected')
  },
  eventContent: (arg) => {
    return {
      html: `
        <div class="fc-event-main-content">
          <div class="event-title">${arg.event.title}</div>
          <div class="event-status">${arg.event.extendedProps.status}</div>
        </div>
      `
    }
  },
  eventDisplay: 'block',
  eventClassNames: (arg) => {
    return [`status-${arg.event.extendedProps.status}`]
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
    arg.el.style.height = '120px'
  }
}
</script>

<style scoped>
.calendar-view {
  padding: 20px;
  width: 90%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.current-date {
  font-size: 16px;
  color: #666;
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
</style> 