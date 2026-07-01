# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

家庭记账应用。后端 `backend/` 为 FastAPI + SQLAlchemy（SQLite 默认 / MySQL 可选）；前端 `family-account-mini/` 为 uni-app（Vue 3）微信小程序。支持多成员协作、收支分类管理、预算控制和投资理财追踪。

> 注：根目录 `README.md` 已过时（描述的是未实现的 Vue3+Vant 网页端），以本文件和 `AGENTS.md` 为准。

## 常用命令

### 后端（Python 3.10+，在 `backend/` 下执行）

```bash
venv\Scripts\activate                       # Windows 激活虚拟环境
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000   # 启动开发服务器
```

- API 文档：http://localhost:8000/api/docs （`docs_url="/api/docs"`，注意不是 `/docs`）
- 健康检查：`GET /health`
- **数据库迁移未实际使用**：`alembic/versions/` 为空，未生成过迁移文件。建表靠 `init_db()` → `Base.metadata.create_all()`，在 `startup` 事件中自动执行。改模型后重启即可生效，无需 `alembic upgrade head`。
- **无测试**：`backend/tests/` 为空，未配置测试框架。

### 微信小程序（Node.js，在 `family-account-mini/` 下执行）

```bash
npm install
npm run dev:mp-weixin     # 微信小程序开发模式（watch）
npm run build:mp-weixin   # 生产构建
npm run type-check        # vue-tsc --noEmit 类型检查
```

构建产物在 `dist/build/mp-weixin`，用微信开发者工具导入该目录。`package.json` 还包含其他平台（h5、mp-alipay 等）的 dev/build 脚本，但当前只面向微信小程序。

## 项目架构

### 后端三层架构（`backend/app/`）

```
api/v1/     → 路由（FastAPI router，统一 prefix="/api/v1"）
services/   → 业务逻辑
models/     → SQLAlchemy ORM 模型 + enums.py 枚举
schemas/    → Pydantic 请求/响应模型
core/       → config（pydantic-settings）/ database / security（JWT + bcrypt）
```

路由模块：`auth, records, categories, accounts, statistics, budgets, families, investments`（均在 `main.py` 中 `include_router` 注册）。

### 微信小程序结构（`family-account-mini/src/`）

```
pages/      页面（login 为入口；TabBar：首页/记账/统计/我的）
stores/     状态：用 uni.getStorageSync/setStorageSync 持久化，非 Pinia
api/        后端调用封装
utils/request.ts   请求工具（JWT 拦截器）
```

- 路径别名：`@/*` → `./src/*`（见 `tsconfig.json`）
- easycom 自动导入 `uni-*` 组件（`@dcloudio/uni-ui`）；图表用 `@qiun/ucharts`
- `App.vue` 的 `onShow` 检查登录态

## 关键约定与坑点

### 后端

- **认证**：登录 `POST /api/v1/auth/login` 使用 **OAuth2 密码表单**（`application/x-www-form-urlencoded`，字段 `username`/`password`），不是 JSON。微信登录走 `POST /api/v1/auth/wechat-login`，传 `{code}`，后端调 `code2session` 换 openid。JWT 过期 7 天（10080 分钟）。
- **`database.py` 中 `implicit_returning=False` 勿删**：为兼容 SQLite 必需。
- **DEBUG 行为**：`DEBUG=True` 时 CORS 允许 `["*"]`，并开启 SQLAlchemy `echo`。生产环境必须显式设置 `JWT_SECRET_KEY` 和 `CORS_ORIGINS`，否则启动告警。
- **`DEBUG` 环境变量用 `field_validator` 解析**：系统可能存在全局 `DEBUG=WARN`，直接当布尔读会出错，故 `config.py` 用 `mode="before"` 校验器把字符串转布尔。
- `DATABASE_URL` 默认 `sqlite:///./family_account.db`；切 MySQL 改为 `mysql+pymysql://...` 或配 `MYSQL_*` 变量。
- **`create_all` 不改已有表**：`init_db()` 的 `Base.metadata.create_all()` 只建新表，**不给已有表加列/改字段**。给已有模型加字段（如 `Budget.year`）后，重启不会自动同步表结构，必须手动执行 `ALTER TABLE ... ADD COLUMN ...`（sqlite/MySQL 语法不同），否则查询会抛 `no such column` → 接口 500。
- **重启后端务必杀干净旧进程**：Windows 上 `uvicorn --reload` 多次重启容易留下旧实例（多个进程同时监听 8000，旧实例跑旧代码 → 接口一直 500，但新代码在 TestClient 里却是好的，极难排查）。重启前先确认端口释放（git bash）：`for p in $(netstat -ano | grep ":8000" | grep LISTENING | awk '{print $NF}'); do taskkill //PID $p //T //F; done`

### 微信小程序

- **BASE_URL 硬编码**于 `src/utils/request.ts`（当前 `http://192.168.1.61:8000/api/v1`），换环境必须改此处。请求还会带 `ngrok-skip-browser-warning: true` 头（应对 ngrok 转发）；401 自动清 token 并 `reLaunch` 到 `/pages/login/index`。

### 小程序已知技术坑（实现相关功能前务必阅读）

- **`conic-gradient` 不支持**：微信小程序 CSS 不支持，uni-app 编译器会直接剔除。环形图改用 Canvas 2D API 实现（见 `pages/statistics/index.vue`）。
- **`getCurrentInstance()` 不能在异步回调中调用**：需在 setup 顶层捕获，或直接不用 `.in(instance)`（页面级不需要）。
- **Canvas 2D 选择器**：`uni.createSelectorQuery().select('#id')` 直接用，页面级不需要 `.in()`。
- **`uni.getSystemInfoSync()` 已废弃**：用 `uni.getWindowInfo().pixelRatio` 替代，需 try-catch。
- **`uni.getUserProfile` 已废弃**（基础库 3.x+）：生产环境返回"微信用户"，登录改用 `uni.login` + 后端 `wechat-login`。
- **`position: fixed/sticky` 在小程序中有限支持**：分类页用 flex 布局（`height: 100vh; overflow: hidden`）替代。
- **`picker-view` 的 `:value` 绑定**：不能在 change 事件中立即更新，会导致滚动回弹，需分离绑定和回调状态。
- **`uni.fields` 的 callback 在微信小程序不触发**：`createSelectorQuery().fields({...}, cb)` 的第二参数 cb 在 H5/App 可用，但编译到微信小程序底层 `wx.fields` 不认，callback **永远不会被调用**（症状：drawDonut 进了却拿不到节点）。Canvas 节点查询必须用 `.fields({...}).exec(cb)`（callback 放 exec），别为了消 type 报错改成 `.fields(..., cb)`。
- **Canvas 2D 节点获取要重试**：canvas 是原生组件，首次渲染时 `res[0].node` 可能还没 ready，取空直接 return 就什么都不画。`.fields({node:true}).exec` 后判空，空就 `setTimeout` 重试几次。
- **手写 store 的 ref 在模板不自动解包**：本项目 store 是手写的（非 Pinia），返回对象里的 `userInfo` 是 `Ref`。Vue 模板只对 **setup 顶层 ref** 自动解包，对象属性里的 ref（如 `userStore.userInfo`）**不解包**。组件里要用独立顶层 ref 接收：`const userInfo = ref<any>(store.userInfo.value)`，刷新时显式 `userInfo.value = res`；别用 `ref(storeRef)` 别名，也别直接绑 `store.userInfo?.xxx`。

## 枚举值参考（`backend/app/models/enums.py`）

- RecordType：`income` / `expense` / `investment`
- AccountType：`cash` / `bank` / `alipay` / `wechat` / `credit_card` / `investment`
- InvestmentType：`stock` / `fund` / `bond` / `deposit` / `other`
- InsuranceType：`life` / `health` / `accident` / `car` / `property` / `other`
- FixedCycle：`daily` / `weekly` / `monthly` / `yearly`
- ReimbursementStatus：`none` / `pending` / `done`
- UserRole：`owner`（家庭创建者）/ `admin` / `member`

## API 接口文档

所有接口前缀为 `/api/v1`，需认证的接口在请求头携带 `Authorization: Bearer <token>`。

### 认证（`/auth`）

| 方法 | 路径 | 描述 | 请求体 |
|------|------|------|--------|
| POST | `/auth/register` | 注册 | `{username, password, nickname?, phone?, email?}` |
| POST | `/auth/login` | 登录（**OAuth2 表单**，非 JSON） | form: `username, password` |
| POST | `/auth/wechat-login` | 微信登录 | `{code}` |
| GET | `/auth/me` | 当前用户信息 | - |

登录响应：`{ "access_token": "...", "token_type": "bearer" }`

### 记账记录（`/records`）

| 方法 | 路径 | 描述 | 查询参数 |
|------|------|------|----------|
| POST | `/records` | 创建记录 | - |
| GET | `/records` | 记录列表 | `start_date?, end_date?, record_type?, category_id?, skip?, limit?` |
| GET | `/records/statistics/monthly` | 月度统计 | `year, month` |
| GET | `/records/fixed` | 固定收支记录 | - |

RecordCreate 请求体：
```json
{
  "account_id": 1, "category_id": 1, "type": "expense", "amount": 100.00,
  "record_date": "2026-04-08", "remark": "午餐",
  "is_fixed": false, "fixed_cycle": null, "reimbursement_status": "none"
}
```
`type`：`income` / `expense` / `investment`

### 分类（`/categories`）

| 方法 | 路径 | 描述 | 查询参数 |
|------|------|------|----------|
| GET | `/categories` | 分类列表 | `category_type?`（income/expense/investment） |
| POST | `/categories` | 创建自定义分类 | - |
| GET | `/categories/{id}` | 分类详情 | - |
| DELETE | `/categories/{id}` | 删除自定义分类 | - |

CategoryCreate：`{name, type, parent_id?, icon?, color?, is_fixed?}`（支持父子分类）。

### 账户（`/accounts`）

GET 列表 / POST 创建 / PUT `{id}` 更新 / DELETE `{id}` 删除。

AccountCreate：`{name, type, balance?, icon?, color?, is_default?}`。`type`：`cash` / `bank` / `alipay` / `wechat` / `credit_card` / `investment`。

### 统计（`/statistics`）

| 方法 | 路径 | 描述 | 查询参数 |
|------|------|------|----------|
| GET | `/statistics/monthly` | 月度统计 | `year, month` |
| GET | `/statistics/yearly` | 年度统计 | `year` |
| GET | `/statistics/category` | 分类统计 | `year, month, record_type?, parent_id?` |
| GET | `/statistics/trend` | 收支趋势 | `months?`（默认6） |

MonthlyStatistics 响应：`{income, expense, balance, income_trend, expense_trend, budget_percent, categories:[{category_id, name, amount, percent, count}]}`

另有 `/budgets`、`/families`、`/investments` 三组路由，结构与上述一致。

## 数据模型

核心实体：`User`（含 family_id、role）、`Family`、`Account`、`Category`（父子）、`Record`、`Budget`、`Investment`、`InvestmentValue`、`Insurance`。Record 关键字段：`type`、`amount`(Decimal)、`is_fixed`、`fixed_cycle`、`reimbursement_status`。

## 环境变量（后端 `backend/.env`）

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./family_account.db` |
| `DEBUG` | 调试模式（CORS 全开 + SQL echo） | `False` |
| `JWT_SECRET_KEY` | JWT 签名密钥（生产必填） | 空 |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token 过期（分钟） | `10080`（7天） |
| `CORS_ORIGINS` | 允许来源（逗号分隔） | 空 |
| `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE` | MySQL 配置（可选） | localhost/3306/root/-/family_account |
| `WEIXIN_APPID` / `WEIXIN_APPSECRET` | 微信小程序凭证 | 空 |

需求说明文档见 `docs/requirement.md`。
