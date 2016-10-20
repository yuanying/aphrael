import m from 'mithril';

export default {
  controller: (args) => {
    return {
      imageUrl: (image) => {
        return `images/${args.index}/${image.path}`;
      },
      thumbUrl: (image) => {
        return `thumbs/${args.index}/${image.path}`;
      }
    }
  },
  view: (ctrl, args) => {
    return m('.container-fluid.images', [
      m('.row' , args.images.map((image) => {
        return m('a', { href: ctrl.imageUrl(image) }, [
          m('.col-xs-3.col-sm-2.col-md-1.col-lg-1.image', [
            m('img', { src: ctrl.thumbUrl(image) }),
          ])
        ]);
      }))
    ]);
  }
};
