var MapEditor = {

  checkLogin: function (pgisMap) {
    $.get( '/is_authenticated')
        .done(function (data) {
          if (data.is_authenticated) {
            MapEditor.addPoint(pgisMap);
          } else {
            //pgisMap.sidebar.setContent('You need to be logged in first!<br><a target="_blank" href="/admin/do_login?next=/index&redirect_back=true">Login</a> ');
            //pgisMap.sidebar.show();
            window.location.replace('/admin/login?next=%2Findex%3Fredirect_back%3Dtrue%26lat%3D'
                + pgisMap.map.getBounds().getCenter().lat + '%26long%3D' + pgisMap.map.getBounds().getCenter().lng
                + '%26zoom%3D' + pgisMap.map.getZoom());
          }
        })
        .error(function () {
          pgisMap.sidebar.setContent('There was a connection problem on your side or on our side. Please try again.');
            pgisMap.sidebar.show();
        })
  },

  addPoint: function(pgisMap) {

    $('#map').css('cursor', 'url(static/images/marker-icon-red.cur) 12 41, crosshair');
    pgisMap.sidebar.setContent(MapHelpers.getPlacePointSidebarContent());
    pgisMap.sidebar.show();


    //workaround: because MapEditor.addPoint is triggered by onclick it would also trigger the pgisMap.map onclick
    // trigger without timeout
    setTimeout(function(){
      pgisMap.map.on('click', addMarker)
    }, 1);

    function addMarker(e) {
        pgisMap.map.off('click', addMarker);

        var unverifiedIcon = L.icon({
          iconUrl: 'static/images/marker-unverified-icon-2x.png',
          shadowUrl: 'static/images/marker-shadow.png',
          iconSize:    [25, 41],
          iconAnchor:  [12, 41],
          popupAnchor: [1, -34],
          shadowSize:  [41, 41]
        });

        var marker = L.marker([e.latlng.lat, e.latlng.lng], {icon: unverifiedIcon, draggable: true}).addTo(pgisMap.map);
        $('#map').css('cursor', 'auto');


        MapEditor.addPointData(pgisMap, marker);
      }

    // if sidebar is closed before adding a point
    pgisMap.sidebar.on('hide', function abortAddPoint () {
      pgisMap.map.off('click', addMarker);
      $('#map').css('cursor', 'auto');
      pgisMap.sidebar.off('hide', abortAddPoint);
    });

  },

  addPointData: function(pgisMap, marker) {
    sidebarData = new Array();
    sidebarData['latlng'] = marker.getLatLng();
    marker.on('move', moveMarker);

    function moveMarker(e) {
      sidebarData['latlng'] = e.latlng;
      pgisMap.sidebar.setContent(MapHelpers.getAddPointSidebarContent(sidebarData));
      $('#addPowerObject button').click(showUploadForm);
    }

    pgisMap.sidebar.setContent(MapHelpers.getAddPointSidebarContent(sidebarData));
    $('#addPowerObject button').click(showUploadForm);

    function showUploadForm() {
      marker.off('move', moveMarker);
      marker.dragging.disable();
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
        marker.on('move', moveMarker);
        marker.dragging.enable();
      });
    }

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
