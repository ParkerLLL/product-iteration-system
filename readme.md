# Product Iteration System

一个用于管理产品迭代和需求的系统。

## 功能特性

- 产品管理：创建、编辑和删除产品
- 版本管理：管理产品的不同版本
- 发布日历：可视化展示各产品版本的发布计划
- 需求明细：查看各版本的需求变更情况

## 技术栈

### 前端
- Vue 3
- Vuex
- Vue Router
- Element Plus
- FullCalendar

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
│ │ ├── store/ # Vuex 状态管理
│ │ ├── router/ # 路由配置
│ │ └── components/# 通用组件
│ └── ...
├── backend/ # 后端 Django 项目（计划中）
│ ├── products/ # 产品管理应用
│ └── ...
└── README.md

## 开发计划

- [x] 前端基础功能实现
- [x] 产品管理界面
- [x] 版本发布日历
- [x] 需求明细查看
- [ ] 后端 API 开发
- [ ] 数据持久化
- [ ] 用户认证
- [ ] 权限管理

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)