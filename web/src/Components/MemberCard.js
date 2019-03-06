import React from 'react'
import Twemoji from '../Utils/Twemoji'
import Avatar from './Avatar'

import './MemberCard.css'

class MemberCard extends React.PureComponent {
  render () {
    const {
      //id,
      name,
      description,
      avatar_url,
      pronouns,
      birthday,
      color
    } = this.props.member

    return (
      <article className='membercard'>
        <header className='membercard-header'>
          <h2 className='membercard-name'>
            <Avatar url={avatar_url} alt={`${name}'s avatar`} />
            <Twemoji>{name}</Twemoji>
          </h2>
        </header>

        <p className='membercard-description'>
          {description}
        </p>
      </article>
    )
  }
}

export default MemberCard;
