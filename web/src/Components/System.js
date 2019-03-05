import React from 'react'
import { requestGet, API_ROOT } from '../Utils/fetch'
import MemberCard from './MemberCard'
import Loading from './Loading'

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
      id,
      name,
      description,
      tag,
      avatar_url,
      members
    } = this.state.system

    return (
      <section key={id} className="system">
        <header>
          {avatar_url ? <img src={avatar_url} alt={`The system avatar`} /> : false}
          {name}
        </header>
        <p>
          {description}
        </p>
        <p>
          <strong>Tag is:</strong> <span>{tag}</span>
        </p>
        <div className="system-members">
          {members.map(m => <MemberCard member={m} key={m.id} />)}
        </div>
      </section>
    )
  }
}
