import m from 'mithril';

export default {
  controller: (args) => {
    return {
      linkTo: (path, title) => {
        let tag = 'a.active';
        let attr = { };
        let url = `/${args.index}/${path.join('/')}`;

        if (decodeURI(url) != decodeURI(m.route())) {
          tag = 'a';
          attr = {
            href: url,
            config: m.route
          }
        }
        return m('li', m(tag, attr, title));
      }
    }
  },
  view: (ctrl, args) => {
    let breadcrumbs = [
      ctrl.linkTo([], 'Home')
    ];
    for(let i=0; i<args.paths.length; i++) {
      let path = args.paths.slice(0, i+1);
      breadcrumbs.push(
        ctrl.linkTo(path, args.paths[i])
      );
    }
    return m('.container-fluid', m('ol.breadcrumb', breadcrumbs));
  }
};
