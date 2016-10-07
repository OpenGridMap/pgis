

from app import GisGeneratorApp
from app.controllers.transnet_controller import TransnetController


@GisGeneratorApp.route('/transnet/export_cim')
def transnet_export_cim():
    controller = TransnetController()
    return controller.export_cim()


@GisGeneratorApp.route('/transnet/export_cim_countries')
def transnet_export_cim_countries():
    controller = TransnetController()
    return controller.export_cim_countries()
