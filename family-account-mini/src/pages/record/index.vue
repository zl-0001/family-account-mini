<template>
  <view class="record-container">
    <!-- 类型选择 -->
    <view class="type-selector">
      <view
        class="type-btn"
        :class="{ active: activeType === 'expense' }"
        @click="activeType = 'expense'"
      >
        支出
      </view>
      <view
        class="type-btn"
        :class="{ active: activeType === 'income' }"
        @click="activeType = 'income'"
      >
        收入
      </view>
    </view>

    <!-- 金额输入 -->
    <view class="amount-section">
      <text class="amount-label">金额</text>
      <view class="amount-input-wrapper">
        <text class="currency">¥</text>
        <input
          v-model="form.amount"
          type="digit"
          placeholder="0.00"
          class="amount-input"
        />
      </view>
    </view>

    <!-- 分类选择 -->
    <view class="form-item" @click="openCategoryPicker">
      <text class="item-label">分类</text>
      <view class="item-value">
        <text>{{ selectedCategoryText }}</text>
        <text class="arrow">›</text>
      </view>
    </view>

    <!-- 账户选择 -->
    <view class="form-item" @click="openAccountPicker">
      <text class="item-label">账户</text>
      <view class="item-value">
        <text>{{ selectedAccount?.name || '请选择' }}</text>
        <text class="arrow">›</text>
      </view>
    </view>

    <!-- 日期选择 -->
    <view class="form-item" @click="openDatePicker">
      <text class="item-label">日期</text>
      <view class="item-value">
        <text>{{ form.record_date }}</text>
        <text class="arrow">›</text>
      </view>
    </view>

    <!-- 备注 -->
    <view class="form-item">
      <text class="item-label">备注</text>
      <input
        v-model="form.remark"
        type="text"
        placeholder="添加备注"
        class="remark-input"
      />
    </view>

    <!-- 保存按钮 -->
    <button class="save-btn" type="primary" @click="handleSave" :loading="loading" :disabled="loading">
      保存
    </button>

    <!-- 分类选择器（分组列表，仅叶子/子分类可选） -->
    <view class="modal-mask" v-if="showCategoryPicker" @click="showCategoryPicker = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text @click="showCategoryPicker = false">取消</text>
          <text class="modal-title">选择分类</text>
          <text class="modal-placeholder">确定</text>
        </view>
        <CategoryTreePicker
          :categories="categories"
          :selected-id="selectedCategory?.id"
          @pick="onPickCategory"
        />
      </view>
    </view>

    <!-- 账户选择器 -->
    <view class="modal-mask" v-if="showAccountPicker" @click="showAccountPicker = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text @click="showAccountPicker = false">取消</text>
          <text class="confirm" @click="confirmAccount">确定</text>
        </view>
        <picker-view :value="pickerAccountValue" @change="onAccountChange" class="modal-picker">
          <picker-view-column>
            <view v-for="acc in accounts" :key="acc.id" class="picker-item">{{ acc.name }}</view>
          </picker-view-column>
        </picker-view>
      </view>
    </view>

    <!-- 日期选择器 -->
    <view class="modal-mask" v-if="showDatePicker" @click="showDatePicker = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text @click="showDatePicker = false">取消</text>
          <text class="confirm" @click="confirmDate">确定</text>
        </view>
        <picker-view :value="pickerDateValue" @change="onDateChange" class="modal-picker">
          <picker-view-column>
            <view v-for="date in dateList" :key="date" class="picker-item">{{ date }}</view>
          </picker-view-column>
        </picker-view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCategories, getAccounts, createRecord } from '@/api'
import CategoryTreePicker from '@/components/CategoryTreePicker.vue'

const activeType = ref<'expense' | 'income'>('expense')
const loading = ref(false)

const form = ref({
  amount: '',
  record_date: new Date().toISOString().split('T')[0],
  remark: '',
})

const categories = ref<any[]>([])
const accounts = ref<any[]>([])
const selectedCategory = ref<any>(null)
const selectedAccount = ref<any>(null)

// Modal 显示状态
const showCategoryPicker = ref(false)
const showAccountPicker = ref(false)
const showDatePicker = ref(false)

const accountIndex = ref(0)
const dateIndex = ref(0)
const pickerAccountValue = ref([0])
const pickerDateValue = ref([0])

const dateList = computed(() => {
  const dates: string[] = []
  for (let i = 0; i < 30; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(d.toISOString().split('T')[0])
  }
  return dates
})

// 第一个叶子分类，作为默认选中
const firstLeaf = computed(() => {
  const child = categories.value.find((c: any) => c.parent_id != null)
  return child || categories.value[0] || null
})

// 表单项显示：带父分类前缀，如「家庭不固定支出 / 餐饮」
const selectedCategoryText = computed(() => {
  const c = selectedCategory.value
  if (!c) return '请选择'
  if (c.parent_id != null) {
    const parent = categories.value.find((p: any) => p.id === c.parent_id)
    return parent ? `${parent.name} / ${c.name}` : c.name
  }
  return c.name
})

const onPickCategory = (cat: any) => {
  selectedCategory.value = cat
  showCategoryPicker.value = false
}

const onAccountChange = (e: any) => {
  accountIndex.value = e.detail.value[0]
}

const onDateChange = (e: any) => {
  dateIndex.value = e.detail.value[0]
}

const confirmAccount = () => {
  selectedAccount.value = accounts.value[accountIndex.value]
  showAccountPicker.value = false
}

const confirmDate = () => {
  form.value.record_date = dateList.value[dateIndex.value]
  showDatePicker.value = false
}

const openCategoryPicker = () => {
  showAccountPicker.value = false
  showDatePicker.value = false
  showCategoryPicker.value = true
}

const openAccountPicker = () => {
  showCategoryPicker.value = false
  showDatePicker.value = false
  pickerAccountValue.value = [accountIndex.value]
  showAccountPicker.value = true
}

const openDatePicker = () => {
  showCategoryPicker.value = false
  showAccountPicker.value = false
  pickerDateValue.value = [dateIndex.value]
  showDatePicker.value = true
}

const fetchCategories = async () => {
  try {
    const res: any = await getCategories(activeType.value)
    categories.value = res || []
    selectedCategory.value = firstLeaf.value || null
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

const fetchAccounts = async () => {
  try {
    const res: any = await getAccounts()
    accounts.value = res || []
    if (accounts.value.length > 0) {
      selectedAccount.value = accounts.value[0]
    }
  } catch (error) {
    console.error('获取账户失败', error)
  }
}

const handleSave = async () => {
  if (loading.value) return
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    uni.showToast({ title: '请输入有效金额', icon: 'none' })
    return
  }
  if (!selectedCategory.value) {
    uni.showToast({ title: '请选择分类', icon: 'none' })
    return
  }
  if (!selectedAccount.value) {
    uni.showToast({ title: '请选择账户', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await createRecord({
      account_id: selectedAccount.value.id,
      category_id: selectedCategory.value.id,
      type: activeType.value,
      amount: parseFloat(form.value.amount),
      record_date: form.value.record_date,
      remark: form.value.remark || undefined,
    })
    uni.showToast({ title: '保存成功', icon: 'success' })
    // 重置表单
    form.value.amount = ''
    form.value.remark = ''
  } catch (error: any) {
    uni.showToast({ title: error.message || '保存失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchAccounts()
})

onShow(() => {
  fetchAccounts()
})

watch(activeType, () => {
  fetchCategories()
  fetchAccounts()
})
</script>

<style scoped lang="scss">
.record-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx;
}

.type-selector {
  display: flex;
  background: #fff;
  border-radius: 10rpx;
  padding: 10rpx;
  margin-bottom: 20rpx;

  .type-btn {
    flex: 1;
    text-align: center;
    padding: 20rpx;
    border-radius: 8rpx;
    font-size: 28rpx;

    &.active {
      background: #1989fa;
      color: #fff;
    }
  }
}

.amount-section {
  background: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  overflow: hidden;

  .amount-label {
    display: block;
    font-size: 24rpx;
    color: #999;
    margin-bottom: 20rpx;
  }

  .amount-input-wrapper {
    display: flex;
    align-items: center;
    width: 100%;

    .currency {
      font-size: 48rpx;
      font-weight: bold;
      margin-right: 10rpx;
      flex-shrink: 0;
    }

    .amount-input {
      flex: 1;
      min-width: 0;
      width: 0;
      font-size: 60rpx;
      font-weight: bold;
      height: 80rpx;
      line-height: 80rpx;
    }
  }
}

.form-item {
  background: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .item-label {
    font-size: 28rpx;
  }

  .item-value {
    display: flex;
    align-items: center;
    color: #999;

    .arrow {
      margin-left: 10rpx;
    }
  }

  .remark-input {
    flex: 1;
    text-align: right;
    font-size: 28rpx;
  }
}

.save-btn {
  margin-top: 40rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 45rpx;
  height: 90rpx;
  line-height: 90rpx;
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.modal-content {
  background: #fff;
  border-radius: 20rpx 20rpx 0 0;
  padding-bottom: calc(50rpx + env(safe-area-inset-bottom));

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx;
    border-bottom: 1px solid #eee;

    text {
      font-size: 28rpx;
    }

    .confirm {
      color: #1989fa;
    }

    .modal-title {
      font-weight: bold;
      color: #333;
    }

    .modal-placeholder {
      visibility: hidden;
    }
  }

  .modal-picker {
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
