import m from 'mithril';
import $ from 'jquery'
import 'bootstrap';
import Home from './views/home';
import Index from './views/index';
import NavBar from './views/navbar';
import '../css/bootstrap.min.css';
import '../css/main.css';

// import 'photoswipe/dist/photoswipe.css';
// import 'photoswipe/dist/default-skin/default-skin.css';
// import PhotoSwipe from 'photoswipe';
// import PhotoSwipeUI_Default from 'photoswipe/dist/photoswipe-ui-default';

m.route.mode = "hash";

const home = m.component(Home);
const index = m.component(Index)

m.mount(document.getElementById('navbar'),
                                m.component(NavBar, {
                                    title: 'Aphrael'
                                }));

m.route(document.getElementById('root'), '/', {
    '/': home,
    '/:index': index,
    '/:index/:path...': index
});
