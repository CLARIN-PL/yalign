import _ from 'lodash'
import auth from '@/auth'

function buildUrl (templ, params) {
  var chunks = templ.split('{}')
  var url = ''
  chunks.forEach(function (c, i) {
    url += c
    if (i < params.length) {
      url += encodeURIComponent(params[i])
    }
  })
  return url
}

function buildUrlParams (params) {
  var query = ''
  _.forOwn(params, (value, key) => {
    query += encodeURIComponent(key) + '=' + encodeURIComponent(value)
  })
  return query
}

export default class Http {

  constructor () {
    this._method = null
    this._url = null
    this._params = {}
    this._payload = null
    this._file = null
    this._auth = false
  }

  url (targetUrl) {
    var params = []
    for (var i = 1; i < arguments.length; i++) {
      params.push(arguments[i])
    }
    this._url = buildUrl(targetUrl, params)
    return this
  }

  get () {
    this._method = 'GET'
    return this
  }

  post () {
    this._method = 'POST'
    return this
  }

  put () {
    this._method = 'PUT'
    return this
  }

  params (queryParams) {
    if (_.isUndefined(queryParams)) {
      return this
    }
    _.assign(this._params, queryParams)
    return this
  }

  payload (payload) {
    this._payload = payload
    return this
  }

  file (file) {
    this._file = file
    return this
  }

  auth () {
    this._auth = true
    return this
  }

  promise () {
    if (this._file === null) {
      return this.promiseRequest()
    } else {
      return this.promiseUpload()
    }
  }

  promiseRequest () {
    var self = this
    if (self._auth) {
      self.params({token: auth.data.token})
    }
    var requestPromise = new Promise(function (resolve, reject) {
      var request = new XMLHttpRequest()
      request.onload = function (e) {
        if (request.status === 200) {
          resolve(JSON.parse(request.responseText))
        } else {
          try {
            reject(JSON.parse(request.responseText))
          } catch (e) {
            reject({'error': 'Server error ' + request.status.toString()})
          }
        }
      }

      request.onerror = function () {
        reject({'error': 'request failed'})
      }

      var query = buildUrlParams(self._params)
      if (query === '') {
        request.open(self._method, self._url)
      } else {
        request.open(self._method, self._url + '?' + query)
      }
      request.setRequestHeader('Content-Type', 'application/json')
      if (self._payload === null) {
        request.send()
      } else {
        request.send(JSON.stringify(self._payload))
      }
    })
    return requestPromise
  }

  promiseUpload () {
    var self = this
    if (self._auth) {
      self.params({token: auth.data.token})
    }
    var requestPromise = new Promise(function (resolve, reject) {
      var request = new XMLHttpRequest()
      var fd = new FormData()
      fd.append(self._file.name, self._file)

      request.onload = function (e) {
        if (request.status === 200) {
          resolve()
        } else {
          reject({'error': 'Server error ' + request.status.toString()})
        }
      }

      request.onerror = function () {
        reject({'error': 'request failed'})
      }

      var query = buildUrlParams(self._params)
      if (query === '') {
        request.open(self._method, self._url)
      } else {
        request.open(self._method, self._url + '?' + query)
      }
      request.send(fd)
    })

    return requestPromise
  }

}
