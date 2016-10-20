import m from 'mithril';
import Dirs from './dirs'

export default {
  controller: () => {
    let current = m.route.param("path");
    if (current != "") {
      current = `/${current}`;
    }
    let jsonPath = `.${current}/index.js`;
    console.log(current);
    console.log(jsonPath);
    return {
      index: m.request({
        dataType: "jsonp",
        callbackName: "loadPage",
        url: jsonPath
      })
    }
  },
  view: (ctrl) => {
    return m('.container-fluid', [
      m.component(Dirs, { path: ctrl.index().path, dirs: ctrl.index().dirs })
    ]);
  }
};
