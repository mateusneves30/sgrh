from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_session import Session
from models import db, User, ProfissaoCargo, Pessoa, FolhaPgto, Capacitacao
from routes.pessoa_routes import pessoa_bp
from routes.profissao_routes import profissao_bp
from routes.capacitacao_routes import capacitacao_bp
from routes.folha_routes import folha_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sgrh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ifto'

# Configuração da sessão
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('lista_pessoa'))
    else:
        return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        flash('Logado com sucesso!', 'success')
        return redirect(url_for('lista_pessoa'))
    else:
        flash('Usuário ou senha incorretos!', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout efetuado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not User.validate_email(email):
            flash('E-mail inválido!', 'danger')
            return redirect(url_for('cadastrar'))
        novo_user = User(username=username, email=email)
        novo_user.set_password(password)
        db.session.add(novo_user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('cadastrar.html')

@app.route('/lista_pessoa')
@login_required
def lista_pessoa():
    pessoas = Pessoa.query.all()
    profissoes = ProfissaoCargo.query.all()
    capacitacoes = Capacitacao.query.all()
    folhas_pagamento = FolhaPgto.query.all()
    return render_template(
        'lista_pessoa.html',
        pessoas=pessoas,
        profissoes=profissoes,
        capacitacoes=capacitacoes,
        folhas_pagamento=folhas_pagamento
    )

@app.route('/detalhes_pessoa/<int:pessoa_id>')
@login_required
def detalhes_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    return jsonify({
        "id": pessoa.id,
        "nome": pessoa.nome,
        "cpf": pessoa.cpf,
        "data_nascimento": pessoa.data_nascimento.strftime('%d/%m/%Y'),
        "endereco": pessoa.endereco,
        "profissoes": [
            {"titulo": p.titulo, "salario_base": p.salario_base} for p in pessoa.profissoes
        ],
        "capacitacoes": [
            {"titulo": c.titulo, "instituicao": c.instituicao} for c in pessoa.capacitacoes
        ],
        "folhas_pagamento": [
            {"mes_referencia": f.mes_referencia, "salario_liquido": f.salario_liquido} for f in pessoa.folhas_pagamento
        ]
    })

# Registrar os Blueprints
app.register_blueprint(pessoa_bp)
app.register_blueprint(profissao_bp)
app.register_blueprint(capacitacao_bp)
app.register_blueprint(folha_bp)

if __name__ == '__main__':
    app.run(debug=True)
