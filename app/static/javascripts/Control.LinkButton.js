L.Control.LinkButton = L.Control.extend({
  options: {
    // topright, topleft, bottomleft, bottomright
    position: 'topright'
  },
  initialize: function (options) {
    // constructor
    L.Util.setOptions(this, options);
  },
  onAdd: function (map) {
    // happens after added to map
    var container = L.DomUtil.create('div', 'link-button-container');
    this.link = L.DomUtil.create('a', 'link', container);
    this.link.href = this.options.href || "";
    this.link.innerHTML = this.options.text || "No Text???";
    return container;
  },
  onRemove: function (map) {
    // when removed
  }
});

L.control.link_button = function(options) {
  return new L.Control.LinkButton(options);
};
