import os

basedir = os.path.abspath(os.path.dirname(__file__))


WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost:5432/gis'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
GOOGLE_CLIENT_ID='498377614550-0q8d0e0fott6qm0rvgovd4o04f8krhdb.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='OcxQ8mW4eSizqjchgpwKArHH'
ACTION_PERMISSIONS=['admin_points', 'admin_points_new', 'admin_points_create', 'admin_points_edit', 'admin_points_update', 'admin_points_delete', 'admin_powerlines', 'admin_powerlines_new', 'admin_powerlines_create', 'admin_powerlines_edit', 'admin_powerlines_update', 'admin_powerlines_delete']
