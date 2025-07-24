from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/adote_ja'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Pasta para uploads
app.config['UPLOAD_FOLDER_USUARIO'] = os.path.join('static', 'fotos_perfil')
os.makedirs(app.config['UPLOAD_FOLDER_USUARIO'], exist_ok=True)
app.config['UPLOAD_FOLDER_ANIMAL'] = os.path.join('static', 'uploads/img_animais/')
os.makedirs(app.config['UPLOAD_FOLDER_ANIMAL'], exist_ok=True)

db = SQLAlchemy(app)

# MODELOS

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    senha = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(200))  # caminho foto opcional
    animais = db.relationship('Animal', backref='usuario', lazy=True)

class Animal(db.Model):
    __tablename__ = 'animais'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(100))
    sexo = db.Column(db.String(10))
    vacinado = db.Column(db.Boolean, default=False)
    castrado = db.Column(db.Boolean, default=False)
    telefone_contato = db.Column(db.String(20))
    foto = db.Column(db.String(200))  # caminho foto animal
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

# ROTAS

# Rota para cadastro de usuário, com foto opcional
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form.get('telefone')
        senha = request.form['senha']
        foto_file = request.files.get('foto')

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'danger')
            return redirect(url_for('cadastrar'))

        foto_filename = None
        if foto_file and foto_file.filename != '':
            foto_filename = secure_filename(foto_file.filename)
            foto_file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

        senha_hash = generate_password_hash(senha)

        novo_usuario = Usuario(nome=nome, email=email, telefone=telefone, senha=senha_hash, foto=foto_filename)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastrar.html')

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
            flash('E-mail ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def home():
    session['usuario_id'] = 1
    if 'usuario_id' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('perfil.html', usuario=usuario)

from PIL import Image
from werkzeug.utils import secure_filename
import os

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.telefone = request.form.get('telefone')

        foto = request.files.get('foto')
        if foto and foto.filename:
            nome_foto = secure_filename(foto.filename)
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER_USUARIO'], nome_foto)
            foto.save(caminho_foto)
            usuario.foto = nome_foto
        # Se não enviar nova foto, mantém a foto atual (não altera usuario.foto)

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('editar_perfil'))

    return render_template('editar_perfil.html', usuario=usuario)


# Rota cadastrar animal com upload de foto
from PIL import Image

@app.route('/cadastrar_animal', methods=['GET', 'POST'])
def cadastrar_animal():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form.get('raca')
        sexo = request.form.get('sexo')
        vacinado = request.form.get('vacinado') == 'Sim'
        castrado = request.form.get('castrado') == 'Sim'
        foto_file = request.files.get('foto')

        foto_filename = None
        if foto_file and foto_file.filename != '':
            foto_filename = secure_filename(foto_file.filename)

            # Abrir imagem com Pillow
            imagem = Image.open(foto_file)

            # Redimensionar para 400x400
            imagem = imagem.resize((400, 400), Image.Resampling.LANCZOS)

            # Salvar na pasta configurada
            caminho = os.path.join(app.config['UPLOAD_FOLDER_ANIMAL'], foto_filename)
            imagem.save(caminho)

        novo_animal = Animal(
            nome=nome,
            especie=especie,
            raca=raca,
            sexo=sexo,
            vacinado=vacinado,
            castrado=castrado,
            usuario_id=session['usuario_id'],
            foto=foto_filename
        )
        db.session.add(novo_animal)
        db.session.commit()
        flash('Animal cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_animais'))

    return render_template('cadastrar_animal.html')

@app.route('/listar_animais')
def listar_animais():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Aqui pode aplicar filtros, para simplificar lista tudo
    animais = Animal.query.all()
    return render_template('listar_animais.html', animais=animais)

@app.route('/editar_animal/<int:id>', methods=['GET', 'POST'])
def editar_animal(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    animal = Animal.query.get_or_404(id)
    if animal.usuario_id != session['usuario_id']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('listar_animais'))

    if request.method == 'POST':
        animal.nome = request.form['nome']
        animal.especie = request.form['especie']
        animal.raca = request.form.get('raca')
        animal.sexo = request.form.get('sexo')
        animal.vacinado = request.form.get('vacinado') == 'Sim'
        animal.castrado = request.form.get('castrado') == 'Sim'
        animal.telefone_contato = request.form.get('telefone_contato')

        foto_file = request.files.get('foto')
        if foto_file and foto_file.filename != '':
            foto_filename = secure_filename(foto_file.filename)
            foto_file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
            animal.foto = foto_filename

        db.session.commit()
        flash('Animal atualizado com sucesso!', 'success')
        return redirect(url_for('listar_animais'))

    return render_template('editar_animal.html', animal=animal)

@app.route('/excluir_animal/<int:id>', methods=['POST'])
def excluir_animal(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    animal = Animal.query.get_or_404(id)
    if animal.usuario_id != session['usuario_id']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('listar_animais'))

    db.session.delete(animal)
    db.session.commit()
    flash('Animal excluído com sucesso!', 'success')
    return redirect(url_for('listar_animais'))

if __name__ == '__main__':
    app.run(debug=True)
