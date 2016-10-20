import m from 'mithril';
import Dirs from './dirs'

export default {
  controller: () => {
    let index = m.route.param("index");
    let current = m.route.param("path") || "";

    return {
      index: index,
      dirs: m.request({
        method: "GET",
        url: `api/dirs/${index}/${current}`
      })
    }
  },
  view: (ctrl) => {
    return [
      m.component(Dirs, { dirs: ctrl.dirs(), index: ctrl.index })
    ];
  }
};
