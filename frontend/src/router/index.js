import { createRouter, createWebHistory } from 'vue-router'
import Calendar from '../views/Calendar.vue'
import RequirementDetails from '../views/RequirementDetails.vue'

const routes = [
    {
        path: '/',
        redirect: '/products'
    },
    {
        path: '/calendar',
        name: 'Calendar',
        component: Calendar
    },
    {
        path: '/requirements',
        name: 'RequirementDetails',
        component: RequirementDetails
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router 