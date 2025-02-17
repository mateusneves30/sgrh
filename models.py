from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_email(email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False


# Tabela de associação para relação N:M entre Pessoa e Capacitação
pessoa_capacitacao = db.Table(
    'pessoa_capacitacao',
    db.Column('pessoa_id', db.Integer, db.ForeignKey('pessoa.id'), primary_key=True),
    db.Column('capacitacao_id', db.Integer, db.ForeignKey('capacitacao.id'), primary_key=True)
)

# Tabela de associação para relação N:M entre Pessoa e Profissão
pessoa_profissao = db.Table(
    'pessoa_profissao',
    db.Column('pessoa_id', db.Integer, db.ForeignKey('pessoa.id'), primary_key=True),
    db.Column('profissao_id', db.Integer, db.ForeignKey('profissao_cargo.id'), primary_key=True)
)


class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)

    # Relacionamento 1:N (Uma pessoa pode ter várias profissões)
    profissoes = db.relationship('ProfissaoCargo', secondary='pessoa_profissao', back_populates='pessoas')

    # Relacionamento 1:N (Uma pessoa pode ter várias folhas de pagamento)
    folhas_pagamento = db.relationship('FolhaPgto', back_populates='pessoa', cascade="all, delete-orphan")

    # Relacionamento N:M (Uma pessoa pode estar em várias capacitações)
    capacitacoes = db.relationship('Capacitacao', secondary=pessoa_capacitacao, back_populates='pessoas')


class ProfissaoCargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    salario_base = db.Column(db.Float, nullable=False)

    # Relacionamento N:1 (Múltiplas pessoas podem ter a mesma profissão)
    pessoas = db.relationship('Pessoa', secondary='pessoa_profissao', back_populates='profissoes')


class FolhaPgto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    mes_referencia = db.Column(db.String(7), nullable=False)  # formato: 'YYYY-MM'
    salario_bruto = db.Column(db.Float, nullable=False)
    descontos = db.Column(db.Float, nullable=False)
    salario_liquido = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento N:1 (Cada folha de pagamento pertence a uma única pessoa)
    pessoa = db.relationship('Pessoa', back_populates='folhas_pagamento')


class Capacitacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    instituicao = db.Column(db.String(150), nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    data_conclusao = db.Column(db.Date, nullable=False)

    # Relacionamento N:M (Uma capacitação pode ter várias pessoas inscritas)
    pessoas = db.relationship('Pessoa', secondary=pessoa_capacitacao, back_populates='capacitacoes')
