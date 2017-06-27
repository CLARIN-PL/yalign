import Http from '@/http'

export default {
  signin: {
    post: () => new Http()
      .url('/api/users/signin')
      .post()
      .promise()
  },

  langpairs: {
    get: () => new Http()
      .url('/api/langpairs')
      .get()
      .auth()
      .promise()
  },

  tasks: {
    post: data => new Http()
      .url('/api/tasks')
      .post()
      .auth()
      .payload(data)
      .promise()
  },

  meTasks: {
    get: () => new Http()
      .url('/api/me/tasks')
      .get()
      .auth()
      .promise()
  },

  tasksByIdByPairIdByLangInputPairs: {
    post: (taskId, pairId, lang, file) => new Http()
      .url('/api/tasks/{}/{}/{}/inputpairs', taskId, pairId, lang)
      .post()
      .auth()
      .file(file)
      .promise()
  },

  taskByIdEnqueued: {
    put: taskId => new Http()
      .url('/api/tasks/{}/enqueued', taskId)
      .put()
      .auth()
      .promise()
  }
}
