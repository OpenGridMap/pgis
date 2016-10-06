/*
 * Extends L.Polyline to retrieve measured distance of the part of polyline visible inside bounding box in meters.
 *
 * inspired by https://github.com/danimt/Leaflet.PolylineMeasuredDistance
 *
 * Author: Klaus Schreiber
 */

L.Polyline.prototype.measuredDistanceInsideBoundingBox = function () {

  // x = longitude, y = latitude
  var distance = 0,  coordsA = null, coordsB = null, coordsArray = this._latlngs;
  var bounds = this._map.getBounds(), intersection = null;

  for (i = 0; i < coordsArray.length - 1; i++) {
    coordsA = coordsArray[i];
    coordsB = coordsArray[i+1];
    if (bounds.contains(coordsA)) {

      // point A and B of line is inside bounding box
      if (bounds.contains(coordsB)) {
        distance += coordsA.distanceTo(coordsB)
      }

      // point A but not B of line is inside bounding box
      else {
        northWest = bounds.getNorthWest();
        northEast = bounds.getNorthEast();
        southWest = bounds.getSouthWest();
        southEast = bounds.getSouthEast();
        intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, northWest.lng,
            northWest.lat, northEast.lng, northEast.lat);
        if (intersection.seg1 && intersection.seg2) {
          distance += coordsA.distanceTo(L.latLng(intersection.y, intersection.x));
        } else {
          intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, northEast.lng,
              northEast.lat, southEast.lng, southEast.lat);
          if (intersection.seg1 && intersection.seg2) {
            distance += coordsA.distanceTo(L.latLng(intersection.y, intersection.x));
          } else {
            intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, southEast.lng,
                southEast.lat, southWest.lng, southWest.lat);
            if (intersection.seg1 && intersection.seg2) {
              distance += coordsA.distanceTo(L.latLng(intersection.y, intersection.x));
            } else {
              intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, southWest.lng,
                  southWest.lat, northWest.lng, northWest.lat);
              if (intersection.seg1 && intersection.seg2) {
                distance += coordsA.distanceTo(L.latLng(intersection.y, intersection.x));
              }
            }
          }
        }
      }
    }

    // Not point A but point B is inside bounding box
    else if (bounds.contains(coordsB)) { // point B is inside bounds, but not point A
      northWest = bounds.getNorthWest();
      northEast = bounds.getNorthEast();
      southWest = bounds.getSouthWest();
      southEast = bounds.getSouthEast();
      intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, northWest.lng,
          northWest.lat, northEast.lng, northEast.lat);
        if (intersection.seg1 && intersection.seg2) {
          distance += coordsB.distanceTo(L.latLng(intersection.y, intersection.x));
        } else {
          intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, northEast.lng,
              northEast.lat, southEast.lng, southEast.lat);
          if (intersection.seg1 && intersection.seg2) {
            distance += coordsB.distanceTo(L.latLng(intersection.y, intersection.x));
          } else {
            intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, southEast.lng,
                southEast.lat, southWest.lng, southWest.lat);
            if (intersection.seg1 && intersection.seg2) {
              distance += coordsB.distanceTo(L.latLng(intersection.y, intersection.x));
            } else {
              intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, southWest.lng,
                  southWest.lat, northWest.lng, northWest.lat);
              if (intersection.seg1 && intersection.seg2) {
                distance += coordsB.distanceTo(L.latLng(intersection.y, intersection.x));
              }
            }
          }
        }
    } else { // Point A and Point B aren't inside bounds but maybe part of the line is inside bounds
      var intersectionPoints = [];
      northWest = bounds.getNorthWest();
      northEast = bounds.getNorthEast();
      southWest = bounds.getSouthWest();
      southEast = bounds.getSouthEast();

      intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, northWest.lng,
          northWest.lat, northEast.lng, northEast.lat);
      if (intersection != null && intersection.seg1 && intersection.seg2) {
        intersectionPoints.push(L.latLng(intersection.y, intersection.x));
      }

      intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, northEast.lng,
          northEast.lat, southEast.lng, southEast.lat);
      if (intersection != null && intersection.seg1 && intersection.seg2) {
        intersectionPoints.push(L.latLng(intersection.y, intersection.x));
      }

      intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, southEast.lng,
          southEast.lat, southWest.lng, southWest.lat);
      if (intersection != null && intersection.seg1 && intersection.seg2) {
        intersectionPoints.push(L.latLng(intersection.y, intersection.x));
      }

      intersection = lineIntersect(coordsA.lng, coordsA.lat, coordsB.lng, coordsB.lat, southWest.lng,
          southWest.lat, northWest.lng, northWest.lat);
      if (intersection != null && intersection.seg1 && intersection.seg2) {
        intersectionPoints.push(L.latLng(intersection.y, intersection.x));
      }
      if (intersectionPoints.length == 2) {
        distance += intersectionPoints[0].distanceTo(intersectionPoints[1]);
      }
    }


  }

  // adapted from: http://stackoverflow.com/a/38977789, inspired by http://paulbourke.net/geometry/pointlineplane/
  function lineIntersect(x1, y1, x2, y2, x3, y3, x4, y4)
    {
      var denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1);
      if (denom == 0) { // no intersection
          return null;
      }
      var ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3))/denom;
      var ub = ((x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3))/denom;
      return {
        x: x1 + ua*(x2 - x1),
        y: y1 + ua*(y2 - y1),
        seg1: ua >= 0 && ua <= 1,
        seg2: ub >= 0 && ua <= 1
      };
    }

  return distance;
};
