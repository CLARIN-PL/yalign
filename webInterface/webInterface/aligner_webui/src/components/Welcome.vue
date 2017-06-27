<template>
<div class="container">
  <div class="row">
    <div class="col-sm-12">
      <h1>Loading...</h1>
    </div>
  </div>
</div>
</template>

<script>
import router from '@/router/index'
import conf from '@/conf'
import auth from '@/auth'
import api from '@/api'

export default {
  name: 'welcome',
  data () {
    return {
    }
  },
  methods: {
    start () {
      conf.started = true
      if (conf.openRoute !== null) {
        router.push(conf.openRoute)
      } else {
        router.push({
          name: 'aligner',
          params: {id: auth.data.user.id}
        })
      }
    },
    updateLangPairs () {
      return api.langpairs.get().then(langs => {
        conf.langPairs = langs.data
      })
    }
  },
  created () {
    var self = this
    if (conf.userIdFromUrl !== null) {
      auth.setCustom({id: conf.userIdFromUrl}, conf.userIdFromUrl)
      this.updateLangPairs()
        .then(this.start)
    } else if (auth.loadSaved()) {
      this.updateLangPairs()
        .then(this.start)
    } else {
      auth.signin()
        .then(self.updateLangPairs)
        .then(self.start)
    }
  }
}
</script>

<style scoped>
</style>
