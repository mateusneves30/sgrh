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
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

    pessoa = db.relationship('Pessoa', back_populates='user')

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



class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    user = db.relationship('User', back_populates='pessoa', uselist=False)
    profissao = db.relationship('ProfissaoCargo', back_populates='pessoa', uselist=False)
    folhas_pagamento = db.relationship('FolhaPgto', back_populates='pessoa', cascade="all, delete-orphan")
    capacitacoes = db.relationship('Capacitacao', back_populates='pessoa', cascade="all, delete-orphan")


class ProfissaoCargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    salario_base = db.Column(db.Float, nullable=False)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

    pessoa = db.relationship('Pessoa', back_populates='profissao')


class FolhaPgto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    mes_referencia = db.Column(db.String(7), nullable=False)  # formato: 'YYYY-MM'
    salario_bruto = db.Column(db.Float, nullable=False)
    descontos = db.Column(db.Float, nullable=False)
    salario_liquido = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow)

    pessoa = db.relationship('Pessoa', back_populates='folhas_pagamento')


class Capacitacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    instituicao = db.Column(db.String(150), nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    data_conclusao = db.Column(db.Date, nullable=False)

    pessoa = db.relationship('Pessoa', back_populates='capacitacoes')
