<template>
  <scroll-view scroll-y class="category-picker">
    <block v-for="group in tree" :key="group.id">
      <!-- 有子分类：父分类作为可展开的分组标题 -->
      <view
        v-if="group.children.length"
        class="cat-group-title"
        @click="toggleExpand(group.id)"
      >
        <text class="cat-arrow">{{ group.expanded ? '▼' : '▶' }}</text>
        <text class="cat-group-icon">{{ group.icon || '📁' }}</text>
        <text class="cat-group-name">{{ group.name }}</text>
      </view>
      <!-- 展开后渲染子分类（叶子，可选） -->
      <block v-if="group.children.length && group.expanded">
        <view
          v-for="child in group.children"
          :key="child.id"
          class="cat-leaf"
          :class="{ active: selectedId === child.id }"
          @click="emit('pick', child)"
        >
          <text class="cat-leaf-icon">{{ child.icon || '📁' }}</text>
          <text class="cat-leaf-name">{{ child.name }}</text>
          <text v-if="selectedId === child.id" class="cat-check">✓</text>
        </view>
      </block>
      <!-- 无子分类：作为叶子可选 -->
      <view
        v-if="!group.children.length"
        class="cat-leaf"
        :class="{ active: selectedId === group.id }"
        @click="emit('pick', group)"
      >
        <text class="cat-leaf-icon">{{ group.icon || '📁' }}</text>
        <text class="cat-leaf-name">{{ group.name }}</text>
        <text v-if="selectedId === group.id" class="cat-check">✓</text>
      </view>
    </block>
    <view class="cat-list-bottom"></view>
  </scroll-view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  categories: any[]
  selectedId?: number
}>()

const emit = defineEmits<{
  (e: 'pick', cat: any): void
}>()

const expandState = ref<Record<number, boolean>>({})

// 扁平分类 → 父子树，仅叶子（无子项）可选
const tree = computed(() => {
  const list = props.categories
  const childrenMap = new Map<number | null, any[]>()
  list.forEach((c: any) => {
    const arr = childrenMap.get(c.parent_id) || []
    arr.push(c)
    childrenMap.set(c.parent_id, arr)
  })
  const roots = childrenMap.get(null) || []
  return roots.map((r: any) => ({
    ...r,
    children: childrenMap.get(r.id) || [],
    expanded: expandState.value[r.id] !== false,
  }))
})

const toggleExpand = (id: number) => {
  expandState.value[id] = !(expandState.value[id] !== false)
}
</script>

<style scoped lang="scss">
.category-picker {
  max-height: 70vh;

  .cat-group-title {
    display: flex;
    align-items: center;
    padding: 24rpx 30rpx;
    background: #f7f7f7;

    .cat-arrow {
      font-size: 22rpx;
      margin-right: 12rpx;
      color: #999;
    }

    .cat-group-icon {
      font-size: 32rpx;
      margin-right: 14rpx;
    }

    .cat-group-name {
      font-size: 26rpx;
      color: #666;
    }
  }

  .cat-leaf {
    display: flex;
    align-items: center;
    padding: 26rpx 30rpx 26rpx 76rpx;
    border-bottom: 1rpx solid #f5f5f5;

    .cat-leaf-icon {
      font-size: 34rpx;
      margin-right: 16rpx;
    }

    .cat-leaf-name {
      flex: 1;
      font-size: 28rpx;
      color: #333;
    }

    .cat-check {
      font-size: 32rpx;
      color: #07c160;
    }

    &.active {
      background: #f0fff4;
    }
  }

  .cat-list-bottom {
    height: 20rpx;
  }
}
</style>
