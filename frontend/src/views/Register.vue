<template>
  <el-card class="register-card">
    <h2>注册</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @submit.prevent>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" autocomplete="username" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" autocomplete="new-password" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm">
        <el-input v-model="form.confirm" type="password" autocomplete="new-password" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="onSubmit">注册</el-button>
        <el-button link @click="$router.push('/login')">已有账号? 去登录</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const form = reactive({ username: '', password: '', confirm: '' })
const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (_, v, cb) => { v !== form.password ? cb(new Error('两次输入不一致')) : cb() }, trigger: 'blur' }
  ],
}

const onSubmit = () => {
  formRef.value.validate(async (ok) => {
    if (!ok) return
    loading.value = true
    try {
      await api.post('/auth/register', { username: form.username, password: form.password })
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (e) {
      ElMessage.error(e?.response?.data?.msg || '注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-card { max-width: 480px; margin: 80px auto; }
</style>


