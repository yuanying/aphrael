import m from 'mithril';

const NavBar = {
  controller: (args) => {

  },
  view: (ctrl, args) => {
    let favSpan = m("span", {
    }, m("a[aria-hidden='true'][title='new'].glyphicon.glyphicon-heart-empty", {
      href: '#'//,
      //onclick: m.withAttr('title', carib.vm.kindOfMovies)
    }));
    return m('.container', [
      m('.nav-header', [
        m('a.navbar-brand', { href: '#' }, args.title),
      ]),
      m('.menus', [
        m('ul.nav.navbar-nav.navbar-right', [
          m('li', favSpan)
        ])
      ])
    ]);
  }
}

export default NavBar;
