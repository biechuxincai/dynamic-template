<template>
  <div>
    <h2>{{ id ? '编辑模板' : '新建模板' }}</h2>
    <el-form :model="form" label-width="100px" style="max-width:none;">
      <el-form-item label="名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="标识(slug)">
        <el-input v-model="form.slug" :disabled="!!id" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" />
      </el-form-item>
      <el-divider>变量</el-divider>
      <el-form-item label="变量列表">
        <div style="width:100%">
          <el-table :data="form.variables" size="small">
            <el-table-column prop="name" label="名称" width="180">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="变量名" />
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="140">
              <template #default="{ row }">
                <el-select v-model="row.type" placeholder="类型">
                  <el-option label="string" value="string" />
                  <el-option label="number" value="number" />
                  <el-option label="boolean" value="boolean" />
                  <el-option label="enum" value="enum" />
                  <el-option label="json" value="json" />
                  <el-option label="text" value="text" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="required" label="必填" width="80">
              <template #default="{ row }">
                <el-switch v-model="row.required" />
              </template>
            </el-table-column>
            <el-table-column prop="default" label="默认值">
              <template #default="{ row }">
                <el-input v-if="row.type!=='json'" v-model="row.default" placeholder="默认值" />
                <el-input v-else type="textarea" :autosize="{ minRows: 2 }" v-model="row.default" placeholder='JSON 默认值，如 {"a":1}' />
              </template>
            </el-table-column>
            <el-table-column prop="options" label="枚举选项">
              <template #default="{ row }">
                <el-input v-model="row.optionsText" placeholder='仅 enum：以逗号分隔，或输入JSON数组' />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述">
              <template #default="{ row }">
                <el-input v-model="row.description" placeholder="描述" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ $index }">
                <el-button link type="danger" @click="removeVar($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top:8px;">
            <el-button size="small" @click="addVar">新增变量</el-button>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="内容" style="align-items: stretch;">
        <MonacoEditor v-model="form.content" language="jinja" height="70vh" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save" :loading.fullscreen.lock="saving">保存</el-button>
        <el-button @click="toPreview" :disabled="!id">预览</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/client'
import MonacoEditor from '../components/MonacoEditor.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = reactive({ name: '', slug: '', description: '', content: '', variables: [] })
const saving = ref(false)

const load = async () => {
  if (!id) return
  const { data } = await api.get(`/templates/${id}`)
  Object.assign(form, data)
  // prepare edit helpers
  form.variables = (form.variables || []).map(v => ({
    ...v,
    optionsText: v.options ? (Array.isArray(v.options) ? v.options.join(',') : JSON.stringify(v.options)) : ''
  }))
}

const save = async () => {
  saving.value = true
  try {
    // normalize variables
    const normVars = (form.variables || []).map(v => {
      let options = undefined
      const text = (v.optionsText || '').trim()
      if (v.type === 'enum' && text) {
        // try JSON first, else split by comma
        try { options = JSON.parse(text) }
        catch { options = text.split(',').map(s => s.trim()).filter(Boolean) }
      }
      let defVal = v.default
      if (v.type === 'json' && typeof defVal === 'string' && defVal.trim()) {
        try { defVal = JSON.parse(defVal) } catch { /* keep as string */ }
      }
      return {
        name: v.name,
        type: v.type || 'string',
        required: !!v.required,
        default: defVal,
        options,
        description: v.description,
      }
    })

    if (id) {
      await api.put(`/templates/${id}` , { ...form, variables: normVars })
      ElMessage.success('更新成功')
    } else {
      const { data } = await api.post('/templates', { ...form, variables: normVars })
      ElMessage.success('创建成功')
      router.replace(`/editor/${data.id}`)
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '保存失败')
  } finally {
    saving.value = false
  }
}

const addVar = () => {
  form.variables.push({ name: '', type: 'string', required: false, default: '', optionsText: '', description: '' })
}
const removeVar = (i) => {
  form.variables.splice(i, 1)
}

const toPreview = () => router.push(`/preview/${id}`)

onMounted(load)
</script>


