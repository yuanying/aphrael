
let favs = {};
let save = () => {
  localStorage.setItem("favs", JSON.stringify(favs));
};

export default {
  like: (index, path) => {
    favs[`${index}#${path}`] = [index, path];
    save();
  },
  unlike: (index, path) => {
    delete favs[`${index}#${path}`]
    save();
  },
  loadAll: () => {
    favs = localStorage.getItem("favs");
    if (favs) {
      favs = JSON.parse(favs);
    } else {
      favs = {};
    }
  },
  fav: (index, path) => {
    return favs[`${index}#${path}`];
  },
  favs: () => {
    let favList = [];
    Object.keys(favs).forEach(function (key) {
      favList.push(favs[key])
    });
    return favList;
  }
};
