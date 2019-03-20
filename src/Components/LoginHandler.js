import React from 'react'
import { Redirect } from 'react-router-dom'
import queryString from 'query-string'
import Loading from './Loading'
import { requestToken } from '../Utils/fetch'

class LoginHandler extends React.PureComponent {
  constructor (props) {
    super(props)

    this.state = {
      done: false
    }
  }

  componentDidMount () {
    const params = queryString.parse(this.props.location.search)

    if (!params.code) throw new Error('NoCodeProvided');

    requestToken(params.code, token => {
      sessionStorage.setItem('token', token)
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

export default LoginHandler
