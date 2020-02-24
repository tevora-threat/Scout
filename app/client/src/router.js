import Vue from 'vue'
import Router from 'vue-router'
import Settings from './views/Settings.vue'
import Timeline from './views/Timeline.vue'
import AllPlates from './views/AllPlates.vue'
import AllFaces from './views/AllFaces.vue'
import Recent from './views/Recent.vue'

Vue.use(Router)

let router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [{
      path: '*',
      redirect: '/'
    },
    {
      path: '/',
      name: 'Recent',
      component: Recent,
      meta: {
        requiresAuth: false
      },
      props: true
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings,
      meta: {
        requiresAuth: false
      }
    }, {
      path: '/timeline',
      name: 'Timeline',
      component: Timeline,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/plates',
      name: 'AllPlates',
      component: AllPlates,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/faces',
      name: 'AllFaces',
      component: AllFaces,
      meta: {
        requiresAuth: false
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  //where you'd handle auth stuff once implemented (I prefer firebase)
  next()
})

export default router