var MiscHelpers = {
  //Adapted from https://github.com/Leaflet/Leaflet.markercluster/issues/217#issuecomment-20963103
  // creates an icon for the cluster based on the size.
  createClusterIcon: function(cluster) {

    var count = cluster.count;

    // cluster icon
    var c = 'marker-cluster-';
    if (count < 10) {
      c += 'small';
    } else if (count < 100) {
      c += 'medium';
    } else {
      c += 'large';
    }

    return new L.DivIcon({
      html: '<div><span>' + count + '</span></div>',
      className: 'marker-cluster ' + c,
      iconSize: new L.Point(40, 40)
    });
  },

  getQueryString: function(field, url) {
    var href = url ? url : window.location.href;
    var reg = new RegExp( '[?&]' + field + '=([^&#]*)', 'i' );
    var string = reg.exec(href);
    return string ? string[1] : null;
  }
}
