import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import VueAxios from 'vue-axios'
import ElementPlus from 'element-plus';
import { Expand } from '@element-plus/icons'
import 'element-plus/theme-chalk/index.css';

import locale from 'element-plus/lib/locale/lang/zh-cn'

const app = createApp(App).use(VueAxios, axios).use(router).use(ElementPlus, { locale }).mount('#app')
    //app.component('expand', Expand)
    //app.mount('#app')