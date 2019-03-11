import React from 'react'
import Avatar from './Avatar'
import { AVATAR_URL } from './Home'

import './NotFound.css'


class NotFound extends React.PureComponent {
  componentDidMount () {
    setTimeout(() => this.props.history.push('/'), 3000)
  }

  render () {
    return (
      <div className='not-found-container'>
        <p className='not-found-code'>
          404
        </p>
        <div className='not-found-message-box'>
          <Avatar url={AVATAR_URL} />
          <span>
            <span id='oops1' className='not-found-oops'>
              Oops... Page not found~
            </span>
            <span id='oops2' className='not-found-oops'>
              Redirecting you back home~
            </span>
          </span>
        </div>
      </div>
    )
  }
}

export default NotFound
