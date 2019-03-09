import React from 'react'
import { BrowserRouter, Redirect } from 'react-router-dom'
import queryString from 'query-string'
import Loading from './Loading'
import { REDIRECT_URL, ENC_CREDS } from '../Utils/oauth2'


class LoginCallback extends React.PureComponent {
  constructor (props) {
    super(props)

    this.state = {
      done: false
    }
  }

  componentDidMount () {
    const params = queryString.parse(this.props.location.search)

    if (!params.code) throw new Error('NoCodeProvided');

    const url = `https://discordapp.com/api/oauth2/token?grant_type=authorization_code&code=${params.code}&redirect_uri=${REDIRECT_URL}`

    fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Basic ${ENC_CREDS}`,
      },
    })
      .then(res => res.json())
      .then(res => {
        sessionStorage.setItem('token', res.access_token)
        this.setState({ done: true })
      })
  }

  render () {
    if (this.state.done) {
      return <Redirect to='/' />
    } else {
      return <Loading />
    }
  }
}

export default LoginCallback
