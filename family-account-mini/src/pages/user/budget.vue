<template>
  <view class="budget-container">
    <!-- 月份选择 -->
    <view class="month-selector">
      <text class="nav-btn" @click="prevMonth">‹</text>
      <text class="month-text">{{ monthStr }}</text>
      <text class="nav-btn" @click="nextMonth">›</text>
    </view>

    <!-- 预算概览 -->
    <view class="budget-overview">
      <view class="overview-header">
        <text class="overview-title">本月预算</text>
        <text class="overview-amount">¥{{ toFixed(totalBudget) }}</text>
      </view>
      <view class="overview-progress">
        <view class="progress-bar">
          <view
            class="progress-fill"
            :style="{ width: progressPercent + '%', background: progressColor }"
          ></view>
        </view>
        <view class="progress-info">
          <text>已花费 ¥{{ toFixed(totalExpense) }}</text>
          <text :style="{ color: progressColor }">{{ toFixed(progressPercent) }}%</text>
        </view>
      </view>
    </view>

    <!-- 分类预算列表 -->
    <view class="budget-list">
      <view
        class="budget-item"
        v-for="item in budgetList"
        :key="item.id"
        @click="handleEdit(item)"
      >
        <view class="budget-info">
          <text class="budget-icon">{{ item.category_icon || '📁' }}</text>
          <text class="budget-name">{{ item.category_name }}</text>
        </view>
        <view class="budget-amount">
          <text class="spent">¥{{ toFixed(item.spent) }}</text>
          <text class="limit">/ ¥{{ toFixed(item.amount) }}</text>
        </view>
        <view class="budget-progress">
          <view
            class="bar-fill"
            :style="{ width: item.percent + '%', background: getBarColor(item.percent) }"
          ></view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-tip" v-if="budgetList.length === 0">
        <text>暂无预算配置</text>
        <text class="empty-sub">点击添加按钮设置预算</text>
      </view>
    </view>

    <!-- 添加按钮 -->
    <button class="add-btn" @click="handleAdd">设置预算</button>

    <!-- 添加/编辑弹窗 -->
    <uni-popup ref="formPopup" type="bottom">
      <view class="form-popup">
        <view class="popup-header">
          <text>{{ isEditing ? '编辑预算' : '设置预算' }}</text>
          <text class="close" @click="formPopup.close()">×</text>
        </view>
        <view class="form-content">
          <view class="form-item" @click="showCategoryPicker = true">
            <text class="label">支出分类</text>
            <view class="item-value">
              <text>{{ selectedCategory?.name || '请选择' }}</text>
              <text class="arrow">›</text>
            </view>
          </view>
          <view class="form-item">
            <text class="label">预算金额</text>
            <input v-model="form.amount" type="digit" placeholder="请输入预算金额" class="input" />
          </view>
          <button class="save-btn" type="primary" @click="handleSave">
            保存
          </button>
          <button
            v-if="isEditing"
            class="delete-btn"
            type="warn"
            @click="handleDelete"
          >
            删除预算
          </button>
        </view>
      </view>
    </uni-popup>

    <!-- 分类选择器 -->
    <uni-popup ref="categoryPopup" type="bottom">
      <view class="picker-content">
        <view class="picker-header">
          <text @click="showCategoryPicker = false">取消</text>
          <text @click="confirmCategory">确定</text>
        </view>
        <picker-view
          :value="categoryIndex"
          @change="onCategoryChange"
          class="picker-view"
        >
          <picker-view-column>
            <view v-for="cat in expenseCategories" :key="cat.id" class="picker-item">
              {{ cat.name }}
            </view>
          </picker-view-column>
        </picker-view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getBudgets, createBudget, updateBudget, deleteBudget, getCategories, getCategoryStatistics } from '@/api'

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const budgetList = ref<any[]>([])
const expenseCategories = ref<any[]>([])
const formPopup = ref<any>(null)
const categoryPopup = ref<any>(null)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const categoryIndex = ref(0)

const showCategoryPicker = ref(false)
const selectedCategory = ref<any>(null)

const form = ref({
  amount: '',
})

const monthStr = computed(
  () => `${currentYear.value}年${currentMonth.value}月`
)

const totalBudget = computed(() =>
  budgetList.value.reduce((sum, item) => sum + item.amount, 0)
)

const totalExpense = computed(() =>
  budgetList.value.reduce((sum, item) => sum + item.spent, 0)
)

const progressPercent = computed(() => {
  if (totalBudget.value === 0) return 0
  return Math.min((totalExpense.value / totalBudget.value) * 100, 100)
})

const progressColor = computed(() => {
  const percent = progressPercent.value
  if (percent >= 100) return '#ff4d4f'
  if (percent >= 80) return '#ff9500'
  return '#07c160'
})

const toFixed = (val: number | string) => {
  if (typeof val === 'string') val = parseFloat(val) || 0
  return (val as number).toFixed(2)
}

const getBarColor = (percent: number) => {
  if (percent >= 100) return '#ff4d4f'
  if (percent >= 80) return '#ff9500'
  return '#07c160'
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
    const res: any = await getCategories('expense')
    expenseCategories.value = res || []
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

const fetchData = async () => {
  try {
    // 获取预算列表
    const budgetRes: any = await getBudgets(currentYear.value, currentMonth.value)
    const budgets = budgetRes || []

    // 获取分类支出统计
    const statsRes: any = await getCategoryStatistics(
      currentYear.value,
      currentMonth.value,
      'expense'
    )
    const statsMap = new Map(
      (statsRes || []).map((s: any) => [s.category_id, s.amount])
    )

    // 合并数据
    budgetList.value = budgets.map((b: any) => ({
      ...b,
      spent: statsMap.get(b.category_id) || 0,
      percent: b.amount > 0 ? ((statsMap.get(b.category_id) || 0) / b.amount) * 100 : 0,
    }))
  } catch (error) {
    console.error('获取数据失败', error)
  }
}

const onCategoryChange = (e: any) => {
  categoryIndex.value = e.detail.value[0]
}

const confirmCategory = () => {
  selectedCategory.value = expenseCategories.value[categoryIndex.value]
  showCategoryPicker.value = false
}

const handleAdd = () => {
  isEditing.value = false
  editingId.value = null
  categoryIndex.value = 0
  selectedCategory.value = expenseCategories.value[0] || null
  form.value.amount = ''
  formPopup.value.open()
}

const handleEdit = (item: any) => {
  isEditing.value = true
  editingId.value = item.id
  selectedCategory.value = expenseCategories.value.find(
    (c) => c.id === item.category_id
  ) || null
  categoryIndex.value = expenseCategories.value.findIndex(
    (c) => c.id === item.category_id
  ) || 0
  form.value.amount = item.amount?.toString() || ''
  formPopup.value.open()
}

const handleSave = async () => {
  if (!selectedCategory.value) {
    uni.showToast({ title: '请选择分类', icon: 'none' })
    return
  }
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    uni.showToast({ title: '请输入有效金额', icon: 'none' })
    return
  }

  try {
    const data = {
      category_id: selectedCategory.value.id,
      year: currentYear.value,
      month: currentMonth.value,
      amount: parseFloat(form.value.amount),
    }
    if (isEditing.value && editingId.value) {
      await updateBudget(editingId.value, data)
    } else {
      await createBudget(data)
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    formPopup.value.close()
    fetchData()
  } catch (error: any) {
    uni.showToast({ title: error.message || '保存失败', icon: 'none' })
  }
}

const handleDelete = () => {
  if (!editingId.value) return
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该预算吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteBudget(editingId.value!)
          uni.showToast({ title: '删除成功', icon: 'success' })
          formPopup.value.close()
          fetchData()
        } catch (error: any) {
          uni.showToast({ title: error.message || '删除失败', icon: 'none' })
        }
      }
    },
  })
}

watch(showCategoryPicker, (val) => {
  if (val) {
    categoryPopup.value.open()
  } else {
    categoryPopup.value.close()
  }
})

onMounted(() => {
  fetchCategories()
  fetchData()
})
</script>

<style scoped lang="scss">
.budget-container {
  min-height: 100vh;
  background: #f5f5f5;
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

  .nav-btn {
    font-size: 40rpx;
    padding: 10rpx 30rpx;
  }
}

.budget-overview {
  background: #fff;
  margin: 20rpx;
  border-radius: 15rpx;
  padding: 30rpx;

  .overview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;

    .overview-title {
      font-size: 28rpx;
      color: #666;
    }

    .overview-amount {
      font-size: 40rpx;
      font-weight: bold;
      color: #333;
    }
  }

  .overview-progress {
    .progress-bar {
      height: 20rpx;
      background: #f0f0f0;
      border-radius: 10rpx;
      overflow: hidden;
      margin-bottom: 15rpx;

      .progress-fill {
        height: 100%;
        border-radius: 10rpx;
        transition: width 0.3s;
      }
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      font-size: 24rpx;
      color: #666;
    }
  }
}

.budget-list {
  margin: 20rpx;

  .budget-item {
    background: #fff;
    border-radius: 10rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;

    .budget-info {
      display: flex;
      align-items: center;
      margin-bottom: 20rpx;

      .budget-icon {
        font-size: 36rpx;
        margin-right: 15rpx;
      }

      .budget-name {
        font-size: 28rpx;
        color: #333;
      }
    }

    .budget-amount {
      display: flex;
      align-items: baseline;
      margin-bottom: 15rpx;

      .spent {
        font-size: 32rpx;
        font-weight: bold;
        color: #333;
        margin-right: 10rpx;
      }

      .limit {
        font-size: 24rpx;
        color: #999;
      }
    }

    .budget-progress {
      height: 12rpx;
      background: #f0f0f0;
      border-radius: 6rpx;
      overflow: hidden;

      .bar-fill {
        height: 100%;
        border-radius: 6rpx;
        transition: width 0.3s;
      }
    }
  }

  .empty-tip {
    text-align: center;
    padding: 60rpx;
    color: #999;
    font-size: 28rpx;

    .empty-sub {
      display: block;
      font-size: 24rpx;
      margin-top: 20rpx;
    }
  }
}

.add-btn {
  margin: 40rpx 20rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 45rpx;
  height: 90rpx;
  line-height: 90rpx;
}

.form-popup {
  background: #fff;
  border-radius: 20rpx 20rpx 0 0;
  padding: 30rpx;

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
    font-size: 32rpx;
    font-weight: bold;

    .close {
      font-size: 48rpx;
      color: #999;
    }
  }

  .form-content {
    .form-item {
      margin-bottom: 30rpx;

      .label {
        display: block;
        font-size: 26rpx;
        color: #999;
        margin-bottom: 15rpx;
      }

      .item-value {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #eee;
        border-radius: 10rpx;
        padding: 20rpx;

        .arrow {
          color: #999;
        }
      }

      .input {
        border: 1px solid #eee;
        border-radius: 10rpx;
        padding: 20rpx;
        font-size: 28rpx;
      }
    }

    .save-btn {
      margin-top: 30rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      border-radius: 45rpx;
      height: 90rpx;
      line-height: 90rpx;
    }

    .delete-btn {
      margin-top: 20rpx;
      background: #fff;
      color: #ff4d4f;
      border-radius: 45rpx;
      height: 90rpx;
      line-height: 90rpx;
      border: 1px solid #ff4d4f;
    }
  }
}

.picker-content {
  background: #fff;
  border-radius: 20rpx 20rpx 0 0;
  padding-bottom: 50rpx;

  .picker-header {
    display: flex;
    justify-content: space-between;
    padding: 30rpx;
    border-bottom: 1px solid #eee;

    text {
      font-size: 28rpx;
      &:last-child {
        color: #1989fa;
      }
    }
  }

  .picker-view {
    height: 400rpx;

    .picker-item {
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 28rpx;
    }
  }
}
</style>
