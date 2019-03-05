import React from 'react'
import { BrowserRouter as Router, Route } from 'react-router-dom'
import './App.css'

import SystemPage from './Components/System'

class App extends React.PureComponent {
  render () {
    return (
      <main className='app'>
        <Router>
          <Route path='/system/:id' component={SystemPage} />
        </Router>
      </main>
    )
  }
}

export default App;
