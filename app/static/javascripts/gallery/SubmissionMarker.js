SubmissionMarker = L.Marker.extend({
    options: {
        point_id: undefined
    },
    get_data: function() {
        return this.options.data;
    }
});