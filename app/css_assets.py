common_css_files = [
    'stylesheets/leaflet.css',
    'stylesheets/leaflet.draw.css',
    'stylesheets/MarkerCluster.css',
    'stylesheets/MarkerCluster.Default.css'
]
non_admin_css_files = common_css_files + [
    'stylesheets/main.less.css',
    'stylesheets/Control.Geocoder.css',
    'stylesheets/L.Control.Sidebar.css',
    'stylesheets/Control.Loading.css',
    'stylesheets/Control.LinkButton.css'
]

admin_css_files = common_css_files + [
    'stylesheets/admin_main.less.css',
]
