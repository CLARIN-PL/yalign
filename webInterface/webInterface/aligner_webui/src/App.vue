<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
import Vue from 'vue'
import MyTasks from '@/components/MyTasks'

Vue.component('my-tasks', MyTasks)

export default {
  name: 'app'
}
</script>

<style>
#app {
}
</style>
