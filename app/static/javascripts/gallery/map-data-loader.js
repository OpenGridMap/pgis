var MapDataLoader = {
    loadBaseMapDataForMapFragment: function (pgisMap, markerLayer, galleryContainer, gallery) {
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
                            var pointCopy = point;

                            pointCopy['isPopupThumbVisible'] = true;
                            var popupContent = MapHelpers.getPointPopupContent(pointCopy);
                            marker.setPopupContent(popupContent);

                            var id = '#' + $(popupContent).children('img')[0].id;

                            $(id).on('click', function () {
                                $('#gallery-thumb-' + pointCopy.id).trigger('click');
                            });
                        },
                        'popupclose': function (event, data) {
                            // console.log(point);
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

                    pgisMap.data[point.id] = point;
                });

                GalleryHandler.initialize(markerLayer, pgisMap, galleryContainer, gallery);

                pgisMap.map.on({'moveend': function () {
                    GalleryHandler.handleGalleryUpdate();
                }});
            }
        });

        // $.getJSON({
        //     url: countries_layer_data_url,
        //     success: function (data) {
        //     }
        // });

    }
};