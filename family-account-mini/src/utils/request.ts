// 请求工具类 - 适配 UniApp
const BASE_URL = 'https://urchin-payment-celestial.ngrok-free.dev/api/v1'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

interface Response<T = any> {
  data: T
  statusCode: number
}

export const request = async <T = any>(options: RequestOptions): Promise<T> => {
  const { url, method = 'GET', data, header = {} } = options

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
      const errorMsg = (response.data as any)?.detail || '请求失败'
      throw new Error(errorMsg)
    }
  } catch (error: any) {
    uni.showToast({
      title: error.message || '网络请求失败',
      icon: 'none'
    })
    throw error
  }
}

export const get = <T = any>(url: string, params?: any): Promise<T> => {
  return request<T>({
    url,
    method: 'GET',
    data: params,
  })
}

export const post = <T = any>(url: string, data?: any): Promise<T> => {
  return request<T>({
    url,
    method: 'POST',
    data,
  })
}

export const put = <T = any>(url: string, data?: any): Promise<T> => {
  return request<T>({
    url,
    method: 'PUT',
    data,
  })
}

export const del = <T = any>(url: string): Promise<T> => {
  return request<T>({
    url,
    method: 'DELETE',
  })
}
