<template>
  <view class="home-container">
    <!-- 月份选择 -->
    <view class="month-selector">
      <text class="month-text">{{ monthStr }}</text>
      <view class="month-nav">
        <text class="nav-btn" @click="prevMonth">‹</text>
        <text class="nav-btn" @click="nextMonth">›</text>
      </view>
    </view>

    <!-- 收支概览 -->
    <view class="overview-card">
      <view class="overview-row">
        <view class="overview-item">
          <text class="label">收入</text>
          <text class="amount income">+¥{{ toFixed(stats.income) }}</text>
        </view>
        <view class="overview-item">
          <text class="label">支出</text>
          <text class="amount expense">-¥{{ toFixed(stats.expense) }}</text>
        </view>
        <view class="overview-item">
          <text class="label">结余</text>
          <text class="amount">¥{{ toFixed(stats.balance) }}</text>
        </view>
      </view>
    </view>

    <!-- 固定收支 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">固定收支</text>
        <text class="more" @click="goRecord">记账</text>
      </view>
      <view class="fixed-list" v-if="fixedRecords.length > 0">
        <view class="fixed-item" v-for="item in fixedRecords" :key="item.id">
          <view class="fixed-info">
            <text class="fixed-name">{{ item.category_name || '记账' }}</text>
            <text class="fixed-date">{{ item.record_date }}</text>
          </view>
          <text class="fixed-amount" :class="item.type">
            {{ item.type === 'income' ? '+' : '-' }}¥{{ toFixed(item.amount) }}
          </text>
        </view>
      </view>
      <view class="empty-tip" v-else>
        <text>暂无固定收支记录</text>
      </view>
    </view>

    <!-- 最近记录 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">最近记录</text>
        <text class="more" @click="goRecord">查看全部</text>
      </view>
      <view class="record-list" v-if="recentRecords.length > 0">
        <view class="record-item" v-for="item in recentRecords" :key="item.id">
          <view class="record-info">
            <text class="record-name">{{ item.category_name || '记账' }}</text>
            <text class="record-date">{{ item.record_date }}</text>
          </view>
          <text class="record-amount" :class="item.type">
            {{ item.type === 'income' ? '+' : '-' }}¥{{ toFixed(item.amount) }}
          </text>
        </view>
      </view>
      <view class="empty-tip" v-else>
        <text>暂无记录，赶快记账吧</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMonthlyStatistics, getFixedRecords, getRecords } from '@/api'

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const monthStr = computed(() => `${currentYear.value}年${currentMonth.value}月`)

const stats = ref({
  income: 0,
  expense: 0,
  balance: 0,
})

const fixedRecords = ref<any[]>([])
const recentRecords = ref<any[]>([])

const toFixed = (val: number | string) => {
  if (typeof val === 'string') val = parseFloat(val) || 0
  return (val as number).toFixed(2)
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  fetchData()
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  fetchData()
}

const fetchData = async () => {
  try {
    // 获取月度统计
    const monthlyRes: any = await getMonthlyStatistics(
      currentYear.value,
      currentMonth.value
    )
    stats.value = monthlyRes

    // 获取固定收支
    const fixedRes: any = await getFixedRecords()
    fixedRecords.value = (fixedRes || []).slice(0, 5)

    // 获取最近记录
    const recordsRes: any = await getRecords({
      start_date: `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-01`,
      end_date: `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-31`,
    })
    recentRecords.value = (recordsRes || []).slice(0, 5)
  } catch (error) {
    console.error('获取数据失败', error)
  }
}

const goRecord = () => {
  uni.switchTab({ url: '/pages/record/index' })
}

onShow(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 20rpx;
}

.month-selector {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .month-text {
    font-size: 32rpx;
    font-weight: bold;
  }

  .month-nav {
    display: flex;

    .nav-btn {
      display: inline-block;
      padding: 10rpx 20rpx;
      margin-left: 20rpx;
      font-size: 40rpx;
    }
  }
}

.overview-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 15rpx;
  padding: 30rpx;

  .overview-row {
    display: flex;
    justify-content: space-around;

    .overview-item {
      text-align: center;

      .label {
        display: block;
        font-size: 24rpx;
        color: #999;
        margin-bottom: 10rpx;
      }

      .amount {
        display: block;
        font-size: 32rpx;
        font-weight: bold;

        &.income {
          color: #07c160;
        }

        &.expense {
          color: #ff4d4f;
        }
      }
    }
  }
}

.section {
  background: #fff;
  margin: 20rpx;
  border-radius: 15rpx;
  padding: 20rpx;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;

    .section-title {
      font-size: 28rpx;
      font-weight: bold;
    }

    .more {
      font-size: 24rpx;
      color: #999;
    }
  }
}

.fixed-list,
.record-list {
  .fixed-item,
  .record-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .fixed-info,
    .record-info {
      .fixed-name,
      .record-name {
        display: block;
        font-size: 28rpx;
        margin-bottom: 8rpx;
      }

      .fixed-date,
      .record-date {
        display: block;
        font-size: 22rpx;
        color: #999;
      }
    }

    .fixed-amount,
    .record-amount {
      font-size: 30rpx;
      font-weight: bold;

      &.income {
        color: #07c160;
      }

      &.expense {
        color: #ff4d4f;
      }
    }
  }
}

.empty-tip {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
