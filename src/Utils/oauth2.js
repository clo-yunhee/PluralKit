
export const CLIENT_ID = process.env.REACT_APP_CLIENT_ID

export const CLIENT_SECRET = process.env.REACT_APP_CLIENT_SECRET

export const REDIRECT_URL = encodeURIComponent(process.env.REACT_APP_REDIRECT_URL)

export const LOGIN_URL = `https://discordapp.com/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URL}&response_type=code&scope=identify`

export const ENC_CREDS = btoa(`${CLIENT_ID}:${CLIENT_SECRET}`)

