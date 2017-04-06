$(document).ready(function () {
    registerHandleBarHelpers();

    var osmTile = MapHelpers.getOsmTile();
    var satelliteTile = MapHelpers.getSatelliteTile();

    var pgisMap = new PgisMap();
    pgisMap.createMap(osmTile);

    var map = pgisMap.map;

    var baseMaps = {
        "Satellite View": satelliteTile,
        "Topological View": osmTile
    };

    pgisMap.addBaseMaps(baseMaps);

    pgisMap.addMarkerLayer({
        name: 'markers',
        layer: new L.MarkerClusterGroup()
    });
    pgisMap.addMarkerLayer({
        name: 'clusterGroup',
        layer: new L.LayerGroup()
    });
    pgisMap.addMarkerLayer({
        name: 'powerlinesLayerGroup',
        layer: new L.LayerGroup()
    });

    var _pgisMap = pgisMap;

    pgisMap.baseMapDataLoader = function () {
        if (_.contains(_pgisMap.selectedOverlayLayers, "relations")
            || _.contains(_pgisMap.selectedOverlayLayers, "transnet")) {
            MapDataLoader.fetchAndPlotRelations(_pgisMap);
        }
        else if (_.contains(_pgisMap.selectedOverlayLayers, "contribute")) {
            MapDataLoader.loadLinesWithMissingData(
                this,
                this.markerLayers.markers,
                this.markerLayers.clusterGroup,
                this.markerLayers.powerlinesLayerGroup
            );
        }
        else {
            MapDataLoader.loadBaseMapDataForMapFragment(
                this,
                this.markerLayers.markers,
                this.markerLayers.clusterGroup,
                this.markerLayers.powerlinesLayerGroup
            );
        }
    };

    pgisMap.baseMapDataLoader();

    pgisMap.addOverlayLayer({
        name: "Relations",
        ref: 'relations',
        layer: new L.LayerGroup()
    });

    pgisMap.addOverlayLayer({
        name: "Transnet",
        ref: 'transnet',
        layer: new L.LayerGroup()
    });

    pgisMap.addOverlayLayer({
        name: "Contribute",
        ref: 'contribute',
        layer: new L.LayerGroup()
    });

    var newPointLinkProperties = {
        ref: 'newPoint',
        text: 'New Point',  // string
        onclick: function () {
            window.location.href = '/admin/points/new?redirect_back=true'
                + '&lat=' + pgisMap.map.getBounds().getCenter().lat
                + '&long=' + pgisMap.map.getBounds().getCenter().lng
                + '&zoom=' + pgisMap.map.getZoom();
        }
    };
    pgisMap.addLinkButton(newPointLinkProperties);

    var rankingTableLinkProperties = {
        ref: 'ranking',
        text: 'Top 10 Ranking',
        onclick: function () {
            window.location.href = '/ranking';
        }
    };
    pgisMap.addLinkButton(rankingTableLinkProperties);

    var userProfileLinkProperties = {
        ref: 'userprofile',
        text: 'Your Profile',
        onclick: function () {
            window.location.href = '/userprofile';
        }
    };
    pgisMap.addLinkButton(userProfileLinkProperties);

    var statisticLinkProperties = {
        ref: 'statistic',
        text: 'Open statistics',
        onclick: function () {
            Statistics.countPowerObjects(pgisMap);
        }
    };
    pgisMap.addLinkButton(statisticLinkProperties);

    var galleryLinkProperties = {
        ref: 'gallery',
        text: 'Gallery',
        onclick: function () {
            window.location.href = '/gallery';
        }
    };
    pgisMap.addLinkButton(galleryLinkProperties);

    var addPointProperties = {
        ref: 'addPoint',
        text: 'Add Point',  // string
        onclick: function () {
            MapEditor.addPoint(pgisMap);
        }
    };
    pgisMap.addLinkButton(addPointProperties);

    pgisMap.addLinkButton({
        ref: 'exportRelations',
        text: 'Export Relations in Bound',
        onclick: function () {
            window.open(
                '/' + pgisMap.selectedOverlayLayers[0] +
                '/export?bounds=' + pgisMap.map.getBounds().toBBoxString()
                + '&zoom=' + _pgisMap.map.getZoom()
                + '&countries=' + _pgisMap.selectedCountries.toString()
                + '&voltages=' + _pgisMap.selectedVoltages.toString(),
                '_blank'
            )
        }
    });
    pgisMap.hideLinkButton(pgisMap.linkButtons.exportRelations);

    pgisMap.addLinkButton({
        ref: 'transnetFilters',
        text: 'Transnet Filters',
        onclick: function () {
            pgisMap.transnetFilterSidebar.toggle();
            pgisMap.transnetValidationsSidebar.hide();
        }
    });
    pgisMap.hideLinkButton(pgisMap.linkButtons.transnetFilters);

    pgisMap.addLinkButton({
        ref: 'transnetOperations',
        text: 'Transnet Operations',
        onclick: function () {
            pgisMap.transnetOperationsSidebar.toggle();
        }
    });
    pgisMap.hideLinkButton(pgisMap.linkButtons.transnetOperations);

    pgisMap.addLinkButton({
        ref: 'transnetRepo',
        text: 'Transnet Repository',
        onclick: function () {
             window.open(
                'https://github.com/OpenGridMap/transnet',
                '_blank'
            )
        }
    });
    pgisMap.hideLinkButton(pgisMap.linkButtons.transnetRepo);

    pgisMap.addLinkButton({
        ref: 'transnetModels',
        text: 'Transnet Models',
        onclick: function () {
            window.open(
                'https://github.com/OpenGridMap/transnet-models',
                '_blank'
            )
        }
    });
    pgisMap.hideLinkButton(pgisMap.linkButtons.transnetModels);

    pgisMap.addLinkButton({
        ref: 'contributionFilters',
        text: 'Electrical Components Filters',
        onclick: function () {
            pgisMap.contributionFilterSidebar.toggle();
        }
    });
    pgisMap.hideLinkButton(pgisMap.linkButtons.contributionFilters);


    window.pgisMap = pgisMap;

    pgisMap.onOverlayAdd = function (layer) {
        if (layer.name == 'Relations') {
            _pgisMap.showLinkButton(_pgisMap.linkButtons.exportRelations);
        }

        if (layer.name == 'Transnet') {
            _pgisMap.showLinkButton(_pgisMap.linkButtons.transnetFilters);
            _pgisMap.showLinkButton(_pgisMap.linkButtons.transnetOperations);
            _pgisMap.showLinkButton(_pgisMap.linkButtons.transnetRepo);
            _pgisMap.showLinkButton(_pgisMap.linkButtons.transnetModels);
        }

        if (layer.name == 'Contribute') {
            _pgisMap.showLinkButton(_pgisMap.linkButtons.contributionFilters);
        }
        _.each(_pgisMap.markerLayers, function (layer) {
            layer.clearLayers();
        });

        this.baseMapDataLoader();
    };

    pgisMap.onOverlayRemove = function (layer) {
        if (layer.name == 'Relations') {
            _pgisMap.hideLinkButton(_pgisMap.linkButtons.exportRelations);
        }

        if (layer.name == 'Transnet') {
            _pgisMap.hideLinkButton(_pgisMap.linkButtons.transnetFilters);
            _pgisMap.hideLinkButton(_pgisMap.linkButtons.transnetOperations);
            _pgisMap.hideLinkButton(_pgisMap.linkButtons.transnetRepo);
            _pgisMap.hideLinkButton(_pgisMap.linkButtons.transnetModels);
            if (_pgisMap.voltagesLegend !== undefined && _pgisMap.voltagesLegend._map)
                _pgisMap.voltagesLegend.removeFrom(_pgisMap.map);
        }

        if (layer.name == 'Contribute') {
            _pgisMap.hideLinkButton(_pgisMap.linkButtons.contributionFilters);
            _pgisMap.contributionFilterSidebar.hide();
        }
        _.each(_pgisMap.markerLayers, function (layer) {
            layer.clearLayers();
        });

        this.baseMapDataLoader();
    };

    Handlebars.registerHelper('relationSelectionButton', function () {
        htmlClasses = [];
        if (this.selectedRelationsIds.indexOf(this.relation.id.toString()) > -1) {
            htmlClasses.push("remove-relation-from-selection");
            htmlText = "Remove relation from export";
        } else {
            htmlClasses.push("add-relation-to-selection");
            htmlText = "Select relation to export"
        }
        return new Handlebars.SafeString(
            "<button class='" + htmlClasses.join(" ") + "'"
            + "data-relation-id='" + this.relation.id + "'>"
            + htmlText
            + "</button>"
        );
    });


    Handlebars.registerHelper('relationSelectionSummaryAndActions', function () {
        htmlClasses = [];
        if (this.selectedRelationsIds.indexOf(this.relation.id.toString()) > -1) {
            htmlClasses.push("remove-relation-from-selection");
            htmlText = "Remove relation from export";
        } else {
            htmlClasses.push("add-relation-to-selection");
            htmlText = "Select relation to export"
        }

        if (this.selectedRelationsIds.length > 0) {
            return new Handlebars.SafeString(
                "<div>" +
                this.selectedRelationsIds.length.toString() +
                " relation(s) currently selected. " +
                "<a class='export-relation-selection' style='cursor:pointer'>" +
                "Export" +
                "</a> | " +
                "<a class='clear-relation-selection' style='cursor:pointer'>" +
                "Clear All" +
                "</a> " +
                "</div>"
            );
        }

        return "";
    });


    relationSelection = Pgis.Relation.selectionMode.init(pgisMap);
});
