<template>
  <view class="statistics-container">
    <!-- 月份选择 -->
    <view class="month-selector">
      <text class="nav-btn" @click="prevMonth">‹</text>
      <text class="month-text">{{ monthStr }}</text>
      <text class="nav-btn" @click="nextMonth">›</text>
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

    <!-- Tab 切换 -->
    <view class="tab-selector">
      <view
        class="tab-btn"
        :class="{ active: activeTab === 'expense' }"
        @click="activeTab = 'expense'"
      >
        支出分类
      </view>
      <view
        class="tab-btn"
        :class="{ active: activeTab === 'income' }"
        @click="activeTab = 'income'"
      >
        收入分类
      </view>
    </view>

    <!-- 分类大项筛选 -->
    <scroll-view class="filter-scroll" scroll-x v-if="parentCategories.length > 0">
      <view class="filter-list">
        <view
          class="filter-tag"
          :class="{ active: selectedParentId === null }"
          @click="selectParent(null)"
        >
          全部
        </view>
        <view
          class="filter-tag"
          :class="{ active: selectedParentId === cat.id }"
          v-for="cat in parentCategories"
          :key="cat.id"
          @click="selectParent(cat.id)"
        >
          {{ cat.icon }} {{ cat.name }}
        </view>
      </view>
    </scroll-view>

    <template v-if="categoryStats.length > 0">
      <!-- 环形图 -->
      <view class="chart-card">
        <view class="donut-wrap">
          <canvas
            type="2d"
            id="donutChart"
            class="donut-canvas"
            :style="{ width: '300rpx', height: '300rpx' }"
          ></canvas>
          <view class="donut-center">
            <text class="donut-total-label">{{ activeTab === 'expense' ? '总支出' : '总收入' }}</text>
            <text class="donut-total-value">¥{{ toFixed(totalAmount) }}</text>
          </view>
        </view>
        <!-- 图例 -->
        <view class="legend-wrap">
          <view class="legend-item" v-for="(item, i) in categoryStats" :key="item.category_id">
            <view class="legend-dot" :style="{ background: chartColors[i % chartColors.length] }"></view>
            <text class="legend-name">{{ item.category_name }}</text>
            <text class="legend-val">{{ toFixed(item.percent) }}%</text>
          </view>
        </view>
      </view>

      <!-- 分类排行 -->
      <view class="rank-card">
        <view class="rank-title">分类排行</view>
        <view class="rank-item" v-for="(item, i) in categoryStats" :key="item.category_id">
          <view class="rank-left">
            <text class="rank-index" :class="{ top: i < 3 }">{{ i + 1 }}</text>
            <text class="rank-name">{{ item.category_name }}</text>
          </view>
          <view class="rank-bar-wrap">
            <view
              class="rank-bar-fill"
              :style="{ width: barWidth(item) + '%', background: chartColors[i % chartColors.length] }"
            ></view>
          </view>
          <text class="rank-amount">¥{{ toFixed(item.amount) }}</text>
        </view>
      </view>
    </template>
    <view class="empty-tip" v-else>
      <text>暂无{{ activeTab === 'expense' ? '支出' : '收入' }}记录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMonthlyStatistics, getCategoryStatistics, getCategories } from '@/api'

let cachedDpr = 0
const getDpr = () => {
  if (cachedDpr) return cachedDpr
  try { cachedDpr = uni.getWindowInfo().pixelRatio } catch { cachedDpr = 2 }
  return cachedDpr
}

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const activeTab = ref<'expense' | 'income'>('expense')
const selectedParentId = ref<number | null>(null)
const allCategories = ref<any[]>([])

const chartColors = [
  '#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE',
  '#3BA272', '#FC8452', '#9A60B4', '#EA7CCC', '#48C9B0',
]

const monthStr = computed(
  () => `${currentYear.value}年${currentMonth.value}月`
)

const stats = ref({ income: 0, expense: 0, balance: 0 })
const categoryStats = ref<any[]>([])

const parentCategories = computed(() =>
  allCategories.value.filter((c: any) => c.type === activeTab.value && c.parent_id === null)
)

const toFixed = (val: number | string) => {
  if (typeof val === 'string') val = parseFloat(val) || 0
  return (val as number).toFixed(2)
}

const totalAmount = computed(() =>
  categoryStats.value.reduce((sum: number, item: any) => sum + parseFloat(toFixed(item.amount)), 0)
)

const drawDonut = () => {
  const total = totalAmount.value
  if (total === 0) return

  const dpr = getDpr()
  const query = uni.createSelectorQuery()
  query.select('#donutChart').fields({ node: true, size: true }).exec((res: any) => {
    if (!res || !res[0] || !res[0].node) return
    const canvas = res[0].node
    const ctx = canvas.getContext('2d')
    const width = res[0].width
    const height = res[0].height
    canvas.width = width * dpr
    canvas.height = height * dpr
    ctx.scale(dpr, dpr)

    const centerX = width / 2
    const centerY = height / 2
    const outerR = Math.min(centerX, centerY) - 2
    const innerR = outerR * 0.55

    ctx.clearRect(0, 0, width, height)

    let startAngle = -Math.PI / 2
    categoryStats.value.forEach((item: any, i: number) => {
      const percent = parseFloat(toFixed(item.amount)) / total
      const sweepAngle = percent * Math.PI * 2
      const endAngle = startAngle + sweepAngle

      ctx.beginPath()
      ctx.arc(centerX, centerY, outerR, startAngle, endAngle)
      ctx.arc(centerX, centerY, innerR, endAngle, startAngle, true)
      ctx.closePath()
      ctx.fillStyle = chartColors[i % chartColors.length]
      ctx.fill()

      startAngle = endAngle
    })
  })
}

const barWidth = (item: any) => {
  const maxAmount = categoryStats.value.length > 0
    ? Math.max(...categoryStats.value.map((c: any) => parseFloat(toFixed(c.amount))))
    : 0
  if (maxAmount === 0) return 0
  return (parseFloat(toFixed(item.amount)) / maxAmount) * 100
}

const selectParent = (id: number | null) => {
  selectedParentId.value = id
  fetchCategoryStats()
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

const fetchCategories = async () => {
  try {
    const res: any = await getCategories()
    allCategories.value = res || []
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

const fetchCategoryStats = async () => {
  try {
    const categoryRes: any = await getCategoryStatistics(
      currentYear.value,
      currentMonth.value,
      activeTab.value,
      selectedParentId.value !== null ? selectedParentId.value : undefined
    )
    categoryStats.value = categoryRes || []
    setTimeout(() => drawDonut(), 150)
  } catch (error) {
    console.error('获取分类统计失败', error)
  }
}

const fetchData = async () => {
  try {
    const monthlyRes: any = await getMonthlyStatistics(currentYear.value, currentMonth.value)
    stats.value = monthlyRes
    fetchCategoryStats()
  } catch (error) {
    console.error('获取数据失败', error)
  }
}

onShow(() => {
  fetchCategories()
  fetchData()
})

watch(activeTab, () => {
  selectedParentId.value = null
  fetchCategoryStats()
})
</script>

<style scoped lang="scss">
.statistics-container {
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

  .month-text { font-size: 32rpx; font-weight: bold; }
  .nav-btn { font-size: 40rpx; padding: 10rpx 30rpx; }
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

      .label { display: block; font-size: 24rpx; color: #999; margin-bottom: 10rpx; }
      .amount {
        display: block; font-size: 32rpx; font-weight: bold;
        &.income { color: #07c160; }
        &.expense { color: #ff4d4f; }
      }
    }
  }
}

.tab-selector {
  display: flex;
  background: #fff;
  margin: 0 20rpx;
  border-radius: 10rpx;

  .tab-btn {
    flex: 1; text-align: center; padding: 25rpx; font-size: 28rpx;
    &.active { color: #1989fa; border-bottom: 4rpx solid #1989fa; }
  }
}

.filter-scroll {
  background: #fff;
  margin: 10rpx 20rpx 0;
  border-radius: 10rpx;
  white-space: nowrap;
}

.filter-list {
  display: inline-flex;
  padding: 16rpx 10rpx;

  .filter-tag {
    display: inline-block;
    padding: 10rpx 24rpx;
    margin: 0 8rpx;
    font-size: 24rpx;
    color: #666;
    background: #f5f5f5;
    border-radius: 30rpx;
    white-space: nowrap;

    &.active {
      background: #1989fa;
      color: #fff;
    }
  }
}

.chart-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 15rpx;
  padding: 30rpx;
}

.donut-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  margin-bottom: 30rpx;
}

.donut-canvas {
  width: 300rpx;
  height: 300rpx;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160rpx;
  height: 160rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .donut-total-label { font-size: 22rpx; color: #999; }
  .donut-total-value { font-size: 26rpx; font-weight: bold; color: #333; margin-top: 6rpx; }
}

.legend-wrap {
  display: flex;
  flex-wrap: wrap;

  .legend-item {
    width: 50%;
    display: flex;
    align-items: center;
    padding: 10rpx 0;
    padding-right: 10rpx;
    box-sizing: border-box;

    .legend-dot {
      width: 16rpx; height: 16rpx; border-radius: 4rpx; margin-right: 10rpx; flex-shrink: 0;
    }
    .legend-name { font-size: 24rpx; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .legend-val { font-size: 22rpx; color: #999; margin-left: 8rpx; flex-shrink: 0; }
  }
}

.rank-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 15rpx;
  padding: 20rpx 30rpx;

  .rank-title {
    font-size: 28rpx; font-weight: bold; color: #333; margin-bottom: 20rpx;
  }

  .rank-item {
    display: flex;
    align-items: center;
    padding: 18rpx 0;
    border-bottom: 1px solid #f5f5f5;

    &:last-child { border-bottom: none; }

    .rank-left {
      width: 160rpx;
      display: flex;
      align-items: center;
      flex-shrink: 0;

      .rank-index {
        width: 40rpx; height: 40rpx; border-radius: 20rpx;
        background: #f0f0f0; color: #999;
        font-size: 22rpx; text-align: center; line-height: 40rpx;
        margin-right: 14rpx; flex-shrink: 0;

        &.top { background: #1989fa; color: #fff; }
      }

      .rank-name { font-size: 26rpx; color: #333; }
    }

    .rank-bar-wrap {
      flex: 1; height: 16rpx; background: #f5f5f5; border-radius: 8rpx; margin: 0 16rpx;

      .rank-bar-fill {
        height: 100%; border-radius: 8rpx;
        transition: width 0.3s ease;
      }
    }

    .rank-amount {
      width: 140rpx; text-align: right; font-size: 26rpx; font-weight: bold; color: #333; flex-shrink: 0;
    }
  }
}

.empty-tip {
  text-align: center; padding: 60rpx; color: #999; font-size: 26rpx;
}
</style>
