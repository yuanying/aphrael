import m from 'mithril';
import Dirs from './dirs'
import Breadcrumbs from './breadcrumbs'

export default {
  controller: () => {
    let index = m.route.param("index");
    let current = m.route.param("path") || "";
    let paths = current.split('/');
    if (paths[0] === "") {
      paths = [];
    }

    return {
      index: index,
      paths: paths,
      dirs: m.request({
        method: "GET",
        url: `api/dirs/${index}/${current}`
      })
    }
  },
  view: (ctrl) => {
    return [
      m.component(Breadcrumbs, { index: ctrl.index, paths: ctrl.paths}),
      m.component(Dirs, { dirs: ctrl.dirs(), index: ctrl.index })
    ];
  }
};
