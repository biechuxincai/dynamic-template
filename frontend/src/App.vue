<template>
  <el-container style="height: 100vh;">
    <el-header>
      <div style="display:flex;align-items:center;gap:16px;">
        <strong>模板平台</strong>
        <el-menu mode="horizontal" :router="true" style="flex:1;">
          <el-menu-item index="/templates">模板列表</el-menu-item>
          <el-menu-item index="/editor">新建模板</el-menu-item>
          <div style="flex:1"></div>
          <template v-if="currentUser">
            <el-sub-menu index="user">
              <template #title>
                <span>👤 {{ currentUser.username }}</span>
              </template>
              <el-menu-item index="/login" @click="logout">退出登录</el-menu-item>
            </el-sub-menu>
          </template>
          <template v-else>
            <el-menu-item index="/login">登录</el-menu-item>
            <el-menu-item index="/register">注册</el-menu-item>
          </template>
        </el-menu>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from './store/auth'

const { state, logout } = useAuthStore()
const currentUser = computed(() => state.user)
</script>

<style>
html, body, #app { height: 100%; margin: 0; }
</style>


