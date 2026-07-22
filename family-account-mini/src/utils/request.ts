// 请求工具类 - 适配 UniApp
const BASE_URL = 'http://127.0.0.1:8000/api/v1'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  // 静默请求：不弹「加载中」遮罩（用于后台刷新、分页加载等）
  silent?: boolean
}

interface Response<T = any> {
  data: T
  statusCode: number
}

// 全局 loading 计数器：并发请求只弹一个 loading，最后一个完成才关
let activeLoadingCount = 0
const showLoading = () => {
  activeLoadingCount++
  if (activeLoadingCount === 1) {
    uni.showLoading({ title: '加载中', mask: true })
  }
}
const hideLoading = () => {
  if (activeLoadingCount > 0) activeLoadingCount--
  if (activeLoadingCount === 0) {
    uni.hideLoading()
  }
}

export const request = async <T = any>(options: RequestOptions): Promise<T> => {
  const { url, method = 'GET', data, header = {}, silent = false } = options

  if (!silent) showLoading()

  // 获取 token
  const token = uni.getStorageSync('token')
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }
  header['Content-Type'] = header['Content-Type'] || 'application/json'
  header['ngrok-skip-browser-warning'] = 'true'

  try {
    const response: Response<T> = await uni.request({
      url: BASE_URL + url,
      method,
      data,
      header,
    })

    if (response.statusCode === 200) {
      return response.data
    } else if (response.statusCode === 401) {
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      uni.reLaunch({ url: '/pages/login/index' })
      throw new Error('请重新登录')
    } else {
      const d = response.data as any
      let errorMsg = '请求失败'
      if (typeof d?.detail === 'string') errorMsg = d.detail
      else if (Array.isArray(d?.detail)) errorMsg = d.detail.map((e: any) => e.msg).filter(Boolean).join('；')
      else if (d?.message) errorMsg = d.message
      throw new Error(errorMsg)
    }
  } catch (error: any) {
    uni.showToast({
      title: error.message || '网络请求失败',
      icon: 'none'
    })
    throw error
  } finally {
    if (!silent) hideLoading()
  }
}

export const get = <T = any>(url: string, params?: any, silent?: boolean): Promise<T> => {
  return request<T>({
    url,
    method: 'GET',
    data: params,
    silent,
  })
}

export const post = <T = any>(url: string, data?: any, silent?: boolean): Promise<T> => {
  return request<T>({
    url,
    method: 'POST',
    data,
    silent,
  })
}

export const put = <T = any>(url: string, data?: any, silent?: boolean): Promise<T> => {
  return request<T>({
    url,
    method: 'PUT',
    data,
    silent,
  })
}

export const del = <T = any>(url: string, silent?: boolean): Promise<T> => {
  return request<T>({
    url,
    method: 'DELETE',
    silent,
  })
}
