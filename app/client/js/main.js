import m from 'mithril';
import $ from 'jquery'
import 'bootstrap';
import Home from './views/home';
import NavBar from './views/navbar';
import '../css/bootstrap.min.css';
import '../css/main.css';

m.route.mode = "hash";

const home = m.component(Home);

m.mount(document.getElementById('navbar'),
                                m.component(NavBar, {
                                    title: 'Mithril Study'
                                }));

m.route(document.getElementById('root'), '/', {
    '/:path...': home
});
