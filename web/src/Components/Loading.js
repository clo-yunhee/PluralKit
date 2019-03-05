import React from 'react';

import './Loading.css'

class Loading extends React.PureComponent {
  render () {
    return (
      <div className='lds-pure'>
        <div></div>
        <div></div>
        <div></div>
      </div>
    )
  }
}

export default Loading;
