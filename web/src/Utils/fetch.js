function handleErrors(response) {
  if (response.ok && response.status >= 200 && response.status < 300) {
    return response;
  } else {
    throw new Error(response.statusText);
  }
}

function json(response) {
  return response.text().then(resText => {
    try {
      return JSON.parse(resText);
    } catch (err) {
      throw new Error(resText);
    }
  });
}

export function requestGet(url, callback) {
  if (!callback) callback = () => {};

  return fetch(url, { method: 'get' })
    .then(handleErrors)
    .then(json)
    .then(callback);
}

export const API_ROOT = 'https://pkapi.astrid.fun';
