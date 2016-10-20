import m from 'mithril';

export default {
  controller: () => {
    return {
      index: m.request({
        method: "GET",
        url: 'api/index'
      })
    }
  },
  view: (ctrl) => {
    return m('.container-fluid',
      m('.row.indexes',
        ctrl.index().map(function(index) {
          return m('a', { href: `/${index.index}/`, config: m.route }, m('.col-xs-12.index', [
            m('img', { src: 'images/folder.png' }),
            index.name
          ]));
        })
      )
    );
  }
};
