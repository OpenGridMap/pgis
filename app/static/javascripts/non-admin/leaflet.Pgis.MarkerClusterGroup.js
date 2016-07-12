// Extend the behavior of L.MarkerClusterGroup from
// https://github.com/Leaflet/Leaflet.markercluster
// so that we can change the style of the cluster or the markers.
//  or highlight em on mouseover based on the relationId in options.

// Author: Sri Vishnu Totakura <t.srivishnu@gmail.com>

L.PgisMarkerClusterGroup = L.MarkerClusterGroup.extend({

  options: {
    // TODO: Override initializer and raise exception if the options are not
    //  set during initialization.
    relationId: undefined,
    relationLayer: undefined,
    // Add these css classes to the Cluster marker icon when
    //  clustered. These classes won't appear when Markers are shown.
    defaultIconCssClasses: ['default'],
    highlightIconCssClasses: ['highlighted']
  },

  // Override the default icon creation function.
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

     return new L.DivIcon({
       html: '<div><span>' + childCount + '</span></div>',
       className: "relation-id-" + this.relationId + ' marker-cluster' + c,
       iconSize: new L.Point(40, 40)
     });
   },

   addHighlightStyle: function() {
     var _this = this;

     _.each(this.options.highlightIconCssClasses, function(cssClass) {
       $(_this._relationClassSelector()).addClass(cssClass)
     })

     // Change to hightlight icon on the markers in this cluster.
     // This assumes all the child layers in this clusterGroup are
     // markers - L.Marker
     this.eachLayer(function(layer){
       layer.setIcon(_this.getMarkerHighlightIcon());
     });
   },

   removeHighlightStyle: function() {
     var _this = this;

     _.each(this.options.highlightIconCssClasses, function(cssClass) {
      $(_this._relationClassSelector()).removeClass(cssClass)
     })

     // This assumes all the child layers in this clusterGroup are
     // markers - L.Marker
     this.eachLayer(function(layer) {
       layer.setIcon(_this.getMarkerDefaultIcon());
     });
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
   },

   _bindEvents: function() {
     var _this = this;

     this.on("clustermouseover", function(e) {
       _this.options.relationLayer.fire('mouseover', e)
     });

     this.on("clustermouseout", function(e) {
       _this.options.relationLayer.fire('mouseout', e)
     })

     L.MarkerClusterGroup.prototype._bindEvents.call(this);
   },

   _relationClass: function() {
     return "relation-id-" + this.options.relationId;
   },

   _relationClassSelector: function() {
     return "." + this._relationClass();
   }

});

L.pgisMarkerClusterGroup = function(options) {
  return new L.PgisMarkerClusterGroup(options);
};


