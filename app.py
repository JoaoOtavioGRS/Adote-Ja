# app.py - CRUD de Animais com Flask, SQLAlchemy e Bootstrap
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuração do MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/adote_ja'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

# Modelo de Animal
class Animal(db.Model):
    __tablename__ = 'animais'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.Enum('Cachorro', 'Gato'), nullable=False)
    raca = db.Column(db.String(100))
    cor = db.Column(db.String(50))
    sexo = db.Column(db.Enum('Macho', 'Fêmea'))
    idade_aproximada = db.Column(db.String(50))
    vacinado = db.Column(db.Boolean, default=False)
    castrado = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', backref=db.backref('animais', lazy=True))

@app.route('/')
def home():
    if 'usuario_id' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario_id' not in session:
        flash('Faça login para acessar seu perfil.', 'warning')
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.telefone = request.form['telefone']
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('home'))

    return render_template('editar_perfil.html', usuario=usuario)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        telefone = request.form['telefone']
        existe = Usuario.query.filter_by(email=email).first()
        if existe:
            flash('E-mail já cadastrado.', 'danger')
            return redirect(url_for('cadastrar'))
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash, telefone=telefone)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('cadastrar.html')

@app.route('/cadastrar_animal', methods=['GET', 'POST'])
def cadastrar_animal():
    if 'usuario_id' not in session:
        flash('Faça login para cadastrar um animal.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form['raca']
        cor = request.form.get('cor', '')
        sexo = request.form['sexo']
        idade_aproximada = request.form.get('idade_aproximada', '')
        vacinado = True if request.form['vacinado'] == 'Sim' else False
        castrado = True if request.form['castrado'] == 'Sim' else False
        usuario_id = session['usuario_id']

        novo_animal = Animal(
            nome=nome,
            especie=especie,
            raca=raca,
            cor=cor,
            sexo=sexo,
            idade_aproximada=idade_aproximada,
            vacinado=vacinado,
            castrado=castrado,
            usuario_id=usuario_id
        )
        db.session.add(novo_animal)
        db.session.commit()
        flash('Animal cadastrado com sucesso!', 'success')
        return redirect(url_for('home'))
    return render_template('cadastrar_animal.html')

@app.route('/listar_animais', methods=['GET'])
def listar_animais():
    if 'usuario_id' not in session:
        flash('Faça login para acessar a listagem.', 'warning')
        return redirect(url_for('login'))

    especie = request.args.get('especie')
    raca = request.args.get('raca')
    sexo = request.args.get('sexo')
    vacinado = request.args.get('vacinado')
    castrado = request.args.get('castrado')

    query = Animal.query

    if especie:
        query = query.filter(Animal.especie == especie)
    if raca:
        query = query.filter(Animal.raca == raca)
    if sexo:
        query = query.filter(Animal.sexo == sexo)
    if vacinado:
        if vacinado == 'Sim':
            query = query.filter(Animal.vacinado.is_(True))
        elif vacinado == 'Não':
            query = query.filter(Animal.vacinado.is_(False))
    if castrado:
        if castrado == 'Sim':
            query = query.filter(Animal.castrado.is_(True))
        elif castrado == 'Não':
            query = query.filter(Animal.castrado.is_(False))

    animais = query.all()

    return render_template('listar_animais.html', animais=animais)

if __name__ == '__main__':
    app.run(debug=True)
