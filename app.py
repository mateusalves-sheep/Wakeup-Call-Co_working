from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from models import Usuario, Task
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os

def formatar_tarefa(tarefa):
    
    if tarefa.status != "Concluída" and tarefa.deadline < date.today():
        status_exibido = "Atrasada"
    else:
        status_exibido = tarefa.status
    
    tarefa_dicionario = {
        "id" : tarefa.task_id,
        "titulo" : tarefa.name_task,
        "descricao" : tarefa.descricao,
        "status" : status_exibido,
        "prazo" : tarefa.deadline.isoformat(),
        "prioridade" : tarefa.prioridade,
        "responsavel" : tarefa.receiver.username
        
    }
    
    return tarefa_dicionario

def modificar_tarefa(tarefa):
    return (tarefa.shared_with == current_user.id or tarefa.create_by == current_user.id)

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

@app.route("/", methods=["GET","POST"])
def login():
    erros = {}
    valores = {"username" : ""}
    
    if request.method == "POST":
        username = request.form.get("username","").strip()
        senha = request.form.get("senha","")
        
        valores["username"] = username
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not username:
            erros["username"] = "Informe o nome do seu usuário."
    
        if not senha:
            erros["senha"] = "informe a sua senha."
            
        if not erros:
            if usuario and check_password_hash(usuario.senha, senha):
                login_user(usuario)
                flash("Login realizado com sucesso!")
                return redirect(url_for("listar_tarefas"))
            
            erros["senha"] = "Usuário ou senha inválidos."
            
    return render_template("login.html", erros=erros,valores=valores)

@app.route("/tarefas")
@login_required
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
            return render_template("cadastro.html", erros=erros, valores=valores)
    
        senha_hash = generate_password_hash(senha)
    
        novo_usuario = Usuario(username=username, senha=senha_hash, funcao='membro')
    
        try:
            db.session.add(novo_usuario)
            db.session.commit()
      
        except Exception:
            db.session.rollback()
            flash("Ocorreu um erro ao cadastrar o usuário. Por favor, tente novamente.")
            return render_template("cadastro.html", erros=erros, valores=valores)

        flash("Usuário cadastrado com sucesso!")
        return redirect(url_for("login"))

    return render_template("cadastro.html", erros=erros, valores=valores)

@app.route("/tarefas/nova", methods=["GET","POST"])
@login_required
def criar_tarefa():
    usuarios = Usuario.query.order_by(Usuario.username).all()
    
    if request.method == "POST":
        titulo = request.form.get("titulo","").strip()
        descricao = request.form.get("descricao","").strip()
        prazo_texto = request.form.get("prazo","")
        prioridade = request.form.get("prioridade","")
        responsavel_id = request.form.get("responsavel","")
        
        if not titulo or not descricao or not prazo_texto or not prioridade or not responsavel_id:
            flash("Preencha todos os campos.")
            return render_template("criar_tarefa.html",usuarios=usuarios)
        
        try:
            prazo = date.fromisoformat(prazo_texto)
            responsavel_id = int(responsavel_id)
        except ValueError:
            flash("Prazo ou responsável inválido.")
            return render_template("criar_tarefa.html", usuarios=usuarios)
        
        usuario_responsavel = db.session.get(Usuario, responsavel_id)
        
        if usuario_responsavel is None:
            flash("Usuário selecionado não existe")
            return render_template("criar_tarefa.html", usuarios=usuarios)
        
        
        if prioridade not in ["Alta", "Média", "Baixa"]:
            flash("Prioridade inválida.")
            return render_template("criar_tarefa.html", usuarios=usuarios)
        
        nova_tarefa = Task(
            name_task=titulo,
            descricao=descricao,
            deadline=prazo,
            prioridade=prioridade,
            create_by=current_user.id,
            shared_with=usuario_responsavel.id
        )
        
        try:
            db.session.add(nova_tarefa)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Ocorreu um erro ao criar a tarefa. Por favor, tente novamente.")
            return render_template("criar_tarefa.html", usuarios=usuarios)
        
        return redirect(url_for("listar_tarefas"))
    
    return render_template("criar_tarefa.html", usuarios=usuarios)

@app.route("/tarefas/<int:task_id>/editar", methods=["GET","POST"])
@login_required
def editar_tarefa(task_id):
    tarefa = Task.query.get_or_404(task_id)
    
    if not modificar_tarefa(tarefa):
        flash("Você não tem permissão para editar esta tarefa.")
        return redirect(url_for("listar_tarefas"))
    
    usuarios = Usuario.query.order_by(Usuario.username).all()
    
    if request.method == "POST":
        titulo = request.form.get("name_task", "").strip()
        descricao = request.form.get("descricao","").strip()
        prazo_texto = request.form.get("deadline","")
        prioridade = request.form.get("prioridade","")
        responsavel_id = request.form.get("shared_with","")
        status = request.form.get("status","")
        
        if not status:
            status = tarefa.status
        
        erros = {}
        
        if not titulo:
            erros["name_task"] = "Informe o título da tarefa."
    
        if not descricao:
            erros["descricao"] = "Informe a descrição da tarefa."
            
        try:
            prazo = date.fromisoformat(prazo_texto)
        except ValueError:
            erros["deadline"] = "Informe uma data válida."
            
        try:
            responsavel_id = int(responsavel_id)
        except (ValueError, TypeError):
            erros["shared_with"] = "Selecione um usuário válido."
            
        if prioridade not in ["Alta", "Média","Baixa"]:
            erros["prioridade"] = "Selecione uma prioridade válida."

        if status not in ["A Fazer", "Fazendo", "Concluída"]:
            erros["status"] = "Selecione um status válido."
            
        usuario_responsavel = None
        
        if "shared_with" not in erros:
            usuario_responsavel = db.session.get(Usuario, responsavel_id)
             
        if usuario_responsavel is None:
            erros["shared_with"] = "Usuário não encontrado."
            
        if erros:
            return render_template(
                    "tarefa_form.html", 
                    modo="editar", 
                    usuarios=usuarios, 
                    valores = request.form, 
                    erros=erros,
                    erro_geral=None,
                    url_excluir=url_for(
                                "excluir_tarefa",
                                task_id=tarefa.task_id
                                )
                            )
            
        tarefa.name_task = titulo
        tarefa.descricao = descricao
        tarefa.deadline = prazo
        tarefa.prioridade = prioridade
        tarefa.shared_with = responsavel_id
        tarefa.status = status
        
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            
            return render_template(
                    "tarefa_form.html", 
                    modo="editar", 
                    usuarios=usuarios, 
                    valores = request.form, 
                    erros={},
                    erro_geral="Não foi possível fazer alterações",
                    url_excluir=url_for(
                                "excluir_tarefa",
                                task_id=tarefa.task_id
                                )
                            )
            
        flash("Tarefa atualizada com sucesso.")
        return redirect(url_for("listar_tarefas"))
    
    return render_template(
            "tarefa_form.html", 
            modo="editar", 
            usuarios=usuarios, 
            valores = tarefa, 
            erros={},
            erro_geral=None,
            url_excluir=url_for(
                        "excluir_tarefa",
                        task_id=tarefa.task_id
                        )
                    )
    
@app.route("/tarefas/<int:task_id>/status", methods=["POST"])
@login_required
def alterar_status(task_id):
    tarefa = Task.query.get_or_404(task_id)
    
    if not modificar_tarefa(tarefa):
        flash("Você não tem permissão para alterar o status desta tarefa.")
        return redirect(url_for("listar_tarefas"))

    novo_status = request.form.get("status","")
    
    status_validos = ["A Fazer", "Fazendo", "Concluída"]
    
    if novo_status not in status_validos:
        flash("Status inválido.")
        return redirect(url_for("listar_tarefas"))
    
    tarefa.status = novo_status
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Não foi possível atualizar status.")
        return redirect(url_for("listar_tarefas"))
    
    flash("Status atualizado com sucesso.")
    return redirect(url_for("listar_tarefas"))

@app.route("/tarefas/<int:task_id>/excluir", methods=["POST"])
@login_required
def excluir_tarefa(task_id):
    tarefa = Task.query.get_or_404(task_id)
    
    if not modificar_tarefa(tarefa):
        flash("Você não tem permissão para excluir esta tarefa.")
        return redirect(url_for("listar_tarefas"))
    
    try:
        db.session.delete(tarefa)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir esta tarefa.")
        return redirect(url_for("listar_tarefas"))
    
    flash("Tarefa excluída com sucesso.")
    return redirect(url_for("listar_tarefas"))

@app.route("/contatos")
@login_required
def listar_contatos():
    contatos = Usuario.query.order_by(Usuario.username.asc()).all()
    
    return render_template("contatos.html",contatos=contatos)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta")
    return redirect(url_for("login"))
    
        
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)