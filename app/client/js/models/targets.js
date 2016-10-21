import m from 'mithril';

export default {
  index: () => {
    return m.request({
      method: "GET",
      url: 'api/index'
    });
  }
};
