from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_session import Session
from models import db, User, ProfissaoCargo, Pessoa, FolhaPgto, Capacitacao

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

@app.route('/editar_pessoa/<int:pessoa_id>', methods=['POST'])
@login_required
def editar_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    pessoa.nome = request.form['nome']
    pessoa.endereco = request.form['endereco']

    # Atualizar Profissões
    profissao_ids = request.form.getlist('profissoes')
    pessoa.profissoes = ProfissaoCargo.query.filter(ProfissaoCargo.id.in_(profissao_ids)).all()

    # Atualizar Capacitações
    capacitacao_ids = request.form.getlist('capacitacoes')
    pessoa.capacitacoes = Capacitacao.query.filter(Capacitacao.id.in_(capacitacao_ids)).all()

    # Atualizar Folhas de Pagamento
    folha_ids = request.form.getlist('folhas_pagamento')
    pessoa.folhas_pagamento = FolhaPgto.query.filter(FolhaPgto.id.in_(folha_ids)).all()

    db.session.commit()
    flash('Dados da pessoa atualizados com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))

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


@app.route('/cadastrar_profissao/<int:pessoa_id>', methods=['POST'])
@login_required
def cadastrar_profissao(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    titulo = request.form['titulo']
    salario_base = request.form['salario_base']

    nova_profissao = ProfissaoCargo(titulo=titulo, salario_base=salario_base, pessoa=pessoa)
    db.session.add(nova_profissao)
    db.session.commit()

    flash(f'Profissão {titulo} adicionada com sucesso para {pessoa.nome}.', 'success')
    return redirect(url_for('lista_pessoa'))


@app.route('/cadastrar_capacitacao/<int:pessoa_id>', methods=['POST'])
@login_required
def cadastrar_capacitacao(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    titulo = request.form['titulo']
    instituicao = request.form['instituicao']
    carga_horaria = request.form['carga_horaria']
    # Converter string para objeto date
    data_conclusao_str = request.form['data_conclusao']
    data_conclusao = datetime.strptime(data_conclusao_str, '%Y-%m-%d').date()

    nova_capacitacao = Capacitacao(
        titulo=titulo,
        instituicao=instituicao,
        carga_horaria=carga_horaria,
        data_conclusao=data_conclusao,
        pessoa=pessoa
    )
    db.session.add(nova_capacitacao)
    db.session.commit()

    flash(f'Capacitação {titulo} adicionada com sucesso para {pessoa.nome}.', 'success')
    return redirect(url_for('lista_pessoa'))


@app.route('/cadastrar_folha/<int:pessoa_id>', methods=['POST'])
@login_required
def cadastrar_folha(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    mes_referencia = request.form['mes_referencia']
    salario_bruto = float(request.form['salario_bruto'])
    descontos = float(request.form['descontos'])

    salario_liquido = salario_bruto - descontos

    # Criar a folha de pagamento sem associar diretamente a pessoa
    nova_folha = FolhaPgto(
        mes_referencia=mes_referencia,
        salario_bruto=salario_bruto,
        descontos=descontos,
        salario_liquido=salario_liquido
    )
    db.session.add(nova_folha)

    # Depois, adicionar a pessoa à relação N:N
    nova_folha.pessoas.append(pessoa)
    db.session.commit()

    flash(f'Folha de pagamento para {mes_referencia} adicionada com sucesso para {pessoa.nome}.', 'success')
    return redirect(url_for('lista_pessoa'))

if __name__ == '__main__':
    app.run(debug=True)
