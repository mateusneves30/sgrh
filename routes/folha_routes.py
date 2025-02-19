from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from models import db, FolhaPgto, Pessoa

folha_bp = Blueprint('folha', __name__)

@folha_bp.route('/cadastrar_folha/<int:pessoa_id>', methods=['POST'])
@login_required
def cadastrar_folha(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    mes_referencia = request.form['mes_referencia']
    salario_bruto = float(request.form['salario_bruto'])
    descontos = float(request.form['descontos'])
    salario_liquido = salario_bruto - descontos

    nova_folha = FolhaPgto(
        mes_referencia=mes_referencia,
        salario_bruto=salario_bruto,
        descontos=descontos,
        salario_liquido=salario_liquido
    )
    db.session.add(nova_folha)

    nova_folha.pessoas.append(pessoa)
    db.session.commit()

    flash(f'Folha de pagamento para {mes_referencia} adicionada com sucesso para {pessoa.nome}.', 'success')
    return redirect(url_for('lista_pessoa'))

@folha_bp.route('/editar_folha/<int:folha_id>', methods=['POST'])
@login_required
def editar_folha(folha_id):
    folha = FolhaPgto.query.get_or_404(folha_id)
    folha.mes_referencia = request.form['mes_referencia']
    folha.salario_bruto = float(request.form['salario_bruto'])
    folha.descontos = float(request.form['descontos'])
    folha.salario_liquido = folha.salario_bruto - folha.descontos

    db.session.commit()
    flash('Folha de pagamento editada com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))

@folha_bp.route('/deletar_folha/<int:folha_id>', methods=['POST'])
@login_required
def deletar_folha(folha_id):
    folha = FolhaPgto.query.get_or_404(folha_id)
    db.session.delete(folha)
    db.session.commit()
    flash('Folha de pagamento removida com sucesso!', 'success')
    return redirect(url_for('lista_pessoa'))
