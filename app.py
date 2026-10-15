from flask import Flask
from extensions import db
from models import Usuario, Task
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'wake_up_call.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH

db.init_app(app)

@app.route("/")
def inicio():
    return "<h1>WakeUp-Call</h1><p>Projeto iniciado com sucesso!</p>"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)