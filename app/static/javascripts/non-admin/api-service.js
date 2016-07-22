var ApiService = {
  fetchRelationsData: function(pgisMap, successCallback) {
    var map = pgisMap.map;

    map.fireEvent("dataloading");

    $.ajax({
      url: "/relations",
      data: {
        "bounds": map.getBounds().toBBoxString()
      },
      success: function(data) {
        successCallback(data)
        map.fireEvent("dataload");
      }
    })
  }
};
