import { get, post, put, del, request } from '@/utils/request'

// 用户相关
export const login = (data: { username: string; password: string }) => {
  // OAuth2 密码模式需要 application/x-www-form-urlencoded 格式
  return request({
    url: '/auth/login',
    method: 'POST',
    data: `username=${encodeURIComponent(data.username)}&password=${encodeURIComponent(data.password)}`,
    header: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export const register = (data: {
  username: string
  password: string
  nickname?: string
}) => post('/auth/register', data)

export const getUserInfo = () => get('/auth/me')

export const updateUserInfo = (data: { nickname?: string; avatar?: string; phone?: string }) =>
  put('/auth/me', data)

// 微信登录
export const wechatLogin = (code: string, nickname?: string, avatar?: string) =>
  post('/auth/wechat-login', { code, nickname, avatar })

// 分类相关
export const getCategories = (categoryType?: string) =>
  get('/categories', categoryType ? { category_type: categoryType } : undefined)

export const createCategory = (data: {
  name: string
  type: string
  parent_id?: number
  icon?: string
  group?: string
}) => post('/categories', data)

export const updateCategory = (id: number, data: any) =>
  put(`/categories/${id}`, data)

export const deleteCategory = (id: number) => del(`/categories/${id}`)

export const reorderCategories = (items: { id: number; sort_order: number }[]) =>
  put('/categories/reorder', items)

// 账户相关
export const getAccounts = () => get('/accounts')

export const createAccount = (data: {
  name: string
  type: string
  balance?: number
  icon?: string
  color?: string
}) => post('/accounts', data)

export const updateAccount = (id: number, data: any) =>
  put(`/accounts/${id}`, data)

export const deleteAccount = (id: number) => del(`/accounts/${id}`)

// 记录相关
export const getRecords = (params?: {
  start_date?: string
  end_date?: string
  record_type?: string
  category_id?: number
}) => get('/records', params)

export const getFixedRecords = () => get('/records/fixed')

export const createRecord = (data: {
  account_id: number
  category_id: number
  type: string
  amount: number
  record_date: string
  remark?: string
  is_fixed?: boolean
}) => post('/records', data)

export const updateRecord = (id: number, data: any) =>
  put(`/records/${id}`, data)

export const deleteRecord = (id: number) => del(`/records/${id}`)

// 统计相关
export const getMonthlyStatistics = (year: number, month: number) =>
  get('/statistics/monthly', { year, month })

export const getCategoryStatistics = (
  year: number,
  month: number,
  recordType: string,
  parentId?: number | null
) => {
  const params: any = { year, month, record_type: recordType }
  if (parentId != null) params.parent_id = parentId
  return get('/statistics/category', params)
}

export const getTrend = (months = 6) => get('/statistics/trend', { months })

// 预算相关
export const getBudgets = (year: number, month: number) =>
  get('/budgets', { year, month })

export const createBudget = (data: {
  category_id: number
  year: number
  month: number
  amount: number
}) => post('/budgets', data)

export const updateBudget = (id: number, data: any) =>
  put(`/budgets/${id}`, data)

export const deleteBudget = (id: number) => del(`/budgets/${id}`)
