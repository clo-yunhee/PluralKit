import React from 'react'
import Avatar from './Avatar'

import './MemberCard.css'

class MemberCard extends React.PureComponent {
  render () {
    const {
      id,
      name,
      description,
      avatar_url,
      pronouns,
      birthday,
      color
    } = this.props.member

    return (
      <article className="membercard">
        <header className="membercard-header">
          <Avatar url={avatar_url} alt={`${name}'s avatar`} />
          {name}
        </header>

        <p>
          {description}
        </p>
      </article>
    )
  }
}

export default MemberCard;
