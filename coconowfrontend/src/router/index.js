import { createRouter, createWebHashHistory } from 'vue-router'
import UserSpace from '@/views/UserSpace.vue'
import Home from '@/views/Home.vue'
import AceEditor from '@/components/AceEditor.vue'
import axios from "axios"
import { ElSkeleton } from 'element-plus'

const routes = [
    {
        path: '/',
        name: '/',
        component: UserSpace,
        meta: {
            requireAuth: true,
        }
    }, {
        path: '/Login',
        name: 'Login',
        component: () => import('../components/Login.vue'),
        meta: {
            requireAuth: false,
        }
    }, {
        path: '/Register',
        name: 'Register',
        component: () => import('../components/Register.vue'),
        meta: {
            requireAuth: false,
        }
    }, {
        path: '/ForgetPassword',
        name: 'ForgetPassword',
        component: () => import('../components/ForgetPassword.vue'),
        meta: {
            requireAuth: false,
        }
    }, {
        path: '/UserSpace',
        name: 'UserSpace',
        component: UserSpace,
        meta: {
            requireAuth: true,
        }
    }, {
        path: '/Home',
        name: 'Home',
        component: Home,
        meta: {
            requireAuth: true,
        }
    },
    {
        path: '/Revise',
        name: 'Revise',
        component: () => import('../components/Revise.vue'),
        meta: {
            requireAuth: true,
        }
    },
    {
        path: '/:catchAll(.*)',
        name: 'NotFound',
        component: () => import('../components/404.vue'),
        meta: {
            requireAuth: false
        }
    },
    {
        path: '/Chat',
        component: () => import('../components/Chat.vue'),
        meta: {
            requireAuth: true,
        }
    }

]


const router = createRouter({
    //history: createWebHistory(process.env.BASE_URL),
    history: createWebHashHistory(),
    routes: routes,
})

router.beforeEach((to, from, next) => {
    if (to.meta.requireAuth == false) {
        next();
    } else {
        axios.get("api/accounts/getIdentity").then((response) => {
            if (response.data.isLogin === "False") {
                next("/Login")
            }
            else {
                next()
            }
        })
    }
})

export default router