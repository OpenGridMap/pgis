var MapEditor = {
  addPoint: function(pgisMap) {
    $('#map').css('cursor', 'url(static/images/marker-icon-red.cur) 12 41, crosshair');
    pgisMap.sidebar.setContent(MapHelpers.getPlacePointSidebarContent());
    pgisMap.sidebar.show();

    //workaround: because MapEditor.addPoint is triggered by onclick it would also trigger the pgisMap.map onclick
    // trigger without timeout
    setTimeout(function(){
      pgisMap.map.on('click', function addMarker(e) {
        pgisMap.map.off('click', addMarker);

        var unverifiedIcon = L.icon({
          iconUrl: 'static/images/marker-unverified-icon-2x.png',
          shadowUrl: 'static/images/marker-shadow.png',
          iconSize:    [25, 41],
          iconAnchor:  [12, 41],
          popupAnchor: [1, -34],
          shadowSize:  [41, 41]
        });
        var marker = L.marker([e.latlng.lat, e.latlng.lng], {icon: unverifiedIcon}).addTo(pgisMap.map);
        $('#map').css('cursor', 'auto');

        MapEditor.addPointData(pgisMap, marker.getLatLng());
      })
    }, 1);

  },

  addPointData: function(pgisMap, latlng) {
    sidebarData = new Array();
    sidebarData['latlng'] = latlng;
    pgisMap.sidebar.setContent(MapHelpers.getAddPointSidebarContent(sidebarData));
    $('#addPowerObject button').click(function() {
      var powerObjectVal = $(this).val();
      var powerObjectText = $(this).text();
      var properties = {
        tags: {timestamp: new Date(),
               power_element_tags: ['power=' + powerObjectVal]}
      };
      var jsonproperties = JSON.stringify(properties);
      $('#properties').val(jsonproperties);
      $('#addPowerObject').hide();
      $('#addPowerDetails').show();
      $('#powerDetailsTitle').text('Add ' + powerObjectText);
      $('#backToPowerObject').click(function () {
      $('#addPowerDetails').hide();
      $('#addPowerObject').show();
      });
    });

    var form = $( '#addPoint' );
    formdata = new FormData();

    $('#picture').change( function(evt) {
          var pictures = evt.target.files; // FileList object

        // Loop through the FileList and render image files as thumbnails.
        for (var i = 0, f; f = pictures[i]; i++) {

          // Only process image files.
          if (!f.type.match('image.*')) {
            continue;
          }

          var reader = new FileReader();

          // Closure to capture the file information.
          reader.onload = (function(theFile) {
            return function(e) {
              // Render thumbnail.
              var span = document.createElement('span');
              span.innerHTML = ['<img class="thumb" src="', e.target.result,
                                '" title="', escape(theFile.name), '"/>'].join('');
              document.getElementById('list').insertBefore(span, null);
            };
          })(f);

          // Read in the image file as a data URL.
          reader.readAsDataURL(f);
          formdata.append('images[]', f);
          }
    });
  },

  submitPoint: function () {
    formdata.append('latitude', $('#latitude').val());
    formdata.append('longitude', $('#longitude').val());
    formdata.append('properties', $('#properties').val());

    $.ajax({
    url: '/submissions/create_by_webapp',
    type: 'POST',
    data: formdata,
    processData: false,
    contentType: false,
    success: function (data) {
      alert( "Thanks for uploading");
      pgisMap.sidebar.hide();
    }
  });
  }
};
