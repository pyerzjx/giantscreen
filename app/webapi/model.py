from utils.dbutils import db


class Datasource(db.Model):
    __tablename__ = 'datasource'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    source_name = db.Column(db.String(255))
    type = db.Column(db.String(255), nullable=False)
    connect = db.Column(db.String(255), nullable=False)
    account = db.Column(db.String(255))
    passwd = db.Column(db.String(255))
    remark = db.Column(db.String(255))
    flag = db.Column(db.Integer, nullable=False, default=1)


class Cwebapi(db.Model):
    __tablename__ = 'webapi'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    api_name = db.Column(db.String(255))
    api = db.Column(db.String(255),nullable=False)
    params = db.Column(db.String(255))
    remark = db.Column(db.String(255))
    deal_params = db.Column(db.String(255))
    flag = db.Column(db.Integer,nullable=False,default=1)
    status = db.Column(db.Integer,nullable=False,default=1)
    datasource_id = db.Column(db.Integer,db.ForeignKey('datasource.id'))
    datasource = db.relationship('Datasource')
    sql_view = db.Column(db.Text,nullable=False)
    cache_time = db.Column(db.Integer,default=0)


