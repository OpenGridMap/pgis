var MapHelpers = {
  getPointSidebarContent: function(pointdata){
    var source   = $("#marker-sidebar-template").html();
    var markerSidebarTemplate = Handlebars.compile(source);

    return markerSidebarTemplate(pointdata);
  },
  getRelationSidebarContent: function(relationProperties){
    var source   = $("#relation-sidebar-template").html();
    var relationSidebarTemplate = Handlebars.compile(source);

    return relationSidebarTemplate(relationProperties);
  },
  setSidebarContentToLastClickedRelation: function(pgisMap, selectedRelationOsmIds) {
    pgisMap.sidebar.setContent(
      this.getRelationSidebarContent({
        relation: pgisMap.overlayLayers.relations.lastClickedRelationFeatureLayer.relation.properties,
        selectedRelationsOsmIds: selectedRelationsOsmIds
      })
    );
  },
  // Binds a the popup to a powerline
  bindPowerlinePopup: function(polyline, powerline){
    var source   = $("#polyline-popup-template").html();
    var polylinePopupTemplate = Handlebars.compile(source);

    var popup = L.popup().setContent(
      polylinePopupTemplate(powerline)
    );

    polyline.bindPopup(popup);
  },

  getOsmTile: function (){
    return L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: 'Map data &copy; '
        + '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, '
        + '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
        + 'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom: 18,
      minZoom: 8
    });
  },

  getSatelliteTile: function(){
    return  L.tileLayer(
      'http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/'
        + 'MapServer/tile/{z}/{y}/{x}',
        {
          attribution: 'Map data &copy; '
            + '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, '
            + '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
            + 'Imagery © <a href="http://mapbox.com">Mapbox</a>',
          maxZoom: 18,
          minZoom: 8
        }
    );
  }
};
