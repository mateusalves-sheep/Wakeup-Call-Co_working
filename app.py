from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return "<h1>WakeUp-Call</h1><p>Projeto iniciado com sucesso!</p>"

if __name__ == "__main__":
    app.run(debug=True)