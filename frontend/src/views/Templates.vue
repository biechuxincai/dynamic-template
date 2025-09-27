<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
      <h2>模板列表</h2>
      <el-button type="primary" @click="$router.push('/editor')">新建模板</el-button>
    </div>
    <el-table :data="templates" style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="slug" label="标识" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" @click="preview(row)">预览</el-button>
          <el-popconfirm title="确认删除?" @confirm="remove(row)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
  </template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api/client'
import { ElMessage } from 'element-plus'

const templates = ref([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/templates')
    templates.value = data
  } finally {
    loading.value = false
  }
}

const edit = (row) => {
  return window.location.assign(`/editor/${row.id}`)
}
const preview = (row) => {
  return window.location.assign(`/preview/${row.id}`)
}
const remove = async (row) => {
  try {
    await api.delete(`/templates/${row.id}`)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(load)
</script>


