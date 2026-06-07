<template>
  <view class="login-container">
    <view class="login-header">
      <text class="title">家庭记账</text>
      <text class="subtitle">轻松管理家庭收支</text>
    </view>

    <view class="login-form">
      <view class="form-item">
        <input
          v-model="form.username"
          type="text"
          placeholder="请输入用户名"
          class="input"
        />
      </view>
      <view class="form-item">
        <input
          v-model="form.password"
          type="password"
          password
          placeholder="请输入密码"
          class="input"
        />
      </view>

      <button class="login-btn" type="primary" @click="handleLogin" :loading="loading">
        登录
      </button>
      <button class="register-btn" type="default" @click="goRegister">
        注册账号
      </button>
      <button class="wechat-btn" type="default" @click="handleWechatLogin">
        微信登录
      </button>
      <view v-if="loading" class="loading-mask">
        <text class="loading-text">正在登录...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { login as loginApi, wechatLogin, getUserInfo } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const form = ref({
  username: '',
  password: '',
})

const handleLogin = async () => {
  if (!form.value.username) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!form.value.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res: any = await loginApi({
      username: form.value.username,
      password: form.value.password,
    })
    userStore.setToken(res.access_token)
    const userInfo: any = await getUserInfo()
    userStore.setUserInfo(userInfo)
    uni.switchTab({ url: '/pages/home/index' })
  } catch (error: any) {
    uni.showToast({ title: error.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const goRegister = () => {
  uni.navigateTo({ url: '/pages/login/register' })
}

const handleWechatLogin = async () => {
  loading.value = true
  try {
    uni.showLoading({ title: '正在登录...' })

    const loginRes: any = await uni.login({ provider: 'weixin' })
    if (!loginRes.code) {
      uni.hideLoading()
      throw new Error('微信登录失败')
    }

    const res: any = await wechatLogin(loginRes.code)
    userStore.setToken(res.access_token)

    const userInfo: any = await getUserInfo()
    userStore.setUserInfo(userInfo)

    uni.hideLoading()
    uni.switchTab({ url: '/pages/home/index' })
  } catch (error: any) {
    uni.hideLoading()
    uni.showToast({ title: error.message || '微信登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  padding: 100rpx 50rpx;
}

.login-header {
  text-align: center;
  margin-bottom: 100rpx;

  .title {
    display: block;
    font-size: 60rpx;
    font-weight: bold;
    color: #fff;
    margin-bottom: 20rpx;
  }

  .subtitle {
    display: block;
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

.login-form {
  background: #fff;
  border-radius: 20rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 30rpx;

  .input {
    height: 90rpx;
    border: 1px solid #eee;
    border-radius: 10rpx;
    padding: 0 30rpx;
    font-size: 28rpx;
  }
}

.login-btn {
  width: 100%;
  height: 90rpx;
  line-height: 90rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 45rpx;
  font-size: 32rpx;
  margin-bottom: 30rpx;
}

.register-btn {
  width: 100%;
  height: 90rpx;
  line-height: 90rpx;
  background: #fff;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 45rpx;
  font-size: 32rpx;
}

.wechat-btn {
  width: 100%;
  height: 90rpx;
  line-height: 90rpx;
  background: #07C160;
  color: #fff;
  border-radius: 45rpx;
  font-size: 32rpx;
  margin-top: 20rpx;
}

.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-text {
  color: #fff;
  font-size: 32rpx;
  background: rgba(0, 0, 0, 0.6);
  padding: 30rpx 60rpx;
  border-radius: 16rpx;
}
</style>
