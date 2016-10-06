var Statistics = {
    countPowerObjects: function(pgisMap) {
      var markers = pgisMap.markerMap;
      var powerlines = pgisMap.markerLayers.powerlinesLayerGroup.getLayers();
      var numPowerElements = [];
      numPowerElements['markers'] = Object.keys(markers).length;
      numPowerElements['clusteredMarkers'] = pgisMap.clusteredMarkers;
      numPowerElements['transformers'] = 0;
      numPowerElements['substations'] = 0;
      numPowerElements['powerPoles'] = 0;
      numPowerElements['powerTowers'] = 0;
      numPowerElements['powerPlants'] = 0;
      numPowerElements['windPower'] = 0 ;
      numPowerElements['solarPower'] = 0;
      numPowerElements['waterPower'] = 0;
      numPowerElements['otherGenerators'] = 0;
      numPowerElements['others'] = 0;
      var lengthOfPowerlines = [];
      lengthOfPowerlines['all'] = 0;
      lengthOfPowerlines['voltage'] = {};
      var numberOfPowerlines = 0;

      for (var marker in markers) {
        if (!markers.hasOwnProperty(marker)) {
          //The current property is not a direct property of p
          continue;
        }
        getPowerType(markers[marker]);
      }

      //for (var powerline in powerlines) {
      for(var i=0, len=powerlines.length; i < len; i++){
        if (!powerlines[i].hasOwnProperty(powerlines[i])) {
          //The current property is not a direct property of p
        }
        getPowerlineLength(powerlines[i]);
      }

      function getPowerType(marker) {
        var tags = marker.data.tags;
        if ('power_element_tags' in tags) {
          var power_element_tags = tags.power_element_tags;
          if (power_element_tags.indexOf('power=transformer') != -1) {
           numPowerElements['transformers']++;
          } else if (power_element_tags.indexOf('power=substation') != -1) {
            numPowerElements['transformers']++;
          }  else if (power_element_tags.indexOf('generator:source=wind') != -1) {
            numPowerElements['windPower']++;
          } else if (power_element_tags.indexOf('generator:source=solar') != -1) {
            numPowerElements['solarPower']++;
          } else if (power_element_tags.indexOf('power=generator') != -1) {
            // power = generator, but not wind or solar
            numPowerElements['otherGenerators']++;
          } else if (power_element_tags.indexOf('power=plant') != -1) {
            numPowerElements['powerPlants']++;
          } else {
            numPowerElements['others']++;
          }
        }
        else if (Object.keys(tags).length != 0 && 'power' in tags) {
          switch(tags.power) {
            case 'tower':
              numPowerElements['powerTowers']++;
              break;
            case 'pole':
              numPowerElements['powerPoles']++;
              break;
            case 'substation':
              numPowerElements['substations']++;
              break;
            case 'sub_station':
              numPowerElements['substations']++;
              break;
            case 'transformer':
              numPowerElements['transformers']++;
              break;
            case 'plant':
              numPowerElements['powerPlants']++;
              break;
            default:
              numPowerElements['others']++;
          }
        }
      }

      function getPowerlineLength(powerline) {
        var distance = powerline.measuredDistanceInsideBoundingBox();
        lengthOfPowerlines['all'] += distance;
        numberOfPowerlines++;
        if ('voltage' in powerline.data.tags) {
          if (powerline.data.tags.voltage in lengthOfPowerlines['voltage']) {
            lengthOfPowerlines['voltage'][powerline.data.tags.voltage] += distance;
          } else {
            lengthOfPowerlines['voltage'][powerline.data.tags.voltage] = distance;
          }
        }
      }

      function getReadableDistance(distance) {
        if (distance > 1000) {
          distanceStr = (distance  / 1000).toFixed(2) + ' km';
        } else {
          distanceStr = Math.ceil(distance) + ' m';
        }
        return distanceStr;
      }
      lengthOfPowerlines['all'] = getReadableDistance(lengthOfPowerlines['all']);

      Object.keys(lengthOfPowerlines['voltage']).forEach(function(key) {
        lengthOfPowerlines['voltage'][key] = getReadableDistance(lengthOfPowerlines['voltage'][key]);
      });

      var statistics = new Array();
      statistics['numPowerElements'] = numPowerElements;
      statistics['lengthOfPowerlines'] = lengthOfPowerlines;
      statistics['numberOfPowerlines'] = numberOfPowerlines;

      pgisMap.sidebar.setContent(MapHelpers.getStatisticSidebarContent(statistics));
      pgisMap.sidebar.show();
  }
};
