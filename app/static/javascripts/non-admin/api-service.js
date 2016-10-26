var ApiService = {
    fetchRelationsData: function (pgisMap, successCallback) {
        var map = pgisMap.map;

        map.fireEvent("dataloading");

        var url = "/" + pgisMap.selectedOverlayLayers[0];

        $.ajax({
            url: url,
            data: {
                "bounds": map.getBounds().toBBoxString(),
                "countries": pgisMap.selectedCountries.toString(),
                "voltages": pgisMap.selectedVoltages.toString(),
                "zoom": map.getZoom()
            },
            success: function (data) {
                successCallback(data);
                map.fireEvent("dataload");
            }
        })
    }
};