var GalleryHandler = {
    markerLayer: null,
    galleryContainer: null,
    data: null,
    current_points: [],
    pgisMap: null,
    n: 0,
    galleryOptions: {
        rowHeight: 50,
        margins: 2,
        border: 5
    },
    initialize: function (markerLayer) {
        this.markerLayer = markerLayer;
        this.pgisMap = window.pgisMap;
        this.handleGalleryUpdate();
    },
    // renderGallery: function () {
        // if (this.current_points != null) {
        //     var diff = (visible_points, this.current_points);
        //     var intersection = _.intersection(visible_points, this.current_points);
        //     var pointsToBeRemoved = _.difference(visible_points, intersection);
        //     var pointsToBeAdded = _.difference(this.current_points, intersection);
        //
            // var n = pointsToBeRemoved.length;
            // for (var i = 0; i < n; i++) {
            //     var item = $('a[data-lightbox="' + pointsToBeRemoved[i] + '"]');
            //     item.remove();
            // }
            //
            // this.current_points = _.union(intersection, pointsToBeAdded);
        // }
    // },
    renderGallery: function (galleryContainer, onscroll) {
        var nBatch = 100;

        if (onscroll == true)
            this.n++;

        var min = this.n * nBatch;
        var max =  min + nBatch <= this.current_points.length ? min + nBatch : this.current_points.length;

        if (onscroll == true) {
            if (min > max) {
                return;
            }
        } else {
            galleryContainer.empty();
        }

        for (var i = min; i < max; i++) {
            var point = pgisMap.data[this.current_points[i]];
            galleryContainer.append(MapHelpers.getGalleryImageContent(point));
        }

        if (onscroll)
            galleryContainer.justifiedGallery('norewind');
        else
            galleryContainer.justifiedGallery(this.galleryOptions);
    },
    handleGalleryUpdate: function () {
        var visible_points = [];
        var sidebar = $('#sidebar');
        var galleryContainer = $('#sidebar-content');

        this.n = 0;

        var i = 0;

        pgisMap.markerLayers.markers.eachLayer(function (layer) {
            if ((layer instanceof SubmissionMarker)) {
                if (pgisMap.map.getBounds().contains(layer.getLatLng())) {
                    var pid = layer.options.point_id;
                    visible_points.push(pid);
                    i++;
                }
            }
        });

        console.log(i);

        this.current_points = visible_points.sort().reverse();
        this.renderGallery(galleryContainer);

        var _this = this;

        sidebar.scroll(function () {
            var scrollTop = sidebar.scrollTop();
            console.log(sidebar.scrollTop());
            if(sidebar.scrollTop() + sidebar.height() == galleryContainer.height()) {
                _this.renderGallery(galleryContainer, true);
            }
        })
    }
};