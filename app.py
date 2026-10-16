from flask import Flask, render_template
from extensions import db
from models import Usuario, Task
import os

def formatar_tarefa(tarefa):
    tarefa_dicionario = {
        "id" : tarefa.task_id,
        "titulo" : tarefa.name_task,
        "descricao" : tarefa.descricao,
        "status" : tarefa.status,
        "prazo" : tarefa.deadline.isoformat(),
        "prioridade" : tarefa.prioridade,
        "responsavel" : tarefa.receiver.username
        
    }
    
    return tarefa_dicionario

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'wake_up_call.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH

db.init_app(app)

@app.route("/")
def inicio():
    return "<h1>WakeUp-Call</h1><p>Projeto iniciado com sucesso!</p>"

@app.route("/tarefas")
def listar_tarefas():
    tarefas = Task.query.all()
    
    tarefas_formatadas = []
    
    for tarefa in tarefas:
        tarefas_formatadas.append(formatar_tarefa(tarefa))
    
    return render_template("index.html", tarefas=tarefas_formatadas, dados_ficticios=False)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)