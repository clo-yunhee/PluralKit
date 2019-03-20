function handleErrors(response) {
  if (response.ok && response.status >= 200 && response.status < 300) {
    return response
  } else {
    throw new Error(response.statusText)
  }
}

function json(response) {
  return response.text().then(resText => {
    try {
      return JSON.parse(resText)
    } catch (err) {
      throw new Error(resText)
    }
  })
}

export function requestGet(path, callback) {
  if (!callback) callback = () => {}

  return fetch(API_ROOT + path)
    .then(handleErrors)
    .then(json)
    .then(callback)
}

export function requestPost(path, data, callback) {
  if (!callback) callback = () => {}

  return fetch(API_ROOT + path, data, {
    method: 'post',
    mode: 'no-cors',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(handleErrors)
    .then(json)
    .then(callback)
}

export function requestToken(code, callback) {
  return fetch(API_ROOT + '/discord_oauth', {
    method: 'post',
    mode: 'no-cors',
    body: encodeURIComponent(code),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
    .then(handleErrors)
    .then(callback)
}

export const API_ROOT = 'https://pkapi.astrid.fun'
