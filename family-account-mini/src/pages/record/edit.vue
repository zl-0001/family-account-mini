<template>
  <view class="edit-container">
    <view class="type-selector">
      <view class="type-btn" :class="{ active: form.type === 'expense' }" @click="form.type = 'expense'">支出</view>
      <view class="type-btn" :class="{ active: form.type === 'income' }" @click="form.type = 'income'">收入</view>
    </view>

    <view class="amount-section">
      <text class="amount-label">金额</text>
      <view class="amount-input-wrapper">
        <text class="currency">¥</text>
        <input v-model="form.amount" type="digit" placeholder="0.00" class="amount-input" />
      </view>
    </view>

    <view class="form-item" @click="showCategoryPicker = true">
      <text class="item-label">分类</text>
      <view class="item-value">
        <text>{{ selectedCategoryText }}</text>
        <text class="arrow">›</text>
      </view>
    </view>
    <view class="form-item" @click="openAccountPicker">
      <text class="item-label">账户</text>
      <view class="item-value">
        <text>{{ selectedAccount?.name || '请选择' }}</text>
        <text class="arrow">›</text>
      </view>
    </view>
    <view class="form-item" @click="openDatePicker">
      <text class="item-label">日期</text>
      <view class="item-value">
        <text>{{ form.record_date }}</text>
        <text class="arrow">›</text>
      </view>
    </view>
    <view class="form-item">
      <text class="item-label">备注</text>
      <input v-model="form.remark" placeholder="添加备注" class="remark-input" />
    </view>

    <button v-if="canEdit" class="save-btn" type="primary" :loading="saving" :disabled="saving" @click="handleSave">保存</button>
    <view v-else class="readonly-tip">家人的记录，仅可查看（仅本人可编辑/删除）</view>
    <button v-if="canEdit" class="delete-btn" @click="handleDelete">删除记录</button>

    <!-- 分类选择器 -->
    <view class="modal-mask" v-if="showCategoryPicker" @click="showCategoryPicker = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text @click="showCategoryPicker = false">取消</text>
          <text class="modal-title">选择分类</text>
          <text class="modal-placeholder">确定</text>
        </view>
        <CategoryTreePicker :categories="categories" :selected-id="selectedCategory?.id" @pick="onPickCategory" />
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
            <view v-for="d in dateList" :key="d" class="picker-item">{{ d }}</view>
          </picker-view-column>
        </picker-view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getRecordDetail, updateRecord, deleteRecord, getCategories, getAccounts } from '@/api'
import CategoryTreePicker from '@/components/CategoryTreePicker.vue'
import { useUserStore } from '@/stores/user'

const recordId = ref(0)
const categories = ref<any[]>([])
const accounts = ref<any[]>([])
const selectedCategory = ref<any>(null)
const selectedAccount = ref<any>(null)
const saving = ref(false)
const userStore = useUserStore()
const canEdit = ref(true)

const form = ref({
  type: 'expense' as 'expense' | 'income',
  amount: '',
  record_date: '',
  remark: '',
})

const showCategoryPicker = ref(false)
const showAccountPicker = ref(false)
const showDatePicker = ref(false)
const accountIndex = ref(0)
const dateIndex = ref(0)
const pickerAccountValue = ref([0])
const pickerDateValue = ref([0])

const selectedCategoryText = computed(() => {
  const c = selectedCategory.value
  if (!c) return '请选择'
  if (c.parent_id != null) {
    const parent = categories.value.find((p: any) => p.id === c.parent_id)
    return parent ? `${parent.name} / ${c.name}` : c.name
  }
  return c.name
})

const dateList = computed(() => {
  const arr: string[] = []
  for (let i = 0; i < 30; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    arr.push(d.toISOString().split('T')[0])
  }
  return arr
})

const onAccountChange = (e: any) => { accountIndex.value = e.detail.value[0] }
const onDateChange = (e: any) => { dateIndex.value = e.detail.value[0] }
const openAccountPicker = () => {
  const i = accounts.value.findIndex((a: any) => a.id === selectedAccount.value?.id)
  accountIndex.value = i >= 0 ? i : 0
  pickerAccountValue.value = [accountIndex.value]
  showAccountPicker.value = true
}
const openDatePicker = () => {
  const i = dateList.value.indexOf(form.value.record_date)
  dateIndex.value = i >= 0 ? i : 0
  pickerDateValue.value = [dateIndex.value]
  showDatePicker.value = true
}
const confirmAccount = () => {
  selectedAccount.value = accounts.value[accountIndex.value]
  showAccountPicker.value = false
}
const confirmDate = () => {
  form.value.record_date = dateList.value[dateIndex.value]
  showDatePicker.value = false
}
const onPickCategory = (cat: any) => {
  selectedCategory.value = cat
  showCategoryPicker.value = false
}

const loadDetail = async () => {
  try {
    const r: any = await getRecordDetail(recordId.value)
    form.value.type = r.type
    const amt = typeof r.amount === 'string' ? parseFloat(r.amount) : Number(r.amount)
    form.value.amount = (isNaN(amt) ? 0 : amt).toString()
    form.value.record_date = r.record_date
    form.value.remark = r.remark || ''
    selectedCategory.value = categories.value.find((c: any) => c.id === r.category_id) || null
    selectedAccount.value = accounts.value.find((a: any) => a.id === r.account_id) || null
    canEdit.value = r.user_id === userStore.userInfo.value?.id
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  }
}

const handleSave = async () => {
  if (saving.value) return
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    uni.showToast({ title: '请输入有效金额', icon: 'none' })
    return
  }
  if (!selectedCategory.value) { uni.showToast({ title: '请选择分类', icon: 'none' }); return }
  if (!selectedAccount.value) { uni.showToast({ title: '请选择账户', icon: 'none' }); return }

  saving.value = true
  try {
    await updateRecord(recordId.value, {
      amount: parseFloat(form.value.amount),
      remark: form.value.remark || undefined,
      category_id: selectedCategory.value.id,
      account_id: selectedAccount.value.id,
      type: form.value.type,
      record_date: form.value.record_date,
    })
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 600)
  } catch (e: any) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}

const handleDelete = () => {
  uni.showModal({
    title: '确认删除',
    content: '确定删除这条记录吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteRecord(recordId.value)
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => uni.navigateBack(), 600)
        } catch (e: any) {
          uni.showToast({ title: e.message || '删除失败', icon: 'none' })
        }
      }
    },
  })
}

onLoad((q: any) => {
  recordId.value = Number(q.id)
  Promise.all([getCategories(), getAccounts()])
    .then(([c, a]: any) => {
      categories.value = c || []
      accounts.value = a || []
      loadDetail()
    })
    .catch(() => {})
})
</script>

<style scoped lang="scss">
.edit-container { min-height: 100vh; background: #f5f5f5; padding: 20rpx; }
.type-selector { display: flex; background: #fff; border-radius: 10rpx; padding: 10rpx; margin-bottom: 20rpx;
  .type-btn { flex: 1; text-align: center; padding: 20rpx; border-radius: 8rpx; font-size: 28rpx;
    &.active { background: #1989fa; color: #fff; }
  }
}
.amount-section { background: #fff; border-radius: 10rpx; padding: 30rpx; margin-bottom: 20rpx;
  .amount-label { display: block; font-size: 24rpx; color: #999; margin-bottom: 20rpx; }
  .amount-input-wrapper { display: flex; align-items: center;
    .currency { font-size: 48rpx; font-weight: bold; margin-right: 10rpx; flex-shrink: 0; }
    .amount-input { flex: 1; min-width: 0; width: 0; font-size: 60rpx; font-weight: bold; height: 80rpx; line-height: 80rpx; }
  }
}
.form-item { background: #fff; border-radius: 10rpx; padding: 30rpx; margin-bottom: 20rpx; display: flex; justify-content: space-between; align-items: center;
  .item-label { font-size: 28rpx; }
  .item-value { display: flex; align-items: center; color: #999;
    .arrow { margin-left: 10rpx; }
  }
  .remark-input { flex: 1; text-align: right; font-size: 28rpx; }
}
.save-btn { margin-top: 20rpx; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 45rpx; height: 90rpx; line-height: 90rpx; }
.readonly-tip { margin-top: 20rpx; text-align: center; color: #999; font-size: 26rpx; padding: 30rpx; }
.delete-btn { margin-top: 20rpx; background: #fff; color: #ff4d4f; border-radius: 45rpx; height: 90rpx; line-height: 90rpx; border: 1rpx solid #ff4d4f; }

.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 999; display: flex; flex-direction: column; justify-content: flex-end; }
.modal-content { background: #fff; border-radius: 20rpx 20rpx 0 0; padding-bottom: calc(50rpx + env(safe-area-inset-bottom));
  .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 30rpx; border-bottom: 1rpx solid #eee;
    text { font-size: 28rpx; }
    .confirm { color: #1989fa; }
    .modal-title { font-weight: bold; color: #333; }
    .modal-placeholder { visibility: hidden; }
  }
  .modal-picker { height: 400rpx;
    .picker-item { display: flex; justify-content: center; align-items: center; font-size: 28rpx; }
  }
}
</style>
