var GalleryHandler = {
    markerLayer: null,
    galleryContainer: null,
    gallery: null,
    data: null,
    current_points: [],
    map: null,
    n: 0,
    nBatch: 100,
    galleryOptions: {
        rowHeight: 50,
        margins: 2,
        border: 5,
        sort: function (a, b) {
            a = $(a).data('timestamp');
            b = $(b).data('timestamp');

            return a - b;
        },
        cssAnimation: true
    },
    initialize: function (markerLayer, map, galleryContainer, gallery) {
        this.markerLayer = markerLayer;
        this.map = map;
        this.galleryContainer = galleryContainer;
        this.gallery = gallery;
        this.handleGalleryUpdate();
    },
    renderGallery: function (onscroll) {
        if (onscroll == true)
            this.n++;
        else
            onscroll = false;

        var min = this.n * this.nBatch;
        var max =  min + this.nBatch <= this._getTotalImageCount() ? min + this.nBatch : this._getTotalImageCount();
        var galleryOptions = this.galleryOptions;
        var _this = this;

        if (onscroll) {
            if (min > max)
                return;

            galleryOptions = 'norewind';
        } else {
            this.gallery.empty();
        }

        for (var i = min; i < max; i++) {
            var point = this.map.data[this.current_points[i]];
            this.gallery.append(MapHelpers.getGalleryImageContent(point));
        }

        this.gallery.justifiedGallery(galleryOptions);

        this.gallery.on('jg.complete', function () {
            if (_this._galleryHeight() < _this._galleryContainerHeight()) {
                if (_this._getVisibleImageCount() <= _this._getTotalImageCount()) {
                    _this.renderGallery(true);
                }
            }
        });
    },
    handleGalleryUpdate: function () {
        var visible_points = this._getVisibleMarkers();
        this.n = 0;

        if (this._isRenderRequired(visible_points)) {
            var _this = this;
            this.current_points = visible_points;
            this.renderGallery();

            this.galleryContainer.on('scroll', function () {
                if(_this._galleryScrollTop() + _this._galleryContainerHeight() == _this._galleryHeight()) {
                    _this.renderGallery(true);
                }
            });
        }


    },
    _getVisibleMarkers: function () {
        var visible_points = [];
        // var i = 0;
        var _this = this;

       _this.map.markerLayers.markers.eachLayer(function (layer) {
            if ((layer instanceof SubmissionMarker)) {
                if (_this.map.map.getBounds().contains(layer.getLatLng())) {
                    var pid = layer.options.point_id;
                    visible_points.push(pid);
                    // i++;
                }
            }
        });
        // console.log(i);
        return visible_points.sort().reverse();
    },
    _isRenderRequired: function (visiblePoints) {
        if (this.current_points != null) {
            var diff = _.union(
                _.difference(this.current_points, visiblePoints),
                _.difference(visiblePoints, this.current_points)
            );

            if (diff.length > 0) return true;
        }

        return false;
    },
    _galleryScrollTop: function () {
        return this.galleryContainer.scrollTop();
    },
    _galleryContainerHeight: function () {
        return this.galleryContainer.height();
    },
    _galleryHeight: function () {
        return this.gallery.height();
    },
    _getVisibleImageCount: function () {
        return this.gallery.children().length;
    },
    _getTotalImageCount: function () {
        return this.current_points.length;
    }
};