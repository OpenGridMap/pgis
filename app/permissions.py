from app import GisApp, db
from flask.ext.principal import Principal, Permission, ActionNeed, identity_loaded, UserNeed, identity_changed, Identity, AnonymousIdentity

principals = Principal(GisApp)
permissions = {}
action_permissions = GisApp.config.get('ACTION_PERMISSIONS')

for action_permission in action_permissions:
    permissions[action_permission] = Permission(ActionNeed(action_permission))

locals().update(permissions)
