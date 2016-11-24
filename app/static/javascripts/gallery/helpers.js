var registerHandleBarHelpers = function () {
    Handlebars.registerHelper('thumb', function (img) {
        if (img == undefined)
            return '';

        return 'gallery/thumb/' + img;
    });

    Handlebars.registerHelper('power_tag', function (powerTag) {
        var powerTags = {
            "power=transformer": "Transformer",
            "power=substation": "Substation",
            "power=plant": "Power Plant",
            "power=generator;generator:method=photovoltaic;generator:source=solar": "Solar PV",
            "power=generator;generator:method=wind_turbine;generator:source=wind": "Wind Turbine",
            "other": "Other",
            "Transformer": "Transformer",
            "Substation": "Substation",
            "Generator": "Generator",
            "PV or Wind Farm": "PV or Wind Farm",
            "Other": "Other"
        };

        return powerTags[powerTag];
    });

    Handlebars.registerHelper('date', function (epochTime) {
        var date = new Date(0);
        date.setUTCSeconds(epochTime);
        return date.getDate() + '.' +  (date.getMonth() + 1) + '.' + date.getFullYear();
        // return date.toLocaleDateString();
    });
};

var MapHelpers = {
    getPointPopupContent: function(pointData, isPopupThumbVisible) {
        var source = $("#popup-template").html();
        var popupTemplate = Handlebars.compile(source);

        if (isPopupThumbVisible == true)
            pointData['isPopupThumbVisible'] = true;

        return popupTemplate(pointData);
    },
    getSplashScreen: function () {
        return $('#splash-screen')
    },
    getOsmTile: function() {
        return L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; ' +
                '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery © <a href="http://mapbox.com">Mapbox</a>',
            maxZoom: 18,
            minZoom: 2
        });
    },
    getSatelliteTile: function() {
        return L.tileLayer(
            'http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/' +
            'MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Map data &copy; ' +
                    '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                    '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                    'Imagery © <a href="http://mapbox.com">Mapbox</a>',
                maxZoom: 18,
                minZoom: 2
            }
        );
    }
};

var GalleryHelpers = {
    getGalleryImageContent: function (imageData) {
        var source = $("#gallery-image-template").html();
        var imageTemplate = Handlebars.compile(source);

        return imageTemplate(imageData);
    },
    getGalleryContainer: function () {
        return $('#sidebar');
    },
    getGallery: function () {
        return $('#sidebar-content');
    }
};
