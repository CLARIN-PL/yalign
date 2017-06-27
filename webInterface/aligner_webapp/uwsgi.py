import os
from workq import db
from alignerwebapp.webapp import app

work_db = '/opt/aligner/data/db'
models = '/opt/aligner/data/models'
data = '/opt/aligner/data/data'

if not os.path.exists(work_db):
    db.init_db(work_db)
if not os.path.exists(data):
    os.mkdir(data)
app.config.update(
    work_db=work_db,
    yalign_models=models,
    data_path=data
)
application = app.wsgi_app
