import m from 'mithril';
import Dirs from './dirs'
import Images from './images'
import Breadcrumbs from './breadcrumbs'

export default {
  controller: (args) => {
    let index = m.route.param("index");
    let current = m.route.param("path") || "";
    current = current.split('&')[0];
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
      }),
      images: m.request({
        method: "GET",
        url: `api/images/${index}/${current}`
      })
    }
  },
  view: (ctrl, args) => {
    return [
      m.component(Breadcrumbs, { index: ctrl.index, paths: ctrl.paths, targets: args.targets }),
      m.component(Dirs, { dirs: ctrl.dirs(), index: ctrl.index }),
      m.component(Images, { images: ctrl.images(), index: ctrl.index })
    ];
  }
};
