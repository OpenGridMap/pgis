// Responsible for all relation selection actions
// Aware of LocalStorage, PgisMap, MapHelpers


if (typeof(Pgis) == 'undefined') {
    var Pgis = {};
}

if (typeof(Pgis.Relation) == 'undefined') {
    Pgis.Relation = {};
}

Pgis.Relation.selectionMode = {
    pgisMap: undefined,
    _localStorageKey: 'selectedRelations',

    init: function (pgisMap) {
        this.pgisMap = pgisMap;
        this._bindRelationSelectionEvents();
        this._bindTransnetFilterEvents();
        var _this = this;
        this.pgisMap.addLinkButton({
            ref: 'exportRelationsWithId',
            text: 'Export selected relations',
            onclick: _this.redirectToExport()
        });
        this._checkAndToggleExportButtonDisplay();

        return this;
    },

    clearRelations: function () {
        localStorage.removeItem(this._localStorageKey);
    },

    redirectToExport: function () {
        var _this = this;
        return function () {
            window.open(
                '/' + _this.pgisMap.selectedOverlayLayers[0] +
                '/export?ids=' + _this._getSelectedRelations().join(',')
                + '&countries=' + this.pgisMap.selectedCountries
                + '&voltages=' + this.pgisMap.selectedVoltages,
                '_blank'
            );
        }
    },

    handleRelationHighlightForSelection: function () {
        var _this = this;
        this.pgisMap.overlayLayers[this.pgisMap.selectedOverlayLayers[0]].layer.eachLayer(function (relationFeatureLayer) {
            // if selected, add selectionStyle.
            if (_this._getSelectedRelations().indexOf(relationFeatureLayer.relation.id.toString()) > -1) {
                relationFeatureLayer.highlightForExport();
            } else {
                relationFeatureLayer.removeHighlightForExport();
            }
        });
    },

    _bindTransnetFilterEvents: function () {
        var _this = this;

        $(document).on('click', '.transnet-voltage-filter', function () {
            var voltage = $(this).attr('data-voltage');
            var index = _this.pgisMap.selectedVoltages.indexOf(voltage);
            if (index > -1) {
                _this.pgisMap.selectedVoltages.splice(index, 1);
            }
            else {
                _this.pgisMap.selectedVoltages.push(voltage);
            }
        });

        $(document).on('click', '.transnet-country-filter', function () {
            var country = $(this).attr('data-country');
            var index = _this.pgisMap.selectedCountries.indexOf(country);
            if (index > -1) {
                _this.pgisMap.selectedCountries.splice(index, 1);
            }
            else {
                _this.pgisMap.selectedCountries.push(country);
            }
        });
    },

    _bindRelationSelectionEvents: function () {
        var _this = this;

        $(document).on('click', '.add-relation-to-selection', function () {
            $(document).trigger('relationSelected', {
                relationId: $(this).attr('data-relation-id')
            });
        });

        $(document).on('click', '.remove-relation-from-selection', function () {
            $(document).trigger('relationUnselected', {
                relationId: $(this).attr('data-relation-id')
            });
        });

        $(document).on('click', '.clear-relation-selection', function () {
            _this.clearRelations();
            $(document).trigger('relationsCleared');
        });

        $(document).on('click', '.export-relation-selection', function () {
            _this.redirectToExport()();
        });

        $(document).on('relationSelected', function (event, options) {
            selectedRelationsIds = _this._getSelectedRelations(); // from local storage
            if (selectedRelationsIds.indexOf(options.relationId) > -1) {
                console.log("Relation already selected");
            } else {
                selectedRelationsIds.push(options.relationId)
                _this._saveSelectedRelations(selectedRelationsIds);
            }
            _this._checkAndToggleExportButtonDisplay();
            _this._updateMapSidebarContent();
            _this.handleRelationHighlightForSelection();
        });

        $(document).on('relationUnselected', function (event, options) {
            selectedRelationsIds = _this._getSelectedRelations(); // from local storage
            index = selectedRelationsIds.indexOf(options.relationId)
            if (index > -1) {
                selectedRelationsIds.splice(index, 1);
            }
            _this._saveSelectedRelations(selectedRelationsIds)
            _this._checkAndToggleExportButtonDisplay();
            _this._updateMapSidebarContent();
            _this.handleRelationHighlightForSelection();
        });

        $(document).on('relationsCleared', function (event, options) {
            _this._checkAndToggleExportButtonDisplay();
            _this._updateMapSidebarContent();
            _this.handleRelationHighlightForSelection();
        });
    },

    _checkAndToggleExportButtonDisplay: function () {
        console.log(this._getSelectedRelations());
        if (this._getSelectedRelations().length > 0) {
            this.pgisMap.showLinkButton(this.pgisMap.linkButtons.exportRelationsWithId);
        } else {
            this.pgisMap.hideLinkButton(this.pgisMap.linkButtons.exportRelationsWithId);
        }
    },

    _getSelectedRelations: function () {
        return (JSON.parse(localStorage.getItem(this._localStorageKey)) || []);
    },

    _saveSelectedRelations: function (selectedRelations) {
        localStorage.setItem(this._localStorageKey, JSON.stringify(selectedRelations));
    },

    _updateMapSidebarContent: function () {
        if (this.pgisMap.sidebar.isVisible()) {
            MapHelpers.setSidebarContentToLastClickedRelation(
                this.pgisMap,
                this._getSelectedRelations()
            )
        }
    }
};
