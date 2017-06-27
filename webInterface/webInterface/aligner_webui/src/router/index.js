import Vue from 'vue'
import Router from 'vue-router'
import Aligner from '@/components/Aligner'
import Welcome from '@/components/Welcome'
import '@/assets/css/bootstrap.css'
import '@/assets/css/base.css'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/aligner/:id',
      name: 'aligner',
      component: Aligner
    },
    {
      path: '/',
      name: 'welcome',
      component: Welcome
    }
  ]
})
