common_js_files = [
    'javascripts/libraries/leaflet-src.js',
    'javascripts/libraries/handlebars-v3.0.3.js',
    'javascripts/libraries/underscore-min.js',
    'javascripts/libraries/leaflet.markercluster-src.js',
    'javascripts/libraries/MarkerClusterGroup.Refresh.js',
    'javascripts/helpers/misc-helpers.js',
    'javascripts/helpers/handlebars.js'
]

non_admin_js_files = common_js_files + [
    'javascripts/libraries/Control.Geocoder.js',
    'javascripts/libraries/Control.LinkButton.js',
    'javascripts/libraries/underscore-min.js',
    'javascripts/libraries/L.Control.Sidebar.js',
    'javascripts/libraries/Control.Loading.js',
    'javascripts/libraries/Map.SelectArea.min.js',
    'javascripts/non-admin/leaflet.pgis.relation.markerClusterGroup.js',
    'javascripts/non-admin/leaflet.pgis.relation.featureGroup.js',
    'javascripts/non-admin/leaflet.pgis.transnet.markerClusterGroup.js',
    'javascripts/non-admin/leaflet.pgis.transnet.featureGroup.js',
    'javascripts/non-admin/pgis-map.js',
    'javascripts/non-admin/map-helpers.js',
    'javascripts/non-admin/map-data-loader.js',
    'javascripts/non-admin/api-service.js',
    'javascripts/non-admin/pgis.relation.selectionMode.js',
    'javascripts/non-admin/main.js',
]

admin_js_files = common_js_files + [
    'javascripts/admin_main.js',
    'javascripts/libraries/leaflet.draw-src.js',
]