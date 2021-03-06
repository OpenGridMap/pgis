var MapDataLoader = {
    loadBaseMapDataForMapFragment: function (pgisMap, markerLayer, galleryContainer, gallery, splashScreen) {
        var map = pgisMap.map;
        var verifiedIcon = L.icon({
            iconUrl: 'static/images/marker-icon-dark-green-2x.png',
            shadowUrl: 'static/images/marker-shadow.png',
            iconSize:    [25, 41],
            iconAnchor:  [12, 41],
            popupAnchor: [1, -34],
            shadowSize:  [41, 41]
        });
        var unverifiedIcon = L.icon({
            iconUrl: 'static/images/marker-unverified-icon-2x.png',
            shadowUrl: 'static/images/marker-shadow.png',
            iconSize:    [25, 41],
            iconAnchor:  [12, 41],
            popupAnchor: [1, -34],
            shadowSize:  [41, 41]
        });
        var selectedPointIcon = L.icon({
              iconUrl: 'static/images/marker-icon-red-2x.png',
              shadowUrl: 'static/images/marker-shadow.png',
              iconSize:    [25, 41],
              iconAnchor:  [12, 41],
              popupAnchor: [1, -34],
              shadowSize:  [41, 41]
        });
        var submission_data_url = '/gallery/data';
        var states_layer_data_url = '/static/javascripts/gallery/states.geo.json';
        var countries_layer_data_url = '/static/javascripts/gallery/countries.geo.json';

        var galleryHandler = null;

        $.getJSON({
            url: submission_data_url,
            success: function (data) {
                markerLayer.clearLayers();

                data.forEach(function (point) {
                    var popupHtml = MapHelpers.getPointPopupContent(point);
                    var latlng = point['latlng'];
                    var icon;

                    if (point['approved'])
                        icon = verifiedIcon;
                    else {
                        icon = unverifiedIcon;

                    }

                    var marker = new SubmissionMarker(latlng, {
                        icon: icon,
                        point_id: point.id
                    }).bindPopup(popupHtml);

                    marker.on({
                        'mouseover': function (event, data) {
                            // TODO Gallery integration of mouseover
                        },
                        'mouseout': function (event, data) {
                            // TODO Gallery integration of mouseout
                        },
                        'popupopen': function (event, data) {
                            var marker = this;
                            var popupContent = MapHelpers.getPointPopupContent(point, true);

                            marker.setPopupContent(popupContent);
                        },
                        'popupclose': function (event, data) {
                            marker.setPopupContent(popupHtml);
                        }
                    });

                    $(document).on('gallery-' + point.id, function (e, d) {
                        if (d.event == 'mouseover') {
                            marker.setIcon(selectedPointIcon);
                        } else if (d.event == 'mouseout') {
                            marker.setIcon(icon);
                        }

                    });

                    markerLayer.addLayer(marker);

                    if (splashScreen != undefined)
                        splashScreen.hide();

                    pgisMap.data[point.id] = point;
                });

                galleryHandler = GalleryHandler.initialize(markerLayer, pgisMap, galleryContainer, gallery);

                pgisMap.map.on({'moveend': function () {
                    galleryHandler.handleGalleryUpdate();
                }});
            }
        });
    }
};