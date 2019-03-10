import React from 'react'
import Avatar from './Avatar'
import { AVATAR_URL } from './Home'

import './NotFound.css'


class NotFound extends React.PureComponent {
  constructor (props) {
    super(props);
  }
  componentDidMount () {
    Promise.resolve(0)
      .then(setTimeout(() => this.props.history.push('/'), 10000))
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
          <span id='oops1'className='not-found-oops'>
            Oops... Page not found~
          </span>
          <span id='oops2'className='not-found-oops'>
            Redirecting you back home~
          </span>
          </span>

          {/*className='not-found-oops' data-text={this.state.text}/>*/}
        </div>
      </div>
    )
  }
}

export default NotFound
