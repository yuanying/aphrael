import m from 'mithril';

export default {
  controller: (args) => {
    let current = [].concat(args.path);
    return {
      dirUrl: (dir) => {
        let url = [""].concat(current, [dir]);
        return url.join('/');
      }
    }
  },
  view: (ctrl, args) => {
    return m('.container-fluid', [
      m('.row' , args.dirs.map((dir) => {
        return m('a', { href: ctrl.dirUrl(dir), config: m.route }, dir);
      }))
    ]);
  }
};
