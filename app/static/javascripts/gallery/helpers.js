// function getJson(url, callback) {
//     var xhr;
//
//     if (typeof XMLHttpRequest !== 'undefined') {
//         xhr = new XMLHttpRequest();
//     } else {
//         var versions = ["MSXML2.XmlHttp.5.0",
//             "MSXML2.XmlHttp.4.0",
//             "MSXML2.XmlHttp.3.0",
//             "MSXML2.XmlHttp.2.0",
//             "Microsoft.XmlHttp"
//         ];
//
//         for (var i = 0, len = versions.length; i < len; i++) {
//             try {
//                 xhr = new ActiveXObject(versions[i]);
//                 break;
//             } catch (e) {}
//         }
//     }
//
//     xhr.onreadystatechange = ensureReadiness;
//
//     function ensureReadiness() {
//         if (xhr.readyState < 4) {
//             return;
//         }
//
//         if (xhr.status !== 200) {
//             return;
//         }
//
//         if (xhr.readyState === 4) {
//             callback(JSON.parse(xhr.responseText));
//         }
//     }
//
//     xhr.open('GET', url, true);
//     xhr.send('');
// }

var registerHandleBarHelpers = function () {
    Handlebars.registerHelper('thumb', function (img) {
        if (img == undefined)
            return '';

        return 'gallery/thumb/' + img;
    });

    Handlebars.registerHelper('power-tag', function (powerTag) {
        var powerTags = {
            "power=transformer": "Transformer",
            "power=substation": "Substation",
            "power=plant": "Power Plant",
            "power=generator;generator:method=photovoltaic;generator:source=solar": "Solar PV",
            "power=generator;generator:method=wind_turbine;generator:source=wind": "Wind Turbine",
            "other": "Other"
        };

        return powerTags[powerTag];
    });

    Handlebars.registerHelper('date', function (epochTime) {
        var date = new Date(epochTime);
        return date.getDay() + '.' +  date.getMonth() + '.' + date.getFullYear();
    });
};

var MapHelpers = {
    getPointPopupContent: function(pointData) {
        var source = $("#popup-template").html();
        var popupTemplate = Handlebars.compile(source);

        return popupTemplate(pointData);
    },
    getGalleryImageContent: function (imageData) {
        var source = $("#gallery-image-template").html();
        var imageTemplate = Handlebars.compile(source);

        return imageTemplate(imageData);
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
