import { render, h } from 'preact';
import Router from 'preact-router';
import SystemPage from './SystemPage';

render((
    <Router>
        <SystemPage path="/system/:id" />
    </Router>
), document.body);