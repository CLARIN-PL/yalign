import api from '@/api'

export default {
  data: {
    user: null,
    token: null
  },
  signin () {
    var self = this
    var promise = api.signin.post()
      .then(user => {
        self.data.user = user
        self.data.token = user.id
        self.save()
        return self.data
      })
    return promise
  },
  loadSaved () {
    var savedId = localStorage.getItem('aligner-user-id')
    var savedToken = localStorage.getItem('aligner-user-token')
    if (savedId === null || savedToken == null) {
      return false
    } else {
      this.data.user = {id: savedId}
      this.data.token = savedToken
      return true
    }
  },
  save () {
    localStorage.setItem('aligner-user-id', this.data.user.id)
    localStorage.setItem('aligner-user-token', this.data.token)
  },
  setCustom (user, token) {
    this.data.user = user
    this.data.token = token
    this.save()
  }
}
