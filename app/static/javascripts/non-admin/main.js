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

  // var newPointLink = L.control.link_button(newPointLinkProperties).addTo(map);
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

  pgisMap.dataLoader = function() {
    MapDataLoader.loadDataForMapFragment(
      this,
      this.markerLayers.markers,
      this.markerLayers.clusterGroup,
      this.markerLayers.powerlinesLayerGroup
    );
  }

  pgisMap.dataLoader();

  pgisMap.addOverlayLayer({
    name: "Relations",
    ref: 'relations',
    layer: new L.LayerGroup()
  });

  var _pgisMap = pgisMap;
  pgisMap.map.addEventListener("overlayadd", function(target, layerName){
    // TODO: Do this only if it is a Relations layr
    // if (target.name == 'Relations') {
      points = [{
        "id": 234934,
        "latlng": [50.1443037, 12.0362751],
        "pictures": [],
        "tags": {
          "construction": "generator",
          "generator:method": "wind_turbine",
          "generator:source": "wind",
          "power": "construction"
        }
      }, {
        "id": 234935,
        "latlng": [50.1470837, 12.0408184],
        "pictures": [],
        "tags": {
          "construction": "generator",
          "generator:method": "wind_turbine",
          "generator:source": "wind",
          "power": "construction"
        }
      }, {
        "id": 234936,
        "latlng": [50.1475178, 12.0361834],
        "pictures": [],
        "tags": {
          "construction": "generator",
          "generator:method": "wind_turbine",
          "generator:source": "wind",
          "power": "construction"
        }
      }, {
        "id": 234937,
        "latlng": [50.150042, 12.0416572],
        "pictures": [],
        "tags": {
          "construction": "generator",
          "generator:method": "wind_turbine",
          "generator:source": "wind",
          "power": "construction"
        }
      }, {
        "id": 234938,
        "latlng": [50.1529804, 12.0410105],
        "pictures": [],
        "tags": {
          "construction": "generator",
          "generator:method": "wind_turbine",
          "generator:source": "wind",
          "power": "construction"
        }
      }
      ]
    lines = [{
      "id": 1956,
      "latlngs": [[50.1076684, 12.1660907], [50.1088502, 12.165964], [50.1102951, 12.1657883], [50.111762, 12.1656264], [50.1132, 12.1654716], [50.1141919, 12.165696], [50.1151685, 12.1661927], [50.1172989, 12.1670659], [50.11858, 12.1666948], [50.1195184, 12.1648587], [50.1204281, 12.1630588], [50.1209982, 12.1619071]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 1957,
      "latlngs": [[50.122844, 12.1613774], [50.1244613, 12.1624665], [50.1261384, 12.1636028], [50.1275776, 12.1646241], [50.129076, 12.1656455]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 2801,
      "latlngs": [[50.1140258, 12.0898605], [50.1155463, 12.0903052], [50.1170258, 12.090733], [50.1183606, 12.0911475], [50.1194996, 12.0901634], [50.1203792, 12.0894456], [50.121148, 12.0887768], [50.1228565, 12.087354], [50.1242057, 12.0861995], [50.1254768, 12.0851329], [50.1265827, 12.0842031], [50.1274662, 12.0834406], [50.1289643, 12.0821539], [50.1300188, 12.0812303]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 2860,
      "latlngs": [[50.1262728, 12.1303876], [50.1265343, 12.1294425]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 6754,
      "latlngs": [[50.1698884, 12.0548468], [50.1694294, 12.0535366], [50.1690295, 12.05269], [50.1685583, 12.051673], [50.1678827, 12.0501216], [50.1672722, 12.0489178], [50.1667117, 12.0476573], [50.1661194, 12.0463968], [50.1649726, 12.0450227], [50.1633601, 12.0429068]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 6755,
      "latlngs": [[50.1633601, 12.0429068], [50.1629086, 12.0437642]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 6756,
      "latlngs": [[50.1634194, 12.0486091], [50.1644785, 12.0477014], [50.165342, 12.0470747], [50.1661194, 12.0463968], [50.1671341, 12.0455281], [50.1691405, 12.0436484], [50.1700747, 12.0427528]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 6757,
      "latlngs": [[50.1633601, 12.0429068], [50.1633986, 12.0414669], [50.1634597, 12.040002], [50.1635281, 12.0377643], [50.1628615, 12.0361183], [50.16206, 12.0341388], [50.1612889, 12.0322397], [50.1604374, 12.0301538]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 6758,
      "latlngs": [[50.1694294, 12.0535366], [50.1686932, 12.0545772], [50.167657, 12.0559986], [50.1664663, 12.0576801], [50.165421, 12.0591227], [50.1643731, 12.0605962], [50.1636045, 12.0616306], [50.1627966, 12.0627861]],
      "tags": {
        "power": "minor_line"
      }
    }, {
      "id": 7094,
      "latlngs": [[50.1239955, 12.0652399], [50.1237735, 12.0670566], [50.1233307, 12.0691694], [50.1238558, 12.072129], [50.1245907, 12.07434], [50.1252899, 12.0764845]],
      "tags": {
        "power": "minor_line"
      }
    }
    ]

    var defaultStyle = {
      color: "red"
    }
    var highlightedStyle = {
      color: "blue"
    }

    var relationFeatureLayer = L.featureGroup();

    _.each(lines, function(line){
      var polyline = L.polyline(line.latlngs);
      polyline.setStyle(defaultStyle);

      relationFeatureLayer.addLayer(polyline);
    });

    var markers = [];
    _.each(points, function(point){
      var marker = new L.Marker(point.latlng)
      // marker.setStyle(defaultStyle)
      markers.push(marker);
    });
    relationFeatureLayer.addLayers(markers);


    relationFeatureLayer.on("mouseover", function(e){
      e.target.setStyle(highlightedStyle);
    });

    relationFeatureLayer.on("mouseout", function(e){
      e.target.setStyle(defaultStyle);
    });

    pgisMap.overlayLayers.relations.layer.addLayer(relationFeatureLayer);
  });
});
