<template>
  <view class="user-container">
    <!-- 用户信息 -->
    <view class="user-info">
      <view class="avatar">
        <text>{{ userInfo?.nickname?.[0] || userInfo?.username?.[0] || 'U' }}</text>
      </view>
      <view class="info">
        <text class="nickname">{{ userInfo?.nickname || userInfo?.username || '用户' }}</text>
        <text class="username">@{{ userInfo?.username }}</text>
      </view>
    </view>

    <!-- 菜单列表 -->
    <view class="menu-list">
      <view class="menu-item" @click="editNickname">
        <text class="menu-icon">👤</text>
        <text class="menu-text">昵称</text>
        <text class="menu-val">{{ userInfo?.nickname || '未设置' }}</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="editPhone">
        <text class="menu-icon">📱</text>
        <text class="menu-text">手机号</text>
        <text class="menu-val">{{ userInfo?.phone || '未绑定' }}</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="goCategories">
        <text class="menu-icon">📁</text>
        <text class="menu-text">分类管理</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="goAccounts">
        <text class="menu-icon">💳</text>
        <text class="menu-text">账户管理</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="goBudget">
        <text class="menu-icon">📊</text>
        <text class="menu-text">预算管理</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <button class="logout-btn" @click="handleLogout">退出登录</button>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { getUserInfo, updateUserInfo } from '@/api'

const userStore = useUserStore()
// 独立顶层 ref：用 store 当前值初始化，刷新时显式赋值，确保模板响应式可靠更新
const userInfo = ref<any>(userStore.userInfo.value)

const refreshUserInfo = async () => {
  try {
    const res: any = await getUserInfo()
    userStore.setUserInfo(res)
    userInfo.value = res
  } catch (e) {
    console.error('刷新用户信息失败', e)
  }
}

const editNickname = () => {
  uni.showModal({
    title: '设置昵称',
    editable: true,
    placeholderText: '请输入昵称',
    content: userInfo.value?.nickname || '',
    success: async (res) => {
      if (res.confirm && res.content) {
        try {
          await updateUserInfo({ nickname: res.content.trim() })
          await refreshUserInfo()
          uni.showToast({ title: '修改成功', icon: 'success' })
        } catch (error: any) {
          uni.showToast({ title: error.message || '修改失败', icon: 'none' })
        }
      }
    },
  })
}

const editPhone = () => {
  uni.showModal({
    title: '绑定手机号',
    editable: true,
    placeholderText: '请输入手机号',
    content: userInfo.value?.phone || '',
    success: async (res) => {
      if (res.confirm && res.content) {
        const phone = res.content.trim()
        if (!/^1\d{10}$/.test(phone)) {
          uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
          return
        }
        try {
          await updateUserInfo({ phone })
          await refreshUserInfo()
          uni.showToast({ title: '绑定成功', icon: 'success' })
        } catch (error: any) {
          uni.showToast({ title: error.message || '修改失败', icon: 'none' })
        }
      }
    },
  })
}

const goCategories = () => {
  uni.navigateTo({ url: '/pages/user/categories' })
}

const goAccounts = () => {
  uni.navigateTo({ url: '/pages/user/accounts' })
}

const goBudget = () => {
  uni.navigateTo({ url: '/pages/user/budget' })
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/login/index' })
      }
    },
  })
}

onShow(() => {
  if (userStore.isLoggedIn()) {
    refreshUserInfo()
  }
})
</script>

<style scoped lang="scss">
.user-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.user-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60rpx 40rpx;
  display: flex;
  align-items: center;

  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 60rpx;
    background: rgba(255, 255, 255, 0.3);
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 30rpx;

    text {
      font-size: 48rpx;
      color: #fff;
      font-weight: bold;
    }
  }

  .info {
    flex: 1;

    .nickname {
      display: block;
      font-size: 36rpx;
      font-weight: bold;
      color: #fff;
      margin-bottom: 10rpx;
    }

    .username {
      display: block;
      font-size: 24rpx;
      color: rgba(255, 255, 255, 0.8);
    }
  }
}

.menu-list {
  background: #fff;
  margin: 20rpx;
  border-radius: 15rpx;
  overflow: hidden;

  .menu-item {
    display: flex;
    align-items: center;
    padding: 35rpx 30rpx;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .menu-icon {
      font-size: 36rpx;
      margin-right: 20rpx;
    }

    .menu-text {
      flex: 1;
      font-size: 28rpx;
      color: #333;
    }

    .menu-val {
      font-size: 24rpx;
      color: #999;
      margin-right: 10rpx;
    }

    .menu-arrow {
      color: #999;
      font-size: 36rpx;
    }
  }
}

.logout-btn {
  margin: 60rpx 40rpx;
  height: 90rpx;
  line-height: 90rpx;
  background: #fff;
  color: #ff4d4f;
  border-radius: 45rpx;
  font-size: 32rpx;
}
</style>
