<template>
  <el-card class="login-card">
    <h2>登录</h2>
    <el-form :model="form" @submit.prevent="onSubmit" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" autocomplete="username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" autocomplete="current-password" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit" :loading="loading">登录</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const loading = ref(false)

const onSubmit = async () => {
  loading.value = true
  try {
    const { data } = await api.post('/auth/login', form)
    const { login } = useAuthStore()
    login(data.user, data.access_token)
    ElMessage.success('登录成功')
    router.push('/templates')
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card { max-width: 420px; margin: 80px auto; }
</style>


