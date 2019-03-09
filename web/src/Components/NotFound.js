import React from 'react'
import Avatar from './Avatar'
import { AVATAR_URL } from './Home'

import './NotFound.css'


const styleHiding = {
  order: 1,
  opacity: 0
}

const styleHidden = {
  order: 2,
  opacity: 0
}

const styleVisible = {
  order: 1,
  opacity: 1
}


function delayState(ms, state) {
  return time => new Promise(resolve => {
    setTimeout(state => {
      this.setState(state)
      resolve(time)
    }, time + ms, state)
  })
}


class NotFound extends React.PureComponent {
  constructor (props) {
    super(props);

    this.delayState = delayState.bind(this)
    this.state = {
      style1: styleHidden,
      style2: styleHidden
    }
  }

  componentDidMount () {
    Promise.resolve(0)
      .then(this.delayState(200, { style1: styleVisible }))
      .then(this.delayState(2000, { style1: styleHiding }))
      .then(this.delayState(700, { style1: styleHidden, style2: styleVisible }))
      .then(this.delayState(2000, { style2: styleHiding }))
      .then(this.delayState(1200, { style2: styleHidden }))
      .then(() => this.props.history.push('/'))
  }

  render () {
    return (
      <div className='not-found-container'>
        <p className='not-found-code'>
          404
        </p>
        <div className='not-found-message-box'>
          <Avatar url={AVATAR_URL} />
          <span className='not-found-oops' ref={this.ref1} style={this.state.style1}>
            Oops... Page not found~
          </span>
          <span className='not-found-oops' ref={this.ref2} style={this.state.style2}>
            Redirecting you back home~
          </span>

          {/*className='not-found-oops' data-text={this.state.text}/>*/}
        </div>
      </div>
    )
  }
}

export default NotFound

