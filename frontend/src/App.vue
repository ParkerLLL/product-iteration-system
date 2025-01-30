<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Calendar, List } from '@element-plus/icons-vue'

const route = useRoute()
const currentPageTitle = computed(() => {
  const titles = {
    '/products': '产品管理',
    '/calendar': '发布日历',
    '/requirements': '需求明细'
  }
  return titles[route.path] || ''
})
</script>

<template>
  <div class="app-container">
    <el-menu
      mode="horizontal"
      :router="true"
      :default-active="$route.path"
      class="nav-menu"
    >
      <div class="logo">产品迭代系统</div>
      <el-menu-item index="/products">
        <el-icon><Document /></el-icon>
        <span>产品管理</span>
      </el-menu-item>
      <el-menu-item index="/calendar">
        <el-icon><Calendar /></el-icon>
        <span>发布日历</span>
      </el-menu-item>
      <el-menu-item index="/requirements">
        <el-icon><List /></el-icon>
        <span>需求明细</span>
      </el-menu-item>
    </el-menu>
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
/* 确保整个应用使用浅色主题 */
:root {
  color-scheme: light;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #f6f8fa !important;
  color: #333333 !important;
}

#app {
  height: 100vh;
  background-color: #f6f8fa !important;
}

.app-container {
  min-height: 100vh;
  background-color: #f6f8fa;
}

.nav-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: #fff !important;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  display: flex !important;
  height: 60px;
}

.logo {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  padding: 0 24px;
  height: 60px;
  line-height: 60px;
  white-space: nowrap;
  border-right: 1px solid #f0f0f0;
  width: fit-content;
}

.el-menu-item {
  font-size: 14px;
  height: 60px !important;
  line-height: 60px !important;
  padding: 0 24px !important;
}

.el-menu-item .el-icon {
  margin-right: 6px;
  font-size: 18px;
}

.main-content {
  padding: 72px 24px 24px; /* 减小顶部内边距 */
  max-width: 1600px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Element Plus 样式覆盖 */
.el-menu--horizontal {
  border-bottom: none !important;
  display: flex !important;
}

.el-menu--horizontal > .el-menu-item {
  float: none !important; /* 覆盖 Element Plus 的浮动 */
}

/* 其他全局样式 */
.el-card,
.el-button,
.el-input__wrapper,
.el-select-dropdown {
  border-radius: 8px !important;
}

.el-table {
  width: 100% !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

/* 响应式布局 */
@media screen and (max-width: 1600px) {
  .main-content {
    padding: 72px 20px 20px;
  }
}

@media screen and (max-width: 1200px) {
  .main-content {
    padding: 72px 16px 16px;
  }
  
  .nav-content {
    padding: 0 16px;
  }
}
</style>
