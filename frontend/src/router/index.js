import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '../views/ProductList.vue'
import Calendar from '../views/Calendar.vue'
import RequirementDetails from '../views/RequirementDetails.vue'

const routes = [
    {
        path: '/',
        redirect: '/products'
    },
    {
        path: '/products',
        name: 'Products',
        component: ProductList
    },
    {
        path: '/calendar',
        name: 'Calendar',
        component: Calendar
    },
    {
        path: '/requirements',
        name: 'Requirements',
        component: RequirementDetails
    }
]

export default createRouter({
    history: createWebHistory(),
    routes
}) 