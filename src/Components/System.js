import React from 'react'
import MagicGrid from 'magic-grid-react'
import { requestGet } from '../Utils/fetch'
import Twemoji from '../Utils/Twemoji'
import MemberCard from './MemberCard'
import Loading from './Loading'
import Avatar from './Avatar'

import './System.css'

class System extends React.PureComponent {
  constructor (props) {
    super(props)

    this.state = {
      id: props.match.params.id,
      system: null,
      members: null
    }
  }

  componentDidMount () {
    requestGet(`/s/${this.state.id}`, data => {
      this.setState({
        system: data
      })
    })

    requestGet(`/s/${this.state.id}/members`, data => {
      this.setState({
        members: data
      })
    })
  }

  render () {
    let {
      system,
      members
    } = this.state

    if (!system) {
      return <Loading />
    }

    if (!members) {
      members = []
    }

    const {
      //id,
      name,
      description,
      tag,
      avatar_url
    } = system

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
          <MagicGrid gutter='.5vmin' animate={true} useMin={true}>
            {sortedMemberList}
          </MagicGrid>
        </div>
      </section>
    )
  }
}

export default System
