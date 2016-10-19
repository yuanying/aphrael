import m from 'mithril';

export default {
    controller: () => {
      return {
        index: m.request({
          dataType: "jsonp",
          callbackName: "loadPage",
          url: "./index.js"
        })
      }
    },
    view: (ctrl) => {
        return ('.container-fluid', [
            m('.row' , [
                m('.col-sm-10.col-sm-offset-1.col-md-10.col-md-offset-1', [
                    m('.page-header', [
                        m('h3', 'Bootswatch Yeti Sample')
                    ]),
                    m('.alert.alert-info[role="alert"]', [
                        m('span.glyphicon.glyphicon-exclamation-sign[aria-hidden="true"]'),
                        m('span.sr-only', 'Info:'),
                        ctrl.index().images
                    ])
                ]),
                m('.col-sm-10.col-sm-offset-1.col-md-10.col-md-offset-1', [
                    m('form',[
                        m('.form-group', [
                            m('label', { for: 'exampleInputEmail1' }, 'Email address'),
                            m('input', { type: 'email',
                                         class: 'form-control',
                                         id: 'exampleInputEmail1',
                                         placeholder: 'Email'})
                        ]),
                        m('.form-group', [
                            m('label', { for: 'exampleInputPassword1' }, 'Password'),
                            m('input', { type: 'password',
                                         class: 'form-control',
                                         id: 'exampleInputPassword1',
                                         placeholder: 'Password'})
                        ]),
                        m('button', { type: 'submit',
                                      class: 'btn btn-warning' },
                          'Submit')
                      ])
                ])
            ])
        ]);
    }
};
