import { requestWithoutData as req } from './ajax'

export const fetchSystem = req('system', 'get', '/s/{system}')

export const fetchMembers = req('system members', 'get', '/s/{system}/members')

export const fetchSwitches = req('system switches', 'get', '/s/{system}/switches')

export const fetchMember = req('system member', 'get', '/s/{member}')


