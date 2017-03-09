var ApiService = {
    fetchRelationsData: function (pgisMap, successCallback) {
        var map = pgisMap.map;
        var currentRequest = null;
        map.fireEvent("dataloading");

        var url = "/" + pgisMap.selectedOverlayLayers[0];

        currentRequest = $.ajax({
            url: url,
            data: {
                "bounds": map.getBounds().toBBoxString(),
                "countries": pgisMap.selectedCountries.toString(),
                "voltages": pgisMap.selectedVoltages.toString(),
                "zoom": map.getZoom()
            },
            beforeSend: function () {
                if (currentRequest != null) {
                    currentRequest.abort();
                }
            },
            success: function (data) {
                successCallback(data);
                map.fireEvent("dataload");
            }
        })
    }
};