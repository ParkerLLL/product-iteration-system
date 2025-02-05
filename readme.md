# Product Iteration System

一个用于管理产品迭代和需求的系统。

## 最新更新

### 日历功能增强
- ✨ 添加日期选择器，支持快速跳转
- 📊 新增产品版本统计信息
- 🔍 支持按产品和状态筛选
- 📅 优化日历事件展示
- 💾 支持导出日历数据
- 🎨 全新的界面设计

## 功能特性

### 产品管理
- 创建、编辑和删除产品
- 管理产品版本信息
- 跟踪版本状态变更

### 版本日历
- 可视化展示发布计划
- 支持日期快速选择
- 版本状态一目了然
- 支持多维度筛选
- 统计信息实时展示
- 数据导出功能

### 需求管理
- 查看版本需求明细
- 需求变更追踪
- 核心功能标记
- 优先级管理

## 技术栈

### 前端
- Vue 3
- Vuex
- Vue Router
- Element Plus
- FullCalendar
- Tippy.js
- XLSX

### 后端（计划中）
- Django
- Django REST framework
- MySQL

## 开发环境设置

### 前端
bash
cd frontend
npm install
npm run dev
后端（计划中）

### 后端（计划中）
bash
cd backend
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

## 项目结构
product-iteration-system/
├── frontend/ # 前端 Vue 项目
│ ├── src/
│ │ ├── views/ # 页面组件
│ │ │ ├── Calendar.vue # 日历视图
│ │ │ ├── ProductList.vue # 产品列表
│ │ │ └── RequirementDetails.vue # 需求明细
│ │ ├── store/ # Vuex 状态管理
│ │ ├── router/ # 路由配置
│ │ └── components/# 通用组件
│ └── ...
├── backend/ # 后端 Django 项目（计划中）
│ ├── products/ # 产品管理应用
│ └── ...
└── README.md


## 开发计划

### 已完成
- [x] 前端基础功能实现
- [x] 产品管理界面
- [x] 版本发布日历
- [x] 需求明细查看
- [x] 日历功能增强
- [x] 界面优化

### 进行中
- [ ] 后端 API 开发
- [ ] 数据持久化
- [ ] 用户认证
- [ ] 权限管理

### 计划中
- [ ] 数据导入导出
- [ ] 批量操作功能
- [ ] 数据统计报表
- [ ] 移动端适配

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 更新日志

### [1.1.0] - 2025-01-30
- 优化日历视图展示
- 添加产品和状态筛选
- 新增统计信息展示
- 添加数据导出功能
- 改进整体界面样式

### [1.0.0] - 2025-01-27
- 初始版本发布
- 基础功能实现

## 许可证

[MIT License](LICENSE)