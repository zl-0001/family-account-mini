<template>
  <view class="categories-container">
    <!-- Tab 切换 -->
    <view class="tab-selector">
      <view
        class="tab-btn"
        :class="{ active: activeType === 'expense' }"
        @click="activeType = 'expense'"
      >
        支出分类
      </view>
      <view
        class="tab-btn"
        :class="{ active: activeType === 'income' }"
        @click="activeType = 'income'"
      >
        收入分类
      </view>
    </view>

    <!-- 分类列表 -->
    <scroll-view class="category-list" scroll-y>
      <block v-for="cat in categoryTree" :key="cat.id">
        <view class="category-item parent" @click="toggleExpand(cat)">
          <text class="cat-expand">{{ cat.expanded ? '▼' : '▶' }}</text>
          <text class="cat-icon">{{ cat.icon || '📁' }}</text>
          <text class="cat-name">{{ cat.name }}</text>
          <view class="cat-actions">
            <text class="action-btn sort" @click.stop="moveCategory(cat, 'up')">↑</text>
            <text class="action-btn sort" @click.stop="moveCategory(cat, 'down')">↓</text>
            <text class="action-btn" @click.stop="handleEdit(cat)">编辑</text>
            <text class="action-btn delete" @click.stop="handleDelete(cat)">删除</text>
          </view>
        </view>
        <block v-if="cat.expanded" v-for="child in cat.children" :key="child.id">
          <view class="category-item child">
            <text class="cat-icon">{{ child.icon || '📁' }}</text>
            <text class="cat-name">{{ child.name }}</text>
            <view class="cat-actions">
              <text class="action-btn sort" @click.stop="moveCategory(child, 'up')">↑</text>
              <text class="action-btn sort" @click.stop="moveCategory(child, 'down')">↓</text>
              <text class="action-btn" @click.stop="handleEdit(child)">编辑</text>
              <text class="action-btn delete" @click.stop="handleDelete(child)">删除</text>
            </view>
          </view>
        </block>
      </block>
      <view class="list-bottom-placeholder"></view>
    </scroll-view>

    <!-- 添加按钮 -->
    <view class="add-btn-wrapper">
      <button class="add-btn" @click="handleAdd">添加分类</button>
    </view>

    <!-- 添加/编辑弹窗 -->
    <uni-popup ref="formPopup" type="bottom" :safe-area="false">
      <view class="form-popup">
        <view class="popup-header">
          <text>{{ isEditing ? '编辑分类' : '添加分类' }}</text>
          <text class="close" @click="formPopup.close()">×</text>
        </view>
        <view class="form-content">
          <view class="form-item">
            <text class="label">名称</text>
            <input v-model="form.name" placeholder="请输入分类名称" class="input" />
          </view>
          <view class="form-item">
            <text class="label">图标</text>
            <input v-model="form.icon" placeholder="请输入图标emoji" class="input" />
          </view>
          <view class="form-item">
            <text class="label">上级分类（可选）</text>
            <picker
              :value="parentIndex"
              :range="parentOptions"
              range-key="name"
              @change="onParentChange"
            >
              <view class="picker-value">
                {{ parentOptions[parentIndex]?.name || '无上级分类' }}
              </view>
            </picker>
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
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  reorderCategories,
} from '@/api'

const activeType = ref<'expense' | 'income'>('expense')
const categories = ref<any[]>([])
const formPopup = ref<any>(null)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  name: '',
  icon: '',
  parent_id: null as number | null,
})
const parentIndex = ref(0)

const parentOptions = computed(() => {
  const sameTypeCats = categoryList.value.filter((c: any) => c.id !== editingId.value)
  return [{ id: null, name: '无上级分类' }, ...sameTypeCats]
})

const categoryList = computed(() =>
  categories.value.filter((c) => c.type === activeType.value)
)

const expandState = ref<Record<number, boolean>>({})

const categoryTree = computed(() => {
  const list = categoryList.value
  const map = new Map<number | null, any[]>()
  const tree: any[] = []

  list.forEach((cat: any) => {
    const children = map.get(cat.parent_id) || []
    children.push({ ...cat, children: [] })
    map.set(cat.parent_id, children)
  })

  const roots = map.get(null) || []
  roots.forEach((root: any) => {
    root.children = map.get(root.id) || []
    root.expanded = expandState.value[root.id] !== false
    tree.push(root)
  })

  return tree
})

const toggleExpand = (cat: any) => {
  expandState.value[cat.id] = !(expandState.value[cat.id] !== false)
}

const fetchCategories = async () => {
  try {
    const res: any = await getCategories()
    categories.value = res || []
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

const handleAdd = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', icon: '', parent_id: null }
  parentIndex.value = 0
  formPopup.value.open()
}

const handleEdit = (cat: any) => {
  isEditing.value = true
  editingId.value = cat.id
  form.value = { name: cat.name, icon: cat.icon || '', parent_id: cat.parent_id }
  parentIndex.value = parentOptions.value.findIndex(
    (p: any) => p.id === cat.parent_id
  )
  formPopup.value.open()
}

const onParentChange = (e: any) => {
  parentIndex.value = e.detail.value
  form.value.parent_id = parentOptions.value[parentIndex.value].id
}

const handleSave = async () => {
  if (!form.value.name) {
    uni.showToast({ title: '请输入名称', icon: 'none' })
    return
  }

  try {
    if (isEditing.value && editingId.value) {
      await updateCategory(editingId.value, {
        name: form.value.name,
        icon: form.value.icon,
        parent_id: form.value.parent_id,
      })
    } else {
      await createCategory({
        name: form.value.name,
        type: activeType.value,
        icon: form.value.icon,
        parent_id: form.value.parent_id,
      })
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    formPopup.value.close()
    fetchCategories()
  } catch (error: any) {
    uni.showToast({ title: error.message || '保存失败', icon: 'none' })
  }
}

const moveCategory = async (cat: any, direction: 'up' | 'down') => {
  const flat = categoryList.value
  const sameLevel = flat.filter((c: any) =>
    cat.parent_id === null ? c.parent_id === null : c.parent_id === cat.parent_id
  )
  const idx = sameLevel.findIndex((c: any) => c.id === cat.id)
  const targetIdx = direction === 'up' ? idx - 1 : idx + 1
  if (targetIdx < 0 || targetIdx >= sameLevel.length) return

  const a = sameLevel[idx]
  const b = sameLevel[targetIdx]

  try {
    await reorderCategories([
      { id: a.id, sort_order: targetIdx },
      { id: b.id, sort_order: idx },
    ])
    fetchCategories()
  } catch (error: any) {
    uni.showToast({ title: error.message || '排序失败', icon: 'none' })
  }
}

const handleDelete = (cat: any) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除分类"${cat.name}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteCategory(cat.id)
          uni.showToast({ title: '删除成功', icon: 'success' })
          fetchCategories()
        } catch (error: any) {
          uni.showToast({ title: error.message || '删除失败', icon: 'none' })
        }
      }
    },
  })
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped lang="scss">
.categories-container {
  height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-selector {
  flex-shrink: 0;
  display: flex;
  background: #fff;
  padding: 20rpx;

  .tab-btn {
    flex: 1;
    text-align: center;
    padding: 20rpx;
    font-size: 28rpx;
    border-radius: 10rpx;

    &.active {
      background: #1989fa;
      color: #fff;
    }
  }
}

.category-list {
  flex: 1;
  height: 0;
  padding: 20rpx;

  .category-item {
    background: #fff;
    border-radius: 10rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;

    &.parent {
      background: #e8f4ff;
    }

    &.child {
      margin-left: 40rpx;
      background: #fafafa;
    }

    .cat-expand {
      font-size: 24rpx;
      color: #999;
      margin-right: 10rpx;
      width: 30rpx;
    }

    .cat-icon {
      font-size: 36rpx;
      margin-right: 20rpx;
    }

    .cat-name {
      flex: 1;
      font-size: 28rpx;
    }

    .cat-actions {
      .action-btn {
        font-size: 24rpx;
        color: #1989fa;
        margin-left: 20rpx;

        &.sort {
          color: #999;
          font-size: 28rpx;
        }

        &.delete {
          color: #ff4d4f;
        }
      }
    }
  }
}

.list-bottom-placeholder {
  height: 20rpx;
}

.add-btn-wrapper {
  flex-shrink: 0;
  padding: 20rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 45rpx;
  height: 90rpx;
  line-height: 90rpx;
  font-size: 32rpx;
}

.form-popup {
  background: #fff;
  border-radius: 20rpx 20rpx 0 0;
  padding: 30rpx;
  padding-bottom: calc(30rpx + env(safe-area-inset-bottom));

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

      .picker-value {
        border: 1px solid #eee;
        border-radius: 10rpx;
        padding: 20rpx;
        font-size: 28rpx;
        background: #fff;
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
