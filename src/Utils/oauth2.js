import { CLIENT_ID, CLIENT_SECRET, REDIRECT_URL } from './oauth2_settings'


export { REDIRECT_URL } from './oauth2_settings'

export const LOGIN_URL = `https://discordapp.com/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URL}&response_type=code&scope=identify`

export const ENC_CREDS = btoa(`${CLIENT_ID}:${CLIENT_SECRET}`)
