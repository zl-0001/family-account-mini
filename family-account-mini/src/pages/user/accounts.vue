<template>
  <view class="accounts-container">
    <!-- 账户列表 -->
    <view class="account-list">
      <view
        class="account-item"
        v-for="acc in accountList"
        :key="acc.id"
      >
        <view class="account-icon" :style="{ background: acc.color || '#4ECDC4' }">
          <text>{{ acc.icon || '💳' }}</text>
        </view>
        <view class="account-info">
          <text class="account-name">{{ acc.name }}</text>
          <text class="account-type">{{ formatType(acc.type) }}</text>
        </view>
        <view class="account-balance">
          <text class="balance-label">余额</text>
          <text class="balance-amount">¥{{ toFixed(acc.balance) }}</text>
        </view>
        <view class="account-actions">
          <text class="action-btn" @click="handleEdit(acc)">编辑</text>
          <text class="action-btn delete" @click="handleDelete(acc)">删除</text>
        </view>
      </view>
    </view>

    <!-- 添加按钮 -->
    <button class="add-btn" @click="handleAdd">添加账户</button>

    <!-- 添加/编辑弹窗 -->
    <uni-popup ref="formPopup" type="bottom">
      <view class="form-popup">
        <view class="popup-header">
          <text>{{ isEditing ? '编辑账户' : '添加账户' }}</text>
          <text class="close" @click="formPopup.close()">×</text>
        </view>
        <view class="form-content">
          <view class="form-item">
            <text class="label">账户名称</text>
            <input v-model="form.name" placeholder="请输入账户名称" class="input" />
          </view>
          <view class="form-item">
            <text class="label">账户类型</text>
            <picker :value="typeIndex" :range="typeOptions" @change="onTypeChange" class="type-picker">
              <view class="picker-value">{{ typeOptions[typeIndex] || '请选择' }}</view>
            </picker>
          </view>
          <view class="form-item">
            <text class="label">初始余额</text>
            <input v-model="form.balance" type="digit" placeholder="0.00" class="input" />
          </view>
          <view class="form-item">
            <text class="label">图标</text>
            <input v-model="form.icon" placeholder="请输入图标emoji" class="input" />
          </view>
          <view class="form-item">
            <text class="label">颜色</text>
            <view class="color-picker">
              <view
                v-for="color in colorOptions"
                :key="color"
                class="color-option"
                :class="{ active: form.color === color }"
                :style="{ background: color }"
                @click="form.color = color"
              ></view>
            </view>
          </view>
          <button class="save-btn" type="primary" @click="handleSave">
            保存
          </button>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  getAccounts,
  createAccount,
  updateAccount,
  deleteAccount,
} from '@/api'

const accountList = ref<any[]>([])
const formPopup = ref<any>(null)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const typeIndex = ref(0)

const typeOptions = ['现金', '银行卡', '支付宝', '微信', '信用卡', '投资账户']
const typeValues = ['cash', 'bank', 'alipay', 'wechat', 'credit_card', 'investment']
const colorOptions = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']

const form = ref({
  name: '',
  type: 'cash',
  balance: '',
  icon: '💳',
  color: '#4ECDC4',
})

const toFixed = (val: number | string) => {
  if (typeof val === 'string') val = parseFloat(val) || 0
  return (val as number).toFixed(2)
}

const formatType = (type: string) => {
  const index = typeValues.indexOf(type)
  return index >= 0 ? typeOptions[index] : type
}

const onTypeChange = (e: any) => {
  typeIndex.value = e.detail.value
  form.value.type = typeValues[e.detail.value]
}

const fetchAccounts = async () => {
  try {
    const res: any = await getAccounts()
    accountList.value = res || []
  } catch (error) {
    console.error('获取账户失败', error)
  }
}

const handleAdd = () => {
  isEditing.value = false
  editingId.value = null
  typeIndex.value = 0
  form.value = {
    name: '',
    type: 'cash',
    balance: '',
    icon: '💳',
    color: '#4ECDC4',
  }
  formPopup.value.open()
}

const handleEdit = (acc: any) => {
  isEditing.value = true
  editingId.value = acc.id
  typeIndex.value = typeValues.indexOf(acc.type) || 0
  form.value = {
    name: acc.name,
    type: acc.type,
    balance: acc.balance?.toString() || '0',
    icon: acc.icon || '💳',
    color: acc.color || '#4ECDC4',
  }
  formPopup.value.open()
}

const handleSave = async () => {
  if (!form.value.name) {
    uni.showToast({ title: '请输入名称', icon: 'none' })
    return
  }

  try {
    const data = {
      name: form.value.name,
      type: form.value.type,
      balance: parseFloat(form.value.balance) || 0,
      icon: form.value.icon,
      color: form.value.color,
    }
    if (isEditing.value && editingId.value) {
      await updateAccount(editingId.value, data)
    } else {
      await createAccount(data)
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    formPopup.value.close()
    fetchAccounts()
  } catch (error: any) {
    uni.showToast({ title: error.message || '保存失败', icon: 'none' })
  }
}

const handleDelete = (acc: any) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除账户"${acc.name}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteAccount(acc.id)
          uni.showToast({ title: '删除成功', icon: 'success' })
          fetchAccounts()
        } catch (error: any) {
          uni.showToast({ title: error.message || '删除失败', icon: 'none' })
        }
      }
    },
  })
}

onMounted(() => {
  fetchAccounts()
})
</script>

<style scoped lang="scss">
.accounts-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.account-list {
  margin: 20rpx;

  .account-item {
    background: #fff;
    border-radius: 10rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;

    .account-icon {
      width: 80rpx;
      height: 80rpx;
      border-radius: 20rpx;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-right: 20rpx;

      text {
        font-size: 40rpx;
      }
    }

    .account-info {
      flex: 1;

      .account-name {
        display: block;
        font-size: 30rpx;
        font-weight: bold;
        margin-bottom: 8rpx;
      }

      .account-type {
        font-size: 24rpx;
        color: #999;
      }
    }

    .account-balance {
      text-align: right;
      margin-right: 30rpx;

      .balance-label {
        display: block;
        font-size: 22rpx;
        color: #999;
      }

      .balance-amount {
        display: block;
        font-size: 32rpx;
        font-weight: bold;
        color: #333;
      }
    }

    .account-actions {
      .action-btn {
        font-size: 24rpx;
        color: #1989fa;
        margin-left: 15rpx;

        &.delete {
          color: #ff4d4f;
        }
      }
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

      .input {
        border: 1px solid #eee;
        border-radius: 10rpx;
        padding: 20rpx;
        font-size: 28rpx;
      }

      .type-picker {
        border: 1px solid #eee;
        border-radius: 10rpx;
        padding: 20rpx;

        .picker-value {
          font-size: 28rpx;
        }
      }

      .color-picker {
        display: flex;
        flex-wrap: wrap;
        gap: 20rpx;

        .color-option {
          width: 60rpx;
          height: 60rpx;
          border-radius: 30rpx;

          &.active {
            border: 4rpx solid #333;
          }
        }
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
  }
}
</style>
