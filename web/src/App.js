import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import './App.css'

import HomePage from './Components/Home'
import SystemPage from './Components/System'
import LoginCallback from './Components/LoginCallback'

class App extends React.PureComponent {
  render () {
    return (
      <Router>
        <main className='app'>
          <Switch>
            {/* API routes */}
            <Route path='/api/login' exact component={LoginCallback} />

            {/* Page routes */}
            <Route path='/' component={HomePage} />
            <Route path='/system/:id' component={SystemPage} />
          </Switch>
        </main>
      </Router>
    )
  }
}

export default App;
