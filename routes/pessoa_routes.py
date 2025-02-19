from flask import Blueprint, request, redirect, url_for, flash, jsonify
from datetime import datetime
from flask_login import login_required
from models import db, Pessoa

pessoa_bp = Blueprint('pessoa', __name__)

@pessoa_bp.route('/cadastrar_pessoa', methods=['POST'])
@login_required
def cadastrar_pessoa():
    nome = request.form['nome']
    cpf = request.form['cpf']
    data_nascimento_str = request.form['data_nascimento']
    endereco = request.form['endereco']
    telefone = request.form['telefone']

    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
    except ValueError:
        flash(f'Formato de data inválido! Use dd/mm/aaaa', 'danger')
        return redirect(url_for('lista_pessoa'))

    nova_pessoa = Pessoa(
        nome=nome,
        cpf=cpf,
        data_nascimento=data_nascimento,
        endereco=endereco,
        telefone=telefone
    )
    db.session.add(nova_pessoa)
    db.session.commit()

    flash(f'{nome} adicionado(a) com sucesso.', 'success')
    return redirect(url_for('lista_pessoa'))

@pessoa_bp.route('/editar_pessoa/<int:pessoa_id>', methods=['POST'])
@login_required
def editar_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    pessoa.nome = request.form['nome']
    pessoa.cpf = request.form['cpf']
    data_nascimento_str = request.form['data_nascimento']

    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
        pessoa.data_nascimento = data_nascimento
    except ValueError:
        flash(f'Formato de data inválido! Use dd/mm/aaaa', 'danger')
        return redirect(url_for('lista_pessoa'))

    pessoa.endereco = request.form['endereco']
    pessoa.telefone = request.form['telefone']

    db.session.commit()
    flash('Dados da pessoa atualizados com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))

@pessoa_bp.route('/deletar_pessoa/<int:pessoa_id>', methods=['POST'])
@login_required
def deletar_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    nome = pessoa.nome

    # Remover relações N:N (folhas de pagamento) e deletar folhas de pagamento associadas
    for folha in pessoa.folhas_pagamento:
        db.session.delete(folha)

    # Remover relações 1:N (profissões e capacitações)
    for profissao in pessoa.profissoes:
        db.session.delete(profissao)

    for capacitacao in pessoa.capacitacoes:
        db.session.delete(capacitacao)

    # Remover a pessoa
    db.session.delete(pessoa)
    db.session.commit()

    flash(f'{nome} removido(a) com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))
