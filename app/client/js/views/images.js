import m from 'mithril';
import PhotoSwipe from 'photoswipe';
import PhotoSwipeUI_Default from 'photoswipe/dist/photoswipe-ui-default';

export default {
  controller: (args) => {
    let imageUrl = (image) => {
      return `images/${args.index}/${image.path}`;
    };
    let thumbUrl = (image) => {
      return `thumbs/${args.index}/${image.path}`;
    };
    let images = args.images.map((image, index) => {
      image['src'] = imageUrl(image);
      return image;
    });
    let photoswipe = (e) => {
      let pswpElement = document.querySelectorAll('.pswp')[0];
      let options = {
        index: 0,
        shareButtons: [
          {id:'download', label:'Download image', url:'{{raw_image_url}}', download:true}
        ]
      };
      var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, images, options);
      gallery.init();
      e.preventDefault();
    };
    return {
      photoswipe: photoswipe,
      imageUrl: imageUrl,
      thumbUrl: thumbUrl
    }
  },
  view: (ctrl, args) => {
    return m('.container-fluid.images', [
      m('.row' , args.images.map((image) => {
        let attr = {
          href: ctrl.imageUrl(image),
          onclick: ctrl.photoswipe
        };
        return m('a', attr, [
          m('.col-xs-3.col-sm-2.col-md-1.col-lg-1.image', [
            m('img', { src: ctrl.thumbUrl(image) }),
          ])
        ]);
      }))
    ]);
  }
};
