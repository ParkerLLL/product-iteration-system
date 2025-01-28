<script setup>
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem } from 'element-plus'
</script>

<template>
  <div class="app-container">
    <el-menu
      mode="horizontal"
      router
      :default-active="$route.path"
      class="nav-menu"
    >
      <el-menu-item index="/products">产品管理</el-menu-item>
      <el-menu-item index="/calendar">发布日历</el-menu-item>
      <el-menu-item index="/requirements">需求明细</el-menu-item>
    </el-menu>
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.nav-menu {
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.main-content {
  padding: 0 20px;
}
</style>
