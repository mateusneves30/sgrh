from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_session import Session
from models import db, User, ProfissaoCargo, Pessoa

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
login_manager.login_view = 'login'  # Redireciona para login se o usuário não estiver autenticado
login_manager.login_message_category = "warning"  # Categoria do flash para login


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/form_profissao', methods=['GET', 'POST'])
@login_required
def form_profissao():
    titulo = request.form['titulo']
    descricao = request.form['descricao']
    salario_base = float(request.form['salario_base'])

    nova_profissao = ProfissaoCargo(titulo=titulo, descricao=descricao, salario_base=salario_base)
    db.session.add(nova_profissao)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": nova_profissao.id,
        "titulo": nova_profissao.titulo,
        "descricao": nova_profissao.descricao,
        "salario_base": nova_profissao.salario_base
    })


@app.route('/lista_profissao')
@login_required
def lista_profissao():
    profissoes = ProfissaoCargo.query.all()
    return render_template('lista_profissao.html', titulo='Sistema de Gestão de Recursos Humanos',
                           profissoes=profissoes)


from datetime import datetime

@app.route('/form_pessoa', methods=['POST'])
@login_required
def form_pessoa():
    nome = request.form['nome']
    cpf = request.form['cpf']
    data_nascimento_str = request.form['data_nascimento']
    endereco = request.form['endereco']
    profissao_id = request.form.get('profissao_id', type=int)

    if not profissao_id or not ProfissaoCargo.query.get(profissao_id):
        return jsonify({"success": False, "message": "Profissão inválida!"}), 400

    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "message": "Formato de data inválido! Use dd/mm/aaaa"}), 400

    nova_pessoa = Pessoa(
        nome=nome,
        cpf=cpf,
        data_nascimento=data_nascimento,
        endereco=endereco,
        profissao_id=profissao_id
    )
    db.session.add(nova_pessoa)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": nova_pessoa.id,
        "nome": nova_pessoa.nome,
        "data_nascimento": nova_pessoa.data_nascimento.strftime("%d/%m/%Y"),
        "cpf": nova_pessoa.cpf,
        "endereco": nova_pessoa.endereco,
        "profissao": nova_pessoa.profissao.titulo
    })


@app.route('/lista_pessoa')
@login_required
def lista_pessoa():
    pessoas = Pessoa.query.all()
    profissoes = ProfissaoCargo.query.all()
    return render_template('lista_pessoa.html', titulo='Sistema de Gestão de Recursos Humanos', pessoas=pessoas, profissoes=profissoes)


@app.route('/')
def login():
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


if __name__ == '__main__':
    app.run(debug=True)
