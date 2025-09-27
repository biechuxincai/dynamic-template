<template>
  <div>
    <h2>预览</h2>
    <el-form :model="values" label-width="140px" style="max-width:1000px;">
      <el-form-item v-for="v in variables" :key="v.name" :label="labelOf(v)">
        <template v-if="v.type === 'boolean'">
          <el-switch v-model="values[v.name]" />
        </template>
        <template v-else-if="v.type === 'number'">
          <el-input-number v-model="values[v.name]" :controls="true" :step="1" style="width: 240px;" />
        </template>
        <template v-else-if="v.type === 'enum' && v.options && Array.isArray(v.options)">
          <el-select v-model="values[v.name]" style="width: 320px;">
            <el-option v-for="opt in v.options" :key="String(opt.value ?? opt)" :label="String(opt.label ?? opt)" :value="opt.value ?? opt" />
          </el-select>
        </template>
        <template v-else-if="v.type === 'text'">
          <el-input v-model="values[v.name]" type="textarea" :autosize="{ minRows: 3 }" :placeholder="v.description || v.name" />
        </template>
        <template v-else-if="v.type === 'json'">
          <el-input v-model="jsonInputs[v.name]" type="textarea" :autosize="{ minRows: 3 }" placeholder="输入 JSON，如: " />
          <div v-if="jsonErrors[v.name]" style="color:#d03050; font-size:12px; margin-top:4px;">{{ jsonErrors[v.name] }}</div>
        </template>
        <template v-else>
          <el-input v-model="values[v.name]" :placeholder="v.description || v.name" />
        </template>
      </el-form-item>

      <el-divider>高级：附加上下文(JSON)</el-divider>
      <el-form-item label="context">
        <el-input v-model="extraContextInput" type="textarea" :autosize="{ minRows: 3 }" placeholder="可选，额外的 JSON 上下文，会与上面变量合并" />
        <div v-if="extraContextError" style="color:#d03050; font-size:12px; margin-top:4px;">{{ extraContextError }}</div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="render" :loading="loading">渲染</el-button>
      </el-form-item>
    </el-form>

    <el-card v-if="preview" style="white-space:pre-wrap;">
      <pre style="white-space:pre-wrap;">{{ preview }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client'
import { ElMessage } from 'element-plus'

const route = useRoute()
const id = route.params.id
const variables = ref([])
const values = reactive({})
const loading = ref(false)
const preview = ref('')
const jsonInputs = reactive({})
const jsonErrors = reactive({})
const extraContextInput = ref('')
const extraContextError = ref('')

const labelOf = (v) => `${v.name}${v.required ? ' *' : ''}`

const load = async () => {
  const { data } = await api.get(`/templates/${id}`)
  variables.value = data.variables || []
  variables.value.forEach(v => {
    if (v.type === 'boolean') values[v.name] = Boolean(v.default ?? false)
    else if (v.type === 'number') values[v.name] = Number(v.default ?? 0)
    else if (v.type === 'json') jsonInputs[v.name] = v.default ? JSON.stringify(v.default, null, 2) : ''
    else values[v.name] = v.default ?? ''
  })
}

const render = async () => {
  loading.value = true
  try {
    // parse JSON inputs
    const payload = { ...values }
    Object.keys(jsonInputs).forEach((key) => {
      const raw = jsonInputs[key]
      if (!raw || !raw.trim()) { payload[key] = null; jsonErrors[key] = '' ; return }
      try {
        payload[key] = JSON.parse(raw)
        jsonErrors[key] = ''
      } catch (e) {
        jsonErrors[key] = '无效的 JSON'
      }
    })

    // merge extra context
    let extra = null
    extraContextError.value = ''
    if (extraContextInput.value && extraContextInput.value.trim()) {
      try { extra = JSON.parse(extraContextInput.value) }
      catch { extraContextError.value = '附加上下文不是有效 JSON' }
    }
    const merged = extra && typeof extra === 'object' ? { ...payload, ...extra } : payload

    const { data } = await api.post(`/templates/${id}/render`, { values: merged })
    preview.value = data.preview
    ElMessage.success('渲染成功')
  } catch (e) {
    const detail = (e.response && e.response.data && (e.response.data.detail || e.response.data.msg))
    preview.value = detail || String(e)
    ElMessage.error(detail || '渲染失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>


