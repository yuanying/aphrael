import m from 'mithril';
import 'bootstrap';
import Home from './home';
import NavBar from './navbar';
import '../css/bootstrap.min.css';
import '../css/main.css';

const home = m.component(Home);

m.mount(document.getElementById('navbar'),
                                m.component(NavBar, {
                                    title: 'Mithril Study'
                                }));

m.route(document.getElementById('root'), '/', {
    '/': home
});
