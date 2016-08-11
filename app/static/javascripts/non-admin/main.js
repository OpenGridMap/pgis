$(document).ready(function(){
  registerHandleBarHelpers();

  var osmTile = MapHelpers.getOsmTile();
  var satelliteTile = MapHelpers.getSatelliteTile();

  var pgisMap = new PgisMap();
  pgisMap.createMap(osmTile);

  var map = pgisMap.map;

  var baseMaps = {
    "Satellite View": satelliteTile,
    "Topological View": osmTile
  };

  pgisMap.addBaseMaps(baseMaps);

  var newPointLinkProperties = {
    ref: 'newPoint',
    text: 'New Point',  // string
    onclick: function() {
      window.location.href = '/admin/points/new?redirect_back=true'
        + '&lat=' + pgisMap.map.getBounds().getCenter().lat
        + '&long=' + pgisMap.map.getBounds().getCenter().lng
        + '&zoom=' + pgisMap.map.getZoom();
    }
  };
  pgisMap.addLinkButton(newPointLinkProperties);

  var rankingTableLinkProperties = {
    ref: 'ranking',
    text: 'Top 10 Ranking',
    onclick: function() {
      window.location.href = '/ranking';
    }
  };
  pgisMap.addLinkButton(rankingTableLinkProperties);

  var userProfileLinkProperties = {
    ref: 'userprofile',
    text: 'Your Profile',
    onclick: function() {
      window.location.href = '/userprofile';
    }
  };
  pgisMap.addLinkButton(userProfileLinkProperties);

  pgisMap.addMarkerLayer({
    name: 'markers',
    layer: new L.MarkerClusterGroup()
  });
  pgisMap.addMarkerLayer({
    name: 'clusterGroup',
    layer: new L.LayerGroup()
  });
  pgisMap.addMarkerLayer({
    name: 'powerlinesLayerGroup',
    layer: new L.LayerGroup()
  });

  var _pgisMap = pgisMap;

  pgisMap.baseMapDataLoader = function() {
    if (_.contains(_pgisMap.selectedOverlayLayers, "Relations")) {
      MapDataLoader.fetchAndPlotRelations(_pgisMap);
    } else {
      MapDataLoader.loadBaseMapDataForMapFragment(
        this,
        this.markerLayers.markers,
        this.markerLayers.clusterGroup,
        this.markerLayers.powerlinesLayerGroup
      );
    }
  }

  pgisMap.baseMapDataLoader();

  pgisMap.addOverlayLayer({
    name: "Relations",
    ref: 'relations',
    layer: new L.LayerGroup()
  });
  pgisMap.addLinkButton({
    ref: 'exportRelations',
    text: 'Export Relations in Bound',
    onclick: function() {
      window.open(
        '/relations/export?bounds=' + pgisMap.map.getBounds().toBBoxString()
          + '&zoom=' + _pgisMap.map.getZoom(),
        '_blank'
      )
    }
  });
  pgisMap.hideLinkButton(pgisMap.linkButtons.exportRelations);

  window.pgisMap = pgisMap;

  pgisMap.onOverlayAdd  = function(layer) {
    if(layer.name == 'Relations') {
      _pgisMap.showLinkButton(_pgisMap.linkButtons.exportRelations);
    }
    _.each(_pgisMap.markerLayers, function(layer){
      layer.clearLayers();
    });

    this.baseMapDataLoader();
  };

  pgisMap.onOverlayRemove  = function(layer) {
    if(layer.name == 'Relations') {
      _pgisMap.hideLinkButton(_pgisMap.linkButtons.exportRelations);
    }
    _.each(_pgisMap.markerLayers, function(layer){
      layer.clearLayers();
    });

    this.baseMapDataLoader();
  };

  Handlebars.registerHelper('relationSelectionButton', function() {
    htmlClasses = [];
    if(this.selectedRelationsOsmIds.indexOf(this.relation.osmid.toString()) > -1) {
      htmlClasses.push("remove-relation-from-selection");
      htmlText = "Remove relation from export";
    } else {
      htmlClasses.push("add-relation-to-selection");
      htmlText = "Select relation to export"
    }
    return new Handlebars.SafeString(
      "<button class='" + htmlClasses.join(" ") + "'"
        + "data-relation-osm-id='" + this.relation.osmid + "'>"
          + htmlText
       + "</button>"
    );
  });

  function getSelectedRelations() {
    return (JSON.parse(localStorage.getItem('selectedRelations')) || []);
  }

  function saveSelectedRelations(selectedRelations) {
    localStorage.setItem('selectedRelations', JSON.stringify(selectedRelations));
  }

  $(document).on('click', '.add-relation-to-selection', function() {
    relationOsmId = $(this).attr('data-relation-osm-id');
    // TODO: Check if the relation is already in the array!
    selectedRelationsOsmIds = getSelectedRelations();
    selectedRelationsOsmIds.push(relationOsmId)
    saveSelectedRelations(selectedRelationsOsmIds);

    MapHelpers.setSidebarContentToLastClickedRelation(
      pgisMap,
      selectedRelationsOsmIds
    );
  });

  $(document).on('click', '.remove-relation-from-selection', function() {
    relationOsmId = $(this).attr('data-relation-osm-id');
    selectedRelationsOsmIds = getSelectedRelations();
    index = selectedRelationsOsmIds.indexOf(relationOsmId)
    if(index > -1) {
     selectedRelationsOsmIds.splice(index, 1);
    }
    saveSelectedRelations(selectedRelationsOsmIds)
    MapHelpers.setSidebarContentToLastClickedRelation(
      pgisMap,
      selectedRelationsOsmIds
    )
  })
});
