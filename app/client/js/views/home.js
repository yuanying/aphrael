import m from 'mithril';

export default {
  controller: (args) => {
  },
  view: (ctrl, args) => {
    return m('.container-fluid',
      m('.row.indexes',
        args.targets().map(function(index) {
          return m('a', { href: `/${index.index}/`, config: m.route }, m('.col-xs-12.index', [
            m('img', { src: 'images/folder.png' }),
            index.name
          ]));
        })
      )
    );
  }
};
