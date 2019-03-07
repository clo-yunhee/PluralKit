import React from 'react'
import { requestGet, API_ROOT } from '../Utils/fetch'
import Twemoji from '../Utils/Twemoji'
import MemberCard from './MemberCard'
import Loading from './Loading'
import Avatar from './Avatar'

import './System.css'

export default class System extends React.PureComponent {
  constructor (props) {
    super(props)

    this.state = {
      id: props.match.params.id,
      system: null
    }
  }

  componentDidMount () {
    requestGet(API_ROOT + '/systems/' + this.state.id, data => {
      this.setState({ system: data })
    })
  }

  render () {
    if (!this.state.system) {
      return <Loading />
    }

    const {
      //id,
      name,
      description,
      tag,
      avatar_url,
      members
    } = this.state.system

    const sortedMemberList = members.sort((s1, s2) => {
      const s1name = s1.name.toLocaleUpperCase()
      const s2name = s2.name.toLocaleUpperCase()

      return s1name.localeCompare(s2name)
    }).map(
      m => <MemberCard member={m} key={m.id} />
    )

    return (
      <section className='system'>
        <header className='system-header'>
          <h1 className='system-name'>
            <Avatar url={avatar_url} alt='The system avatar' />
            {name ? <Twemoji>{name}</Twemoji> : <em>Unnamed</em>}
          </h1>
        </header>

        <div className='system-description'>
          <p className='system-tag'>
            <Twemoji>{tag}</Twemoji>
          </p>

          <p>
            {description}
          </p>
        </div>

        <div className='system-members'>
          {sortedMemberList}
        </div>
      </section>
    )
  }
}
