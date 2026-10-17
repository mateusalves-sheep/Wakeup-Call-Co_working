from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from models import Usuario, Task
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
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

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Alfajor-secreto-por5reais')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def carregar_usuario(usuario_id):
    try:
        return db.session.get(Usuario, int(usuario_id))
    except (TypeError, ValueError):
        return None

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

@app.route("/register", methods=["GET","POST"])
def cadastrar_usuario():
    
    erros = {}
    valores = {"username": ""}
    
    if request.method == "POST":
        username =  request.form.get("username","").strip()
        senha = request.form.get("senha","")
        confirmar_senha = request.form.get("confirmar_senha","") 

        valores["username"] = username
        
        if len(username) < 3:
            erros["username"] = "O nome de usuário deve ter pelo menos 3 caracteres."   
        elif len(username) > 150:
            erros["username"] = "O nome de usuário não pode ter mais de 150 caracteres."
        elif Usuario.query.filter_by(username=username).first():
            erros["username"] = "O nome de usuário já está em uso. Por favor, escolha outro."
            
        if len(senha) < 6:
            erros["senha"] = "A senha deve ter pelo menos 6 caracteres."
            
        if senha != confirmar_senha:
            erros["confirmar_senha"] = "As senhas não coincidem."
            
        if erros:
            return render_template("cadastro.html.html", erros=erros, valores=valores)
    
        senha_hash = generate_password_hash(senha)
    
        novo_usuario = Usuario(username=username, senha=senha_hash, funcao='membro')
    
        try:
            db.session.add(novo_usuario)
            db.session.commit()
      
        except Exception:
            db.session.rollback()
            flash("Ocorreu um erro ao cadastrar o usuário. Por favor, tente novamente.")
            return render_template("cadastro.html.html", erros=erros, valores=valores)

        flash("Usuário cadastrado com sucesso!")
        return redirect(url_for("inicio"))

    return render_template("cadastro.html.html", erros=erros, valores=valores)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)