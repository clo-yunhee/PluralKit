import isEqual from 'lodash/isEqual'
import React from 'react'
import twemoji from 'twemoji'


class Twemoji extends React.Component {
  constructor (props) {
    super(props)

    this.rootRef = React.createRef()
  }

  _parseTwemoji () {
    const node = this.rootRef.current
    twemoji.parse(node, this.props.options)
  }

  componentDidUpdate (prevProps) {
    if (!isEqual(this.props, prevProps)) {
      this._parseTwemoji()
    }
  }

  componentDidMount () {
    this._parseTwemoji()
  }

  render () {
    const { children, ...other } = this.props

    delete other.options
    return <span ref={this.rootRef} {...other}>{children}</span>
  }
}


export default Twemoji
