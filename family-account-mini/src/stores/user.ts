import { ref } from 'vue'

interface UserInfo {
  id: number
  username: string
  nickname: string
  avatar?: string
  role: string
  family_id?: number | null
}

const userInfo = ref<UserInfo | null>(null)
const token = ref<string>('')

export const useUserStore = () => {
  // 从本地存储恢复
  const initFromStorage = () => {
    const storedToken = uni.getStorageSync('token')
    const storedUserInfo = uni.getStorageSync('userInfo')
    if (storedToken) {
      token.value = storedToken
      userInfo.value = storedUserInfo
    }
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    uni.setStorageSync('token', newToken)
  }

  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    uni.setStorageSync('userInfo', info)
  }

  const login = (newToken: string, info: UserInfo) => {
    setToken(newToken)
    setUserInfo(info)
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
  }

  const isLoggedIn = () => !!token.value

  const isAdmin = () => userInfo.value?.role === 'admin'

  // 初始化
  initFromStorage()

  return {
    userInfo,
    token,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    setToken,
    setUserInfo,
  }
}
