// Extend the behavior of L.MarkerClusterGroup from
// https://github.com/Leaflet/Leaflet.markercluster
// so that we can change the style of the cluster or the markers.

// Author: Sri Vishnu Totakura <t.srivishnu@gmail.com>

L.PgisMarkerClusterGroup = L.MarkerClusterGroup.extend({

  options: {
    // Add these css classes to the Cluster marker icon when
    //  clustered. These classes won't appear when Markers are shown.
    defaultIconCssClasses: ['default'],
    highlightIconCssClasses: ['highlighted'],
    // The below option is modified by other functions. Don't pass this
    //  option while initializing. It is changed dynamically depending on
    //  +defaultIconCssClasses+ and +highlightIconCssClasses+.
    clusterIconCssClasses: undefined
    // TODO: May be +clusterIconCssClasses+ could be made a property on
    //  the PgisMarkerClusterGroup rather than being in the +options+
  },

  addedLayers: [],

  // Override the default icon creation function.
  // Only change intended was to add className to DivIcon dynamically
  // based on the +clusterIconCssClasses+ options.
  _defaultIconCreateFunction: function(cluster) {
     var childCount = cluster.getChildCount();

     var c = ' marker-cluster-';

     if (childCount < 10) {
       c += 'small';
     } else if (childCount < 100) {
       c += 'medium';
     } else {
       c += 'large';
     }

     if(!this.clusterIconCssClasses){
       this.clusterIconCssClasses = this.defaultIconCssClasses;
     }
     var additionalClasses = this.clusterIconCssClasses.join(" ")

     return new L.DivIcon({
       html: '<div><span>' + childCount + '</span></div>',
       className: additionalClasses + ' marker-cluster' + c,
       iconSize: new L.Point(40, 40)
     });
   },

   additionalClusterCssClasss: function(){
     return this.clusterIconCssClasses.join(" ")
   },

   addHighlightStyle: function(){
      this.options.clusterIconCssClasses = this.options.highlightIconCssClasses;
      this.refreshClusters();
      var _this = this;

      // This assumes all the child layers in this clusterGroup are
      // markers - L.Marker
      this.eachLayer(function(layer){
        layer.setIcon(_this.getMarkerHighlightIcon());
      })
   },

   removeHighlightStyle: function() {
     this.options.clusterIconCssClasses = this.options.defaultIconCssClasses;
     this.refreshClusters();
     var _this = this;

     // This assumes all the child layers in this clusterGroup are
     // markers - L.Marker
     this.eachLayer(function(layer) {
       layer.setIcon(_this.getMarkerDefaultIcon());
     })
   },

   getMarkerDefaultIcon: function() {
     return new L.Icon({
       iconUrl: '/static/images/marker-icon-red.png'
     });
   },

   getMarkerHighlightIcon: function() {
     return new L.Icon({
       iconUrl: '/static/images/marker-icon.png'
     });
   }
});

L.pgisMarkerClusterGroup = function(options) {
  return new L.PgisMarkerClusterGroup(options);
};


