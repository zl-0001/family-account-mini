<template>
  <view class="family-container">
    <template v-if="family">
      <!-- 已加入家庭 -->
      <view class="card">
        <text class="family-name">{{ family.name }}</text>
        <view class="invite-box">
          <text class="invite-label">邀请码（分享给家人加入）</text>
          <view class="invite-row">
            <text class="invite-code" @click="copyCode">{{ family.invite_code }}</text>
            <text class="regen-btn" v-if="isOwner" @click="regenCode">重新生成</text>
          </view>
        </view>
      </view>

      <view class="card">
        <view class="section-title">家庭成员</view>
        <view class="member-item" v-for="m in family.members" :key="m.user_id">
          <text class="m-name">{{ m.nickname || m.username }}{{ m.user_id === currentUserId ? '（我）' : '' }}</text>
          <text class="m-role">{{ m.role === 'owner' ? '创建者' : '成员' }}</text>
          <text class="m-action" v-if="isOwner && m.user_id !== currentUserId" @click="removeMember(m.user_id)">移除</text>
        </view>
      </view>

      <button class="leave-btn" @click="leaveFamily" v-if="!isOwner">退出家庭</button>
      <view v-else class="owner-hint">你是创建者，不能直接退出（可移除其他成员）</view>
    </template>

    <template v-else>
      <!-- 未加入家庭 -->
      <view class="card">
        <view class="section-title">创建家庭</view>
        <input v-model="createName" placeholder="家庭名称（如：我们家）" class="input" />
        <button class="btn" :loading="creating" :disabled="creating" @click="doCreate">创建家庭</button>
      </view>
      <view class="card">
        <view class="section-title">或通过邀请码加入</view>
        <input v-model="joinCode" placeholder="输入家人分享的邀请码" class="input" />
        <button class="btn" :loading="joining" :disabled="joining" @click="doJoin">加入家庭</button>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import {
  createFamily, getMyFamily, joinFamily,
  regenerateInviteCode, removeFamilyMember, getFamilyMembers,
} from '@/api'
import { useUserStore } from '@/stores/user'
import { getUserInfo } from '@/api'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userInfo.value?.id || 0)
const family = ref<any>(null)
const createName = ref('')
const joinCode = ref('')
const creating = ref(false)
const joining = ref(false)

const isOwner = computed(() => !!family.value && family.value.owner_id === currentUserId.value)

const refresh = async () => {
  // 先把当前用户的 family_id 刷新到 store
  try {
    const me: any = await getUserInfo()
    userStore.setUserInfo(me)
  } catch (e) { /* ignore */ }

  if (userStore.userInfo.value?.family_id) {
    try {
      const f: any = await getMyFamily()
      family.value = f || null
    } catch (e) {
      family.value = null
    }
  } else {
    family.value = null
  }
}

const copyCode = () => {
  if (!family.value?.invite_code) return
  uni.setClipboardData({ data: family.value.invite_code })
}

const regenCode = async () => {
  try {
    const res: any = await regenerateInviteCode()
    uni.showToast({ title: '已生成', icon: 'success' })
    family.value.invite_code = res.invite_code
  } catch (e: any) {
    uni.showToast({ title: e.message || '失败', icon: 'none' })
  }
}

const doCreate = async () => {
  if (creating.value) return
  if (!createName.value.trim()) { uni.showToast({ title: '请填家庭名称', icon: 'none' }); return }
  creating.value = true
  try {
    await createFamily(createName.value.trim())
    uni.showToast({ title: '创建成功', icon: 'success' })
    createName.value = ''
    refresh()
  } catch (e: any) {
    uni.showToast({ title: e.message || '创建失败', icon: 'none' })
  } finally {
    creating.value = false
  }
}

const doJoin = async () => {
  if (joining.value) return
  if (!joinCode.value.trim()) { uni.showToast({ title: '请填邀请码', icon: 'none' }); return }
  joining.value = true
  try {
    await joinFamily(joinCode.value.trim())
    uni.showToast({ title: '加入成功', icon: 'success' })
    joinCode.value = ''
    refresh()
  } catch (e: any) {
    uni.showToast({ title: e.message || '加入失败', icon: 'none' })
  } finally {
    joining.value = false
  }
}

const removeMember = (memberId: number) => {
  uni.showModal({
    title: '确认移除', content: '确定移除该成员吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await removeFamilyMember(memberId)
          uni.showToast({ title: '已移除', icon: 'success' })
          refresh()
        } catch (e: any) {
          uni.showToast({ title: e.message || '失败', icon: 'none' })
        }
      }
    },
  })
}

const leaveFamily = () => {
  uni.showModal({
    title: '确认退出', content: '退出后将不再查看家庭收支，确定？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await removeFamilyMember(currentUserId.value)
          uni.showToast({ title: '已退出', icon: 'success' })
          refresh()
        } catch (e: any) {
          uni.showToast({ title: e.message || '失败', icon: 'none' })
        }
      }
    },
  })
}

onShow(() => {
  refresh()
})
</script>

<style scoped lang="scss">
.family-container { min-height: 100vh; background: #f5f5f5; padding: 20rpx; }
.card { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 20rpx; }
.family-name { display: block; font-size: 36rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
.invite-box {
  .invite-label { display: block; font-size: 24rpx; color: #999; margin-bottom: 12rpx; }
  .invite-row { display: flex; align-items: center; }
  .invite-code { flex: 1; font-size: 34rpx; font-weight: bold; color: #1989fa; letter-spacing: 4rpx; }
  .regen-btn { font-size: 24rpx; color: #999; padding: 8rpx 20rpx; border: 1rpx solid #ddd; border-radius: 30rpx; }
}
.section-title { font-size: 26rpx; color: #999; margin-bottom: 16rpx; }
.member-item { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5;
  &:last-child { border-bottom: none; }
  .m-name { flex: 1; font-size: 28rpx; color: #333; }
  .m-role { font-size: 24rpx; color: #999; margin-right: 20rpx; }
  .m-action { font-size: 24rpx; color: #ff4d4f; }
}
.input { border: 1rpx solid #eee; border-radius: 10rpx; padding: 20rpx; font-size: 28rpx; margin-bottom: 20rpx; }
.btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 45rpx; height: 80rpx; line-height: 80rpx; }
.leave-btn { margin-top: 30rpx; background: #fff; color: #ff4d4f; border-radius: 45rpx; height: 90rpx; line-height: 90rpx; border: 1rpx solid #ff4d4f; }
.owner-hint { text-align: center; color: #bbb; font-size: 24rpx; margin-top: 30rpx; }
</style>
