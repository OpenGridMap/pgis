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
        var _this = this;
        this.markerLayer = markerLayer;
        this.map = map;
        this.galleryContainer = galleryContainer;
        this.gallery = gallery;

        this.gallery.on('jg.complete', function () {
            _this._handleJGComplete(_this);
        });

        this.handleGalleryUpdate();

        return this;
    }, renderGallery: function (onscroll) {
        if (onscroll == true)
            this.n++;
        else
            onscroll = false;

        var min = this.n * this.nBatch;

        var max =  min + this.nBatch <= this._getTotalImageCount() ? min + this.nBatch : this._getTotalImageCount();
        var norewind = false;

        if (onscroll) {
            if (min > max)
                return;

            norewind = true;
        } else {
            this.gallery.empty();
        }

        for (var i = min; i < max; i++) {
            var point = this.map.data[this.current_points[i]];
            this._addPointToGallery(point);
        }

        this._handleGalleryRender(norewind);
    },
    handleGalleryUpdate: function () {
        var visible_points = this._getVisibleMarkers();
        this.n = 0;

        if (this._isRenderRequired(visible_points)) {
            var _this = this;
            this.current_points = visible_points;
            this.renderGallery();

            this.galleryContainer.on('scroll', function () {
                if(_this._galleryScrollTop() + _this._galleryContainerHeight() == _this._contentHeight()) {
                    _this.renderGallery(true);
                }
            });
        }
    },
    addPoint: function (point) {
        this._addPointToGallery(point);
        this._handleGalleryRender(true);
    },
    _addPointToGallery: function (point) {
        this.gallery.append(GalleryHelpers.getGalleryImageContent(point));
    },
    _handleGalleryRender: function (norewind) {
        var _this = this;
        var galleryOptions = null;

        if (norewind == true) {
            galleryOptions = 'norewind';
        }
        else {
            galleryOptions = this.galleryOptions;
            norewind = false;
        }

        this.gallery.justifiedGallery(galleryOptions);

        // if (!norewind) {
        //     this.gallery.on('jg.complete', function () {
        //         if (_this._contentHeight() < _this._galleryContainerHeight()) {
        //             if (_this._getVisibleImageCount() <= _this._getTotalImageCount()) {
        //                 _this.renderGallery(true);
        //             }
        //         }
        //     });
        // }
    },
    _handleJGComplete: function () {
        if (this._contentHeight() < this._galleryContainerHeight()) {
            if (this._getVisibleImageCount() <= this._getTotalImageCount()) {
                this.renderGallery(true);
            }
        }
    },
    _getVisibleMarkers: function () {
        var visible_points = [];
        var _this = this;

       _this.map.markerLayers.markers.eachLayer(function (layer) {
            if ((layer instanceof SubmissionMarker)) {
                if (_this.map.map.getBounds().contains(layer.getLatLng())) {
                    var pid = layer.options.point_id;
                    visible_points.push(pid);
                }
            }
        });
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
    _contentHeight: function () {
        return this.gallery.height();
    },
    _getVisibleImageCount: function () {
        return this.gallery.children().length;
    },
    _getTotalImageCount: function () {
        return this.current_points.length;
    }
};