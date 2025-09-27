import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Templates from './views/Templates.vue'
import Editor from './views/Editor.vue'
import Preview from './views/Preview.vue'

export default [
  { path: '/', redirect: '/templates' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/templates', component: Templates },
  { path: '/editor/:id?', component: Editor, props: true },
  { path: '/preview/:id', component: Preview, props: true },
]


