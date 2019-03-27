export const API_ROOT = 'https://pkapi.astrid.fun'

export function handleErrors(response) {
  if (response.ok && response.status >= 200 && response.status < 300) {
    return response
  } else {
    throw new Error(response.statusText)
  }
}

export function json(response) {
  return response.text().then(resText => {
    try {
      return JSON.parse(resText)
    } catch (err) {
      throw new Error(resText)
    }
  })
}

export function requestJson(method, path, data, callback) {
  if (!callback) callback = () => {}

  return fetch(API_ROOT + path, {
    method: method,
    body: data,
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(handleErrors)
    .then(json)
    .then(callback)
}

export function requestToken(code, callback) {
  return fetch(API_ROOT + '/discord_oauth', {
    method: 'post',
    body: encodeURIComponent(code),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
    .then(handleErrors)
    .then(callback)
}

const wrapReject = name => reject => err => {
  console.warn(`${name} failed: `, err)
  if (reject) {
    reject(err.toString())
  }
}

export function requestWithData(name, method, path) {
  const wrapRejectName = wrapReject(name)

  return function(data, resolve, reject) {
    const wrappedReject = wrapRejectName(reject)

    return requestJson(method, path, JSON.stringify(data), resolve).catch(wrappedReject)
  }
}

export function requestWithoutData(name, method, path) {
  const wrapRejectName = wrapReject(name)

  return function(args, resolve, reject) {
    const wrappedReject = wrapRejectName(reject)

    // resolve the path with arguments
    const pathWithArgs = path.replace(/{(\w+)}/g, (match, key) => args[key] || key)

    return requestJson(method, pathWithArgs, undefined, resolve).catch(wrappedReject)
  }
}
