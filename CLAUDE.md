# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

家庭记账应用，前端使用 uni-app（Vue 3）微信小程序，后端使用 FastAPI + SQLAlchemy + MySQL/SQLite。支持多成员协作、收支分类管理、预算控制和投资理财追踪。

## 常用命令

### 后端（Python 3.10+）

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 微信小程序（Node.js）

```bash
cd family-account-mini

# 安装依赖
npm install

# 开发模式
npm run dev:mp-weixin

# 生产构建
npm run build:mp-weixin

# 类型检查
npm run type-check
```

构建产物在 `dist/build/mp-weixin`，用微信开发者工具导入。

## 项目架构

### 后端结构（`backend/app/`）

```
├── api/v1/           # API 路由处理（auth、records、categories、accounts、statistics）
├── core/              # 核心配置（config、database、security）
├── models/            # SQLAlchemy ORM 模型
├── schemas/           # Pydantic 请求/响应模型
├── services/          # 业务逻辑层
└── main.py            # FastAPI 入口
```

**核心模式：**
- 路由（API）→ 服务（Services）→ 模型（Models）三层架构
- 所有 API 路由前缀为 `/api/v1`
- 数据库：SQLite（默认）或 MySQL，通过 `.env` 中的 `DATABASE_URL` 配置
- 认证：JWT token（`python-jose`）+ 密码加密（`passlib[bcrypt]`）

### 微信小程序结构（`family-account-mini/src/`）

```
├── pages/              # 页面（home、record、statistics、user、login）
├── stores/             # 状态管理（uni.getStorageSync/setStorageSync）
├── api/                # 后端 API 调用封装
├── utils/request.ts    # 请求工具，含 JWT 拦截器
└── types/              # TypeScript 类型定义
```

**请求工具**：`utils/request.ts` 自动在请求头添加 `Authorization: Bearer <token>`，401 响应时自动跳转登录页。BASE_URL 硬编码，换环境需改此处。

## API 接口文档

所有接口前缀为 `/api/v1`，需认证的接口需在请求头携带 JWT token。

### 认证接口（`/api/v1/auth`）

| 方法 | 路径 | 描述 | 请求体 |
|------|------|------|--------|
| POST | `/auth/register` | 用户注册 | `{username, password, nickname?, phone?, email?}` |
| POST | `/auth/login` | 用户登录（OAuth2表单） | `username, password` |
| GET | `/auth/me` | 获取当前用户信息 | - |

**登录响应：**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 记账记录接口（`/api/v1/records`）

| 方法 | 路径 | 描述 | 查询参数 |
|------|------|------|----------|
| POST | `/records` | 创建记账记录 | - |
| GET | `/records` | 获取记录列表 | `start_date?, end_date?, record_type?, category_id?, skip?, limit?` |
| GET | `/records/statistics/monthly` | 获取月度统计 | `year, month` |
| GET | `/records/fixed` | 获取固定收支记录 | - |

**RecordCreate 请求体：**
```json
{
  "account_id": 1,
  "category_id": 1,
  "type": "expense",
  "amount": 100.00,
  "record_date": "2026-04-08",
  "remark": "午餐",
  "is_fixed": false,
  "fixed_cycle": null,
  "reimbursement_status": "none"
}
```

**type 可选值：** `income`（收入）、`expense`（支出）、`investment`（投资）

### 分类管理接口（`/api/v1/categories`）

| 方法 | 路径 | 描述 | 查询参数 |
|------|------|------|----------|
| GET | `/categories` | 获取分类列表 | `category_type?`（income/expense/investment） |
| POST | `/categories` | 创建自定义分类 | - |
| GET | `/categories/{id}` | 获取分类详情 | - |
| DELETE | `/categories/{id}` | 删除自定义分类 | - |

**CategoryCreate 请求体：**
```json
{
  "name": "餐饮",
  "type": "expense",
  "parent_id": null,
  "icon": "food",
  "color": "#FF6B6B",
  "is_fixed": false
}
```

### 账户管理接口（`/api/v1/accounts`）

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/accounts` | 获取账户列表 |
| POST | `/accounts` | 创建账户 |
| PUT | `/accounts/{id}` | 更新账户 |
| DELETE | `/accounts/{id}` | 删除账户 |

**AccountCreate 请求体：**
```json
{
  "name": "我的钱包",
  "type": "cash",
  "balance": 0,
  "icon": "wallet",
  "color": "#4ECDC4",
  "is_default": true
}
```

**type 可选值：** `cash`（现金）、`bank`（银行卡）、`alipay`（支付宝）、`wechat`（微信）、`credit_card`（信用卡）、`investment`（投资账户）

### 统计分析接口（`/api/v1/statistics`）

| 方法 | 路径 | 描述 | 查询参数 |
|------|------|------|----------|
| GET | `/statistics/monthly` | 获取月度统计 | `year, month` |
| GET | `/statistics/yearly` | 获取年度统计 | `year` |
| GET | `/statistics/category` | 获取分类统计 | `year, month, record_type?, parent_id?` |
| GET | `/statistics/trend` | 获取收支趋势 | `months?`（默认6） |

**MonthlyStatistics 响应：**
```json
{
  "income": 5000.00,
  "expense": 3000.00,
  "balance": 2000.00,
  "income_trend": 10.5,
  "expense_trend": -5.2,
  "budget_percent": 75.0,
  "categories": [
    {"category_id": 1, "name": "餐饮", "amount": 800, "percent": 26.7, "count": 15}
  ]
}
```

## 数据模型

### 核心实体关系

- **User**：用户表，含用户名、密码哈希、家庭ID、角色（member/admin）
- **Family**：家庭表，支持多成员协作
- **Account**：账户表（现金、银行卡、支付宝、微信、信用卡、投资账户）
- **Category**：分类表，支持父子分类（收入/支出/投资三大类）
- **Record**：记账记录表，含金额、日期、所属账户和分类
- **Budget**：预算表
- **Investment**：投资记录表
- **Insurance**：保险记录表

**Record 关键字段：** `type`（income/expense/investment）、`amount`（Decimal）、`is_fixed`（是否固定收支）、`fixed_cycle`（固定周期）、`reimbursement_status`（报销状态）

## 环境变量

后端 `.env` 文件：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./family_account.db` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | `your-secret-key-change-in-production` |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token 过期时间（分钟） | `10080`（7天） |
| `MYSQL_HOST` | MySQL 主机 | `localhost` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户 | `root` |
| `MYSQL_PASSWORD` | MySQL 密码 | - |
| `MYSQL_DATABASE` | MySQL 数据库名 | `family_account` |
| `WEIXIN_APPID` | 微信小程序 AppID | - |
| `WEIXIN_APPSECRET` | 微信小程序 AppSecret | - |

小程序 `family-account-mini/src/utils/request.ts` 中 `BASE_URL` 配置 API 基础路径。
