# AGENTS.md

家庭记账应用。项目包含 `backend/`（FastAPI 后端）和 `family-account-mini/`（微信小程序，uni-app）。

## 后端（`backend/`）

### 启动

```bash
cd backend
venv\Scripts\activate          # Windows 虚拟环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/api/docs

### 配置

- `.env` 控制：`DATABASE_URL`（默认 SQLite）、`JWT_SECRET_KEY`、`WEIXIN_APPID`/`WEIXIN_APPSECRET`
- 当前默认使用 SQLite（`sqlite:///./family_account.db`），已存在 `family_account.db` 文件
- MySQL 为可选：设置 `MYSQL_*` 环境变量或改 `DATABASE_URL` 为 `mysql+pymysql://...`
- `database.py` 中 `implicit_returning=False` 是为兼容 SQLite，勿删
- `DEBUG=True` 时 CORS 允许所有来源
- `DEBUG` 环境变量需用 `field_validator` 处理，避免系统 `DEBUG=WARN` 覆盖

### 架构（三层）

```
api/v1/     → 路由（FastAPI router，prefix="/api/v1"）
services/   → 业务逻辑
models/     → SQLAlchemy ORM 模型
schemas/    → Pydantic 请求/响应 schema
core/       → config / database / security（JWT + bcrypt）
```

路由模块：auth, records, categories, accounts, statistics, budgets, families, investments

### 认证

- 登录使用 OAuth2 密码表单（`application/x-www-form-urlencoded`），非 JSON
- 微信登录：`POST /api/v1/auth/wechat-login`，传 `{code}` 后端调 `code2session` 换 openid
- JWT 过期 7 天（10080 分钟）

### 枚举值（`models/enums.py`）

- RecordType: `income` / `expense` / `investment`
- AccountType: `cash` / `bank` / `alipay` / `wechat` / `credit_card` / `investment`
- InvestmentType: `stock` / `fund` / `bond` / `deposit` / `other`
- FixedCycle: `daily` / `weekly` / `monthly` / `yearly`

### 数据库迁移

`alembic/versions/` 当前为空，未生成过迁移文件。`init_db()` 在启动时 `create_all` 建表。

### 测试

`tests/` 目录为空，无测试框架配置。

## 微信小程序（`family-account-mini/`）

### 技术栈

uni-app（Vue 3）+ TypeScript + SCSS，目标平台微信小程序。

### 开发命令

```bash
cd family-account-mini
npm run dev:mp-weixin     # 微信小程序开发模式
npm run build:mp-weixin   # 微信小程序生产构建
npm run type-check        # vue-tsc --noEmit 类型检查
```

构建产物在 `dist/` 目录，用微信开发者工具导入 `dist/build/mp-weixin`。

### API 基地址

`src/utils/request.ts` 中硬编码为 `http://192.168.1.61:8000/api/v1`。换环境需改此处。请求自动带 `Authorization: Bearer <token>`，401 自动跳登录页。

### 路径别名

`@/*` → `./src/*`（tsconfig.json）

### 页面结构

- 登录页为入口（`pages/login/index`），App.vue 中 `onShow` 检查登录态
- TabBar：首页 / 记账 / 统计 / 我的
- easycom 自动导入 `uni-*` 组件（`@dcloudio/uni-ui`）

### 状态

`stores/user.ts` 使用 `uni.getStorageSync`/`setStorageSync` 持久化 token 和用户信息，非 Pinia。

### 已知坑点

- **`conic-gradient` 不支持**：微信小程序 CSS 不支持 `conic-gradient`，uni-app 编译器会直接剔除。环形图用 Canvas 2D API 实现（`pages/statistics/index.vue`）
- **`getCurrentInstance()` 不能在异步回调中调用**：需在 setup 顶层捕获，或直接不用 `.in(instance)`（页面级不需要）
- **Canvas 2D 选择器**：`uni.createSelectorQuery().select('#id')` 直接用，页面级不需要 `.in()`
- **`uni.getSystemInfoSync()` 已废弃**：用 `uni.getWindowInfo().pixelRatio` 替代，需 try-catch
- **`uni.getUserProfile` 已废弃**（WeChat 基础库 3.x+）：生产环境返回"微信用户"，登录改用 `uni.login` + 后端 `wechat-login`
- **`position: fixed/sticky` 在小程序中有限支持**：分类页面用 flex 布局（`height: 100vh; overflow: hidden`）替代
- **`picker-view` 的 `:value` 绑定**：不能在 change 事件中立即更新，会导致滚动回弹，需分离绑定和回调状态

## 全局

- Git 分支：main / develop / feature/* / hotfix/*
- 提交格式：`feat:` / `fix:` / `docs:` / `style:` / `refactor:` / `test:` / `chore:`
- 完整 API 文档和需求说明分别在 `CLAUDE.md` 和 `docs/requirement.md`
