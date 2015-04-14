#!/usr/bin/env python3
from app import db
from app import GisApp
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(GisApp, db)

manager = Manager(GisApp)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
