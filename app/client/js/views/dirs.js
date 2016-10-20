import m from 'mithril';

export default {
  controller: (args) => {
    return {
      dirUrl: (dir) => {
        return `/${args.index}/${dir.path}`;
      }
    }
  },
  view: (ctrl, args) => {
    return m('.container-fluid.dirs', [
      m('.row' , args.dirs.map((dir) => {
        return m('a', { href: ctrl.dirUrl(dir), config: m.route }, [
          m('.col-xs-6.col-sm-4.col-md-3.col-lg-2.dir', [
            m('div', m('img.img-responsive.img-thumbnail', { src: 'images/default.png' })),
            m('div.text-overflow', dir.name)
          ])
        ]);
      }))
    ]);
  }
};
