<template>
<div v-show="tasks.length > 0">
  <h1>Aligned Files</h1>
  <table class="table table-striped">
    <thead>
      <tr>
        <th>
          Task ID
        </th>
        <th>
          Aligner
        </th>
        <th>
          Status
        </th>
        <th>
          Download Link
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="task in selected">
        <td>
          {{ task.id }}
        </td>
        <td>
          {{ titles.methods[task.data.method] }}
        </td>
        <td>
          {{ task.status }}
        </td>
        <td>
          <span v-if="task.result === null">
            processing...
          </span>
          <span v-else>
            <a class="btn btn-success" v-bind:href="task.result + '?token=' + auth.data.token" target="_blank">download</a>
          </span>
        </td>
      </tr>
    </tbody>
  </table>
  <nav>
    <ul class="pagination">
      <li>
      <a href="#" v-on:click.prevent="prevPage()">
        <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
      </a>
      </li>
      <li>
      <a href="#" v-on:click.prevent="nextPage()">
        <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
      </a>
      </li>
    </ul>
  </nav>
</div>
</template>

<script>
import _ from 'lodash'
import conf from '@/conf'
import api from '@/api'
import auth from '@/auth'

export default {
  name: 'my-tasks',
  data () {
    return {
      titles: conf.titles,
      timer: null,
      auth: auth,
      tasks: [],
      pages: [],
      perPage: 4,
      page: 0,
      selected: []
    }
  },
  methods: {
    nextPage () {
      this.page += 1
      this.updatePage()
    },
    prevPage () {
      this.page -= 1
      this.updatePage()
    },
    updatePage () {
      if (this.page >= this.pages.length) {
        this.page = this.pages.length - 1
      }
      if (this.page < 0) {
        this.page = 0
      }
      this.selected = this.pages[this.page]
    },
    getTasks () {
      api.meTasks.get().then(tasks => {
        this.tasks = tasks.data
        this.pages = _.chunk(this.tasks, this.perPage)
        this.updatePage()
      })
    }
  },
  created () {
    if (!conf.started) {
      return
    }
    this.getTasks()
    this.timer = setInterval(this.getTasks, 5000)
  },
  destroyed () {
    if (this.timer !== null) {
      clearInterval(this.timer)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
