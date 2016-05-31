common_js_files = [
    'javascripts/leaflet-src.js',
    'javascripts/handlebars-v3.0.3.js',
    'javascripts/underscore-min.js',
    'javascripts/leaflet.markercluster-src.js'
]
non_admin_js_files = common_js_files + [
    'javascripts/Control.Geocoder.js',
    'javascripts/Control.LinkButton.js',
    'javascripts/underscore-min.js',
    'javascripts/L.Control.Sidebar.js',
    'javascripts/Control.Loading.js',
    'javascripts/Map.SelectArea.min.js',
    'javascripts/main.js'
]

admin_js_files = common_js_files + [
    'javascripts/admin_main.js',
    'javascripts/leaflet.draw-src.js',
]
