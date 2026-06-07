<script setup lang="ts">
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'

onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  // 检查登录状态
  const userStore = useUserStore()
  if (!userStore.isLoggedIn) {
    // 未登录，跳转到登录页
    uni.reLaunch({ url: '/pages/login/index' })
  }
})
</script>
<style>
/* 全局样式 */
page {
  font-size: 28rpx;
  color: #333;
}

button {
  margin: 0;
  padding: 0;
}
</style>
