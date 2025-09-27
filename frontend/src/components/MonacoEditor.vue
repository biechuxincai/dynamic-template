<template>
  <div ref="root" :style="{ width: '100%', height, border: '1px solid #e5e7eb' }"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import monaco from '../monaco'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'jinja' },
  height: { type: String, default: '500px' },
})
const emit = defineEmits(['update:modelValue'])

const root = ref(null)
let editor

onMounted(() => {
  editor = monaco.editor.create(root.value, {
    value: props.modelValue,
    language: props.language,
    automaticLayout: true,
    minimap: { enabled: false },
  })
  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue())
  })
})

watch(() => props.modelValue, (v) => {
  if (editor && v !== editor.getValue()) editor.setValue(v || '')
})

onBeforeUnmount(() => {
  if (editor) editor.dispose()
})
</script>


