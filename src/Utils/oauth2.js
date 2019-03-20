
export const CLIENT_ID = process.env.REACT_APP_CLIENT_ID

export const REDIRECT_URL = encodeURIComponent(process.env.REACT_APP_REDIRECT_URL)

//export const LOGIN_URL = `https://discordapp.com/oauth2/authorize?client_id=${CLIENT_ID}&response_type=&scope=identify`

export const LOGIN_URL = `https://discordapp.com/oauth2/authorize?client_id=553610828197134346&response_type=code&scope=identify&redirect_uri=http://localhost:3000/login`


