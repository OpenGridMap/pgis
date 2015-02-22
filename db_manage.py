#!/home/headshota/miniconda3/envs/gisenv/bin/python
from app import db
from app import GisApp
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
# v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
# tmp_module = imp.new_module('old_model')
# old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# exec(old_model, tmp_module.__dict__)
# script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
# open(migration, "wt").write(script)
# api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# print('New migration saved as ' + migration)
# print('Current database version: ' + str(v))

migrate = Migrate(GisApp, db)

manager = Manager(GisApp)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()