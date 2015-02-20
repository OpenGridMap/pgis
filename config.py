import os

basedir = os.path.abspath(os.path.dirname(__file__))


WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost:5432/gis'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
