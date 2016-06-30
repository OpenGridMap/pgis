var ApiService = {
  fetchRelationsData: function(pgisMap) {
    var map = pgisMap.map;

    map.fireEvent("dataloading");

    $.ajax({
      url: "/relations",
      data: {
        "bounds": map.getBounds().toBBoxString()
      },
      success: function(data) {
        console.log(data);
      }
    })
  }
};
