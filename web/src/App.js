import React from 'react'
import { BrowserRouter as Router, Route } from 'react-router-dom'
import './App.css'

import HomePage from './Components/Home'
import SystemPage from './Components/System'

class App extends React.PureComponent {
  render () {
    return (
      <Router>
        <main className='app'>
          <Route path='/' component={HomePage} />
          <Route path='/system/:id' component={SystemPage} />
        </main>
      </Router>
    )
  }
}

export default App;
