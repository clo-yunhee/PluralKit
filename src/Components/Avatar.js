import React from 'react'

import './Avatar.css'

const NONE_URL = 'https://discordapp.com/assets/6debd47ed13483642cf09e832ed0bc1b.png'

class Avatar extends React.PureComponent {

  render () {
    const {
      url,
      alt
    } = this.props

    const actualUrl = url || NONE_URL

    return (
      <div
        className='avatar' alt={alt}
        style={{ backgroundImage: `url(${actualUrl})` }}
      />
    )
  }

}

export default Avatar;
