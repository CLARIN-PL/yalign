<template>
<div class="container">
  <div class="row">
    <div class="col-sm-12">
      <h1>Aligner | File Selector</h1>
      <form class="form-horizontal" v-if="status === 'new'" v-on:submit="upload()">
        <div class="form-group">
          <label class="col-sm-2 control-label">Aligning method</label>
          <div class="col-sm-10">
            <select class="form-control" v-model="alignTask.method">
              <option v-for="method in alignMethods" v-bind:value="method">{{ titles.methods[method] }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-2 control-label">Languages</label>
          <div class="col-sm-10">
            <select class="form-control" v-model="alignTask.langs">
              <option v-for="langPair in langs" v-bind:value="langPair">{{ langPair[0] }}-{{ langPair[1] }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-2 control-label">Output format</label>
          <div class="col-sm-10">
            <select class="form-control" v-model="alignTask.output">
              <option v-for="output in outputFormats" v-bind:value="output">{{ titles.formats[output] }}</option>
            </select>
          </div>
        </div>
        <div class="form-group" v-for="(pair, index) in alignTask.filePairs">
          <label class="col-sm-2 control-label">File pair {{ index + 1 }}</label>
          <div class="col-sm-5">
            {{ pair[0].name }}
          </div>
          <div class="col-sm-5">
            {{ pair[1].name }}
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-2 control-label">File pair {{ alignTask.filePairs.length + 1 }}</label>
          <div class="col-sm-5">
            <button type="button" class="btn btn-default" v-on:click="selectFile1()">File ({{ getLang(0) }})</button>
            <input type="file" ref="newFileInput1" v-on:change="setFile1()" style="display: none">
            <span v-if="newFile1 !== null">{{ newFile1.name }}</span>
          </div>
          <div class="col-sm-5">
            <button type="button" class="btn btn-default" v-on:click="selectFile2()">File ({{ getLang(1) }})</button>
            <input type="file" ref="newFileInput2" v-on:change="setFile2()" style="display: none">
            <span v-if="newFile2 !== null">{{ newFile2.name }}</span>
          </div>
        </div>
        <div class="form-group">
          <div class="col-sm-offset-2 col-sm-10">
            <button type="submit" class="btn btn-success" v-bind:disabled="!isReady()">Align</button>
          </div>
        </div>
      </form>
      <div v-if="status === 'uploading'">
        <b>Uploading...</b>
      </div>
      <div v-if="status === 'done'">
        <div><b>Aligning started... When finished result will show up in Aligned Files table</b></div>
        <div><button type="button" class="btn btn-success" v-on:click="resetForm()">Align more</button></div>
      </div>
      <my-tasks></my-tasks>
    </div>
  </div>
</div>
</template>

<script>
import router from '@/router/index'
import conf from '@/conf'
import api from '@/api'

export default {
  name: 'aligner',
  data () {
    return {
      titles: conf.titles,
      status: 'new',
      alignMethods: [
        'yalign',
        'hunalign'
      ],
      outputFormats: [
        'plaintext',
        'tmx',
        'tsv'
      ],
      langs: [],
      alignTask: {
        method: 'yalign',
        langs: null,
        output: 'plaintext',
        filePairs: []
      },
      newFile1: null,
      newFile2: null
    }
  },
  methods: {
    getLang (id) {
      if (this.alignTask.langs !== null) {
        return this.alignTask.langs[id]
      } else {
        return ''
      }
    },
    isReady () {
      return this.status === 'new' && this.alignTask.filePairs.length > 0
    },
    selectFile1 () {
      this.$refs.newFileInput1.click()
    },
    setFile1 () {
      if (this.$refs.newFileInput1.files.length > 0) {
        this.newFile1 = this.$refs.newFileInput1.files[0]
      }
      this.updateFilesList()
    },
    selectFile2 () {
      this.$refs.newFileInput2.click()
    },
    setFile2 () {
      if (this.$refs.newFileInput2.files.length > 0) {
        this.newFile2 = this.$refs.newFileInput2.files[0]
      }
      this.updateFilesList()
    },
    updateFilesList () {
      if (this.newFile1 !== null && this.newFile2 !== null) {
        this.alignTask.filePairs.push([this.newFile1, this.newFile2])
        this.newFile1 = null
        this.newFile2 = null
      }
    },
    upload () {
      var self = this
      if (this.status !== 'new') {
        return
      }
      this.status = 'uploading'
      var taskData = {
        'method': this.alignTask.method,
        'output': this.alignTask.output,
        'lang1': this.alignTask.langs[0],
        'lang2': this.alignTask.langs[1]
      }
      var taskPromise = api.tasks.post(taskData)
      taskPromise.then(task => {
        var promises = []
        self.alignTask.filePairs.forEach((pair, i) => {
          promises.push(
            api.tasksByIdByPairIdByLangInputPairs.post(
              task.id,
              i.toString(),
              self.alignTask.langs[0],
              pair[0]
            )
          )
          promises.push(
            api.tasksByIdByPairIdByLangInputPairs.post(
              task.id,
              i.toString(),
              self.alignTask.langs[1],
              pair[1]
            )
          )
        })
        Promise.all(promises)
          .then(() => api.taskByIdEnqueued.put(task.id))
          .then(() => {
            self.status = 'done'
            return null
          })
      })
    },

    resetForm () {
      this.alignTask = {
        method: 'yalign',
        langs: conf.langPairs[0],
        output: 'plaintext',
        filePairs: []
      }
      this.newFile1 = null
      this.newFile2 = null
      this.status = 'new'
    }
  },
  beforeCreate () {
    if (!conf.started) {
      conf.userIdFromUrl = this.$route.params.id
      conf.openRoute = {
        name: this.$route.name,
        params: this.$route.params
      }
      router.push({
        name: 'welcome'
      })
    }
  },
  created () {
    if (!conf.started) {
      return
    }
    this.langs = conf.langPairs
    this.alignTask.langs = conf.langPairs[0]
  }
}
</script>

<style scoped>
</style>
