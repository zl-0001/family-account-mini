# 家庭记账项目

## 项目简介

一款面向家庭用户的智能记账工具，支持多成员协作、收支分类管理、预算控制和投资理财追踪。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vant UI（移动端组件库）
- ECharts（图表库）
- Pinia（状态管理）
- Vue Router（路由）
- Axios（HTTP请求）

### 后端
- Python 3.10+
- FastAPI（Web框架）
- SQLAlchemy（ORM）
- MySQL 8.0（数据库）
- Redis（缓存，可选）

## 项目结构

```
family-account-project/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   └── v1/
│   │   │       ├── auth.py      # 认证接口
│   │   │       ├── records.py   # 记账接口
│   │   │       └── ...
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py        # 配置文件
│   │   │   ├── database.py      # 数据库连接
│   │   │   └── security.py      # 安全认证
│   │   ├── models/         # 数据模型
│   │   │   ├── user.py
│   │   │   ├── record.py
│   │   │   └── ...
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # 入口文件
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试文件
│   ├── requirements.txt    # 依赖文件
│   └── .env.example        # 环境变量示例
│
├── frontend/               # 前端项目
│   └── family-account/
│       ├── src/
│       │   ├── views/      # 页面
│       │   │   ├── home/   # 首页
│       │   │   ├── record/ # 记账
│       │   │   ├── statistics/ # 统计
│       │   │   └── user/   # 我的
│       │   ├── components/ # 组件
│       │   ├── stores/     # 状态管理
│       │   ├── api/        # 接口
│       │   ├── utils/      # 工具
│       │   ├── router/     # 路由
│       │   └── styles/     # 样式
│       ├── public/
│       ├── package.json
│       └── vite.config.ts
│
└── docs/                   # 文档
```

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
copy .env.example .env
# 编辑 .env 文件，配置数据库信息

# 创建数据库
mysql -u root -p -e "CREATE DATABASE family_account CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API文档访问：http://localhost:8000/api/docs

### 2. 前端启动

```bash
# 进入前端目录
cd frontend/family-account

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问：http://localhost:5173

## 功能模块

### 已完成
- ✅ 项目架构设计
- ✅ 数据库模型设计
- ✅ 后端API框架搭建
- ✅ 前端项目初始化
- ✅ 用户认证模块

### 待开发
- ⏳ 记账核心功能
- ⏳ 分类管理
- ⏳ 账户管理
- ⏳ 统计分析
- ⏳ 预算管理
- ⏳ 投资理财
- ⏳ 家庭协作
- ⏳ 微信小程序适配

## 开发规范

### Git提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具相关

### 分支管理
- main: 主分支
- develop: 开发分支
- feature/*: 功能分支
- hotfix/*: 紧急修复分支

## 团队成员

- 产品经理：需求分析、原型设计
- UX设计师：UI设计、交互设计
- 技术负责人：架构设计、技术攻关
- 前端开发：Vue3页面开发
- 后端开发：FastAPI接口开发

## 更新日志

### v1.0.0 (2026-04-03)
- 项目初始化
- 基础架构搭建
