import m from 'mithril';
import jQuery from 'jquery';

export default {
  controller: (args) => {
    return {
      thumbUrl: (dir) => {
        return `api/thumbs/${args.index}/${dir.path}`;
      },
      dirUrl: (dir) => {
        return `/#/${args.index}/${dir.path}`;
      }
    }
  },
  view: (ctrl, args) => {
    return m('.container-fluid.dirs', [
      m('.row' , args.dirs.map((dir) => {
        let attr = {
          src: 'images/default.png',
          config: function(element, isInitialized, context) {
            if (!isInitialized) {
              var thumbnail = new Image();
              thumbnail.src = ctrl.thumbUrl(dir);
              jQuery(thumbnail).bind('load', function() {
                element.src = thumbnail.src;
              });
            }
          }
        }
        //return m('a', { href: ctrl.dirUrl(dir), config: m.route }, [
        return m('a', { href: ctrl.dirUrl(dir) }, [
          m('.col-xs-6.col-sm-4.col-md-3.col-lg-2.dir', [
            m('div', m('img.img-responsive.img-thumbnail', attr)),
            m('div.text-overflow', decodeURI(dir.name))
          ])
        ]);
      }))
    ]);
  }
};
