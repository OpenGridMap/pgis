var ApiService = {
    fetchRelationsData: function (pgisMap, successCallback) {
        var map = pgisMap.map;

        map.fireEvent("dataloading");

        $.ajax({
            url: "/relations",
            data: {
                "bounds": map.getBounds().toBBoxString()
            },
            success: function (data) {
                successCallback(data)
                map.fireEvent("dataload");
            }
        })
    },
    fetchTransnetData: function (pgisMap, successCallback) {
        var map = pgisMap.map;

        map.fireEvent("dataloading");

        $.ajax({
            url: "/transnet",
            data: {
                "bounds": map.getBounds().toBBoxString()
            },
            success: function (data) {
                successCallback(data)
                map.fireEvent("dataload");
            }
        })
    }
};