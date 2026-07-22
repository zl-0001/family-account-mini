<template>
  <view class="records-container">
    <view class="top-bar">
      <view class="month-selector">
        <text class="nav-btn" @click="prevMonth">‹</text>
        <text class="month-text">{{ monthStr }}</text>
        <text class="nav-btn" @click="nextMonth">›</text>
      </view>
      <view class="type-filter">
        <text class="type-btn" :class="{ active: filterType === '' }" @click="changeType('')">全部</text>
        <text class="type-btn" :class="{ active: filterType === 'expense' }" @click="changeType('expense')">支出</text>
        <text class="type-btn" :class="{ active: filterType === 'income' }" @click="changeType('income')">收入</text>
      </view>
      <view class="member-filter" v-if="isFamily">
        <picker :value="memberIndex" :range="memberOptions" range-key="nickname" @change="onMemberChange">
          <view class="member-filter-box">{{ memberOptions[memberIndex]?.nickname || '全部家人' }} ▼</view>
        </picker>
      </view>
    </view>

    <view class="record-list">
      <view class="record-item" v-for="r in list" :key="r.id" @click="goDetail(r)">
        <text class="r-icon">{{ r.category_icon || '📁' }}</text>
        <view class="r-info">
          <text class="r-cat">
            {{ r.category_name || '未分类' }}
            <text v-if="r.user_nickname" class="r-owner">· {{ r.user_nickname }}</text>
          </text>
          <text class="r-meta">{{ r.record_date }}{{ r.remark ? ' · ' + r.remark : '' }}</text>
        </view>
        <text class="r-amount" :class="r.type">{{ r.type === 'income' ? '+' : '-' }}¥{{ toFixed(r.amount) }}</text>
      </view>
      <view v-if="!list.length && !loadingMore" class="empty">本月暂无记录</view>
      <view v-if="loadingMore" class="bottom-tip">加载中...</view>
      <view v-else-if="noMore && list.length" class="bottom-tip">没有更多了</view>
      <view class="bottom-placeholder"></view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow, onReachBottom } from '@dcloudio/uni-app'
import { getRecords, getFamilyMembers } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isFamily = computed(() => !!userStore.userInfo.value?.family_id)
const currentUserId = computed(() => userStore.userInfo.value?.id)

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)
const filterType = ref('')
const list = ref<any[]>([])
const members = ref<any[]>([])
const memberIndex = ref(0)
const skip = ref(0)
const PAGE = 20
const noMore = ref(false)
const loadingMore = ref(false)

const monthStr = computed(() => `${currentYear.value}年${currentMonth.value}月`)
const toFixed = (v: any) => {
  const n = typeof v === 'string' ? parseFloat(v) || 0 : Number(v) || 0
  return n.toFixed(2)
}

const memberOptions = computed(() => [
  { user_id: null as number | null, nickname: '全部家人' },
  ...members.value.map((m: any) => ({ user_id: m.user_id as number | null, nickname: m.nickname || m.username })),
])
const currentFilterUid = computed(() => memberOptions.value[memberIndex.value]?.user_id ?? null)

const monthRange = () => {
  const y = currentYear.value, m = currentMonth.value
  const start = `${y}-${String(m).padStart(2, '0')}-01`
  const last = new Date(y, m, 0).getDate()
  const end = `${y}-${String(m).padStart(2, '0')}-${String(last).padStart(2, '0')}`
  return { start, end }
}

const fetchList = async (reset = true) => {
  if (reset) { skip.value = 0; noMore.value = false; list.value = [] }
  if (noMore.value) return
  loadingMore.value = true
  try {
    const { start, end } = monthRange()
    const params: any = { start_date: start, end_date: end, skip: skip.value, limit: PAGE }
    if (filterType.value) params.record_type = filterType.value
    if (currentFilterUid.value) params.user_id = currentFilterUid.value
    const res: any = await getRecords(params, true)
    const arr = res || []
    list.value = reset ? arr : [...list.value, ...arr]
    if (arr.length < PAGE) noMore.value = true
    else skip.value += PAGE
  } catch (e) {
    // 静默请求失败由 request 层 toast
  } finally {
    loadingMore.value = false
  }
}

const loadMore = () => {
  if (!loadingMore.value && !noMore.value) fetchList(false)
}

const prevMonth = () => {
  if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
  else currentMonth.value--
  fetchList()
}
const nextMonth = () => {
  if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
  else currentMonth.value++
  fetchList()
}
const changeType = (t: string) => {
  filterType.value = t
  fetchList()
}
const onMemberChange = (e: any) => {
  memberIndex.value = e.detail.value
  fetchList()
}

const goDetail = (r: any) => {
  // 本人 → 编辑；家人 → 只读详情（同一页，edit 页按 user_id 切换）
  uni.navigateTo({ url: `/pages/record/edit?id=${r.id}` })
}

onShow(() => {
  if (isFamily.value) {
    getFamilyMembers().then((m: any) => { members.value = m || [] }).catch(() => {})
  }
  fetchList()
})

onReachBottom(() => loadMore())
</script>

<style scoped lang="scss">
.records-container { min-height: 100vh; background: #f5f5f5; }
.top-bar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20rpx 30rpx 16rpx; }
.month-selector { display: flex; justify-content: space-between; align-items: center; color: #fff;
  .nav-btn { font-size: 40rpx; padding: 10rpx 30rpx; }
  .month-text { font-size: 32rpx; font-weight: bold; }
}
.type-filter { display: flex; padding: 20rpx 0 4rpx;
  .type-btn { padding: 8rpx 28rpx; margin-right: 16rpx; font-size: 24rpx; color: rgba(255,255,255,0.85); border: 1rpx solid rgba(255,255,255,0.4); border-radius: 30rpx;
    &.active { background: #fff; color: #667eea; border-color: #fff; font-weight: bold; }
  }
}
.member-filter { padding-top: 16rpx;
  .member-filter-box { display: inline-block; background: rgba(255,255,255,0.2); color: #fff; font-size: 24rpx; padding: 8rpx 24rpx; border-radius: 30rpx; }
}
.record-list { padding: 20rpx; }
.record-item { background: #fff; border-radius: 12rpx; padding: 28rpx; margin-bottom: 16rpx; display: flex; align-items: center;
  .r-icon { font-size: 40rpx; margin-right: 20rpx; }
  .r-info { flex: 1; min-width: 0;
    .r-cat { display: block; font-size: 28rpx; color: #333; font-weight: bold;
      .r-owner { font-size: 22rpx; color: #1989fa; font-weight: normal; margin-left: 8rpx; }
    }
    .r-meta { display: block; font-size: 22rpx; color: #999; margin-top: 6rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  }
  .r-amount { font-size: 30rpx; font-weight: bold; flex-shrink: 0;
    &.expense { color: #ff4d4f; }
    &.income { color: #07c160; }
  }
}
.empty { text-align: center; padding: 80rpx 0; color: #999; font-size: 26rpx; }
.bottom-tip { text-align: center; padding: 30rpx 0; color: #bbb; font-size: 24rpx; }
.bottom-placeholder { height: 40rpx; }
</style>
