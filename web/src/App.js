import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import './App.css'

import HomePage from './Components/Home'
import SystemPage from './Components/System'
import NotFoundPage from './Components/NotFound'
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
            <Route path='/system/:id' exact component={SystemPage} />
            <Route path='/' exact component={HomePage} />

            {/* Page not found */}
            <Route component={NotFoundPage} />
          </Switch>
        </main>
      </Router>
    )
  }
}

export default App;
