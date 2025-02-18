from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from models import db, ProfissaoCargo, Pessoa

profissao_bp = Blueprint('profissao', __name__)

@profissao_bp.route('/cadastrar_profissao/<int:pessoa_id>', methods=['POST'])
@login_required
def cadastrar_profissao(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    titulo = request.form['titulo']
    salario_base = float(request.form['salario_base'])

    nova_profissao = ProfissaoCargo(titulo=titulo, salario_base=salario_base, pessoa=pessoa)
    db.session.add(nova_profissao)
    db.session.commit()

    flash(f'Profissão {titulo} adicionada com sucesso para {pessoa.nome}.', 'success')
    return redirect(url_for('lista_pessoa'))

@profissao_bp.route('/editar_profissao/<int:profissao_id>', methods=['POST'])
@login_required
def editar_profissao(profissao_id):
    profissao = ProfissaoCargo.query.get_or_404(profissao_id)
    profissao.titulo = request.form['titulo']
    profissao.salario_base = float(request.form['salario_base'])

    db.session.commit()
    flash('Profissão editada com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))

@profissao_bp.route('/remover_profissao/<int:profissao_id>', methods=['POST'])
@login_required
def remover_profissao(profissao_id):
    profissao = ProfissaoCargo.query.get_or_404(profissao_id)
    db.session.delete(profissao)
    db.session.commit()
    flash('Profissão removida com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))
