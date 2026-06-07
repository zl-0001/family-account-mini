<template>
  <view class="register-container">
    <view class="register-form">
      <view class="form-title">注册账号</view>

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
          placeholder="请输入密码（至少6位）"
          class="input"
        />
      </view>
      <view class="form-item">
        <input
          v-model="form.nickname"
          type="text"
          placeholder="请输入昵称（可选）"
          class="input"
        />
      </view>

      <button class="register-btn" type="primary" @click="handleRegister" :loading="loading">
        注册
      </button>
      <button class="back-btn" type="default" @click="goBack">
        返回登录
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { register as registerApi } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const form = ref({
  username: '',
  password: '',
  nickname: '',
})

const handleRegister = async () => {
  if (!form.value.username) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!form.value.password || form.value.password.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await registerApi({
      username: form.value.username,
      password: form.value.password,
      nickname: form.value.nickname || undefined,
    })
    uni.showToast({ title: '注册成功，请登录', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  uni.navigateBack()
}
</script>

<style scoped lang="scss">
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 100rpx 50rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.register-form {
  background: #fff;
  border-radius: 20rpx;
  padding: 60rpx 40rpx;
  width: 100%;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 40rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 60rpx;
  color: #333;
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

.register-btn {
  width: 100%;
  height: 90rpx;
  line-height: 90rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 45rpx;
  font-size: 32rpx;
  margin-bottom: 30rpx;
}

.back-btn {
  width: 100%;
  height: 90rpx;
  line-height: 90rpx;
  background: #fff;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 45rpx;
  font-size: 32rpx;
}
</style>
