import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import i18n from './locales' // 【新增】引入 i18n

const app = createApp(App)

app.use(router)
app.use(i18n) // 【新增】挂载

app.mount('#app')