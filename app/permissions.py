from app import GisApp, db
from flask.ext.principal import Principal, Permission, ActionNeed, identity_loaded, UserNeed, identity_changed, Identity, AnonymousIdentity

principals = Principal(GisApp)
admin_points = Permission(ActionNeed('admin_points'))
admin_points_new = Permission(ActionNeed('admin_points_new'))
admin_points_create = Permission(ActionNeed('admin_points_create'))
admin_points_edit = Permission(ActionNeed('admin_points_edit'))
admin_points_update = Permission(ActionNeed('admin_points_update'))
admin_points_delete = Permission(ActionNeed('admin_points_delete'))


admin_powerlines = Permission(ActionNeed('admin_powerlines'))
admin_powerlines_new = Permission(ActionNeed('admin_powerlines_new'))
admin_powerlines_create = Permission(ActionNeed('admin_powerlines_create'))
admin_powerlines_edit = Permission(ActionNeed('admin_powerlines_edit'))
admin_powerlines_update = Permission(ActionNeed('admin_powerlines_update'))
admin_powerlines_delete = Permission(ActionNeed('admin_powerlines_delete'))
