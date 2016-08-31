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

  init: function(pgisMap) {
    this.pgisMap = pgisMap;
    this._bindRelationSelectionEvents();
    var _this = this;
    this.pgisMap.addLinkButton({
      ref: 'exportRelationsWithId',
      text: 'Export selected relations',
      onclick: _this.redirectToExport()
    });
    this._checkAndToggleExportButtonDisplay();

    return this;
  },

  clearRelations: function() {
    localStorage.removeItem(this._localStorageKey);
  },

  redirectToExport: function() {
    var _this = this;
    return function() {
      window.open(
        '/relations/export?ids=' + _this._getSelectedRelations().join(','),
        '_blank'
      );
    }
  },

  handleRelationHighlightForSelection: function() {
    var _this = this;
    this.pgisMap.overlayLayers.relations.layer.eachLayer(function(relationFeatureLayer) {
      // if selected, add selectionStyle.
      if(_this._getSelectedRelations().indexOf(relationFeatureLayer.relation.id.toString()) > -1) {
        relationFeatureLayer.highlightForExport();
      } else {
        relationFeatureLayer.removeHighlightForExport();
      }
    });
  },

  _bindRelationSelectionEvents: function() {
    var _this = this;

    $(document).on('click', '.add-relation-to-selection', function() {
      $(document).trigger('relationSelected', {
        relationId: $(this).attr('data-relation-id')
      });
    });

    $(document).on('click', '.remove-relation-from-selection', function() {
      $(document).trigger('relationUnselected', {
        relationId: $(this).attr('data-relation-id')
      });
    });

    $(document).on('click', '.clear-relation-selection', function() {
      _this.clearRelations();
      $(document).trigger('relationsCleared');
    });

    $(document).on('click', '.export-relation-selection', function() {
      _this.redirectToExport()();
    });

    $(document).on('relationSelected', function(event, options) {
      selectedRelationsIds = _this._getSelectedRelations(); // from local storage
      if(selectedRelationsIds.indexOf(options.relationId) > -1) {
        console.log("Relation already selected");
      } else {
        selectedRelationsIds.push(options.relationId)
        _this._saveSelectedRelations(selectedRelationsIds);
      }
      _this._checkAndToggleExportButtonDisplay();
      _this._updateMapSidebarContent();
      _this.handleRelationHighlightForSelection();
    });

    $(document).on('relationUnselected', function(event, options) {
      selectedRelationsIds = _this._getSelectedRelations(); // from local storage
      index = selectedRelationsIds.indexOf(options.relationId)
      if(index > -1) {
        selectedRelationsIds.splice(index, 1);
      }
      _this._saveSelectedRelations(selectedRelationsIds)
      _this._checkAndToggleExportButtonDisplay();
      _this._updateMapSidebarContent();
      _this.handleRelationHighlightForSelection();
    });

    $(document).on('relationsCleared', function(event, options) {
      _this._checkAndToggleExportButtonDisplay();
      _this._updateMapSidebarContent();
      _this.handleRelationHighlightForSelection();
    });
  },

  _checkAndToggleExportButtonDisplay: function() {
    console.log(this._getSelectedRelations());
    if(this._getSelectedRelations().length > 0) {
      this.pgisMap.showLinkButton(this.pgisMap.linkButtons.exportRelationsWithId);
    } else {
      this.pgisMap.hideLinkButton(this.pgisMap.linkButtons.exportRelationsWithId);
    }
  },

  _getSelectedRelations: function() {
    return (JSON.parse(localStorage.getItem(this._localStorageKey)) || []);
  },

  _saveSelectedRelations: function(selectedRelations) {
    localStorage.setItem(this._localStorageKey, JSON.stringify(selectedRelations));
  },

  _updateMapSidebarContent: function() {
    if(this.pgisMap.sidebar.isVisible()) {
      MapHelpers.setSidebarContentToLastClickedRelation(
        this.pgisMap,
        this._getSelectedRelations()
      )
    }
  }
};
