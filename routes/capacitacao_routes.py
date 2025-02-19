from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from models import db, Capacitacao, Pessoa

capacitacao_bp = Blueprint('capacitacao', __name__)

@capacitacao_bp.route('/cadastrar_capacitacao/<int:pessoa_id>', methods=['POST'])
@login_required
def cadastrar_capacitacao(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    titulo = request.form['titulo']
    instituicao = request.form['instituicao']
    carga_horaria = int(request.form['carga_horaria'])
    data_conclusao = datetime.strptime(request.form['data_conclusao'], '%Y-%m-%d').date()

    nova_capacitacao = Capacitacao(
        titulo=titulo, instituicao=instituicao, carga_horaria=carga_horaria,
        data_conclusao=data_conclusao, pessoa=pessoa
    )
    db.session.add(nova_capacitacao)
    db.session.commit()

    flash(f'Capacitação {titulo} adicionada com sucesso para {pessoa.nome}.', 'success')
    return redirect(url_for('lista_pessoa'))

@capacitacao_bp.route('/editar_capacitacao/<int:capacitacao_id>', methods=['POST'])
@login_required
def editar_capacitacao(capacitacao_id):
    capacitacao = Capacitacao.query.get_or_404(capacitacao_id)
    capacitacao.titulo = request.form['titulo']
    capacitacao.instituicao = request.form['instituicao']
    capacitacao.carga_horaria = int(request.form['carga_horaria'])
    data_conclusao_str = request.form['data_conclusao']

    try:
        data_conclusao = datetime.strptime(data_conclusao_str, "%Y-%m-%d").date()
        capacitacao.data_conclusao = data_conclusao
    except ValueError:
        flash(f'Formato de data inválido! Use dd/mm/aaaa', 'danger')
        return redirect(url_for('lista_pessoa'))

    db.session.commit()
    flash('Capacitação editada com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))

@capacitacao_bp.route('/deletar_capacitacao/<int:capacitacao_id>', methods=['POST'])
@login_required
def deletar_capacitacao(capacitacao_id):
    capacitacao = Capacitacao.query.get_or_404(capacitacao_id)
    db.session.delete(capacitacao)
    db.session.commit()
    flash('Capacitação removida com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))
