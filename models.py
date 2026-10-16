from extensions import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique = True, nullable = False)
    senha = db.Column(db.String(250), nullable = False)
    funcao = db.Column(db.String(20), default = 'membro', nullable = False)
    tasks_criadas = db.relationship('Task', foreign_keys = 'Task.create_by', backref = 'creator', lazy = True)
    tasks_compartilhadas = db.relationship('Task', foreign_keys = 'Task.shared_with', backref = 'receiver', lazy = True)
    
class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key = True)
    name_task = db.Column(db.String(200), nullable = False)
    descricao = db.Column(db.Text, nullable = False)
    status = db.Column(db.String(20), default = 'A Fazer', nullable = False)
    deadline = db.Column(db.Date, nullable = False)
    prioridade = db.Column(db.String(20), nullable = False)
    create_by = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable = False)
    shared_with = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable = False)