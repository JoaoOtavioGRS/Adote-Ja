from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
from PIL import Image, UnidentifiedImageError
from datetime import datetime, timedelta
import os, json

EXTENSOES_PIL = {
    'jpg': 'JPEG',
    'jpeg': 'JPEG',
    'png': 'PNG',
    'gif': 'GIF',
    'bmp': 'BMP',
    'tiff': 'TIFF',
    'webp': 'WEBP',
    'jfif': 'JPEG'
}

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
# Caminho para a pasta data
DATA_DIR = os.path.abspath(os.path.join(app.root_path, 'data'))
CIDADES_DIR = os.path.join(DATA_DIR, 'cidades')

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
    estado = db.Column(db.String(2))
    cidade = db.Column(db.String(100))

class Animal(db.Model):
    __tablename__ = 'animais'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(100))
    sexo = db.Column(db.String(10))
    vacinado = db.Column(db.Integer, default=2)  # 0 = Sim, 1 = Não, 2 = Não sei
    castrado = db.Column(db.Integer, default=2)  # 0 = Sim, 1 = Não, 2 = Não sei
    telefone_contato = db.Column(db.String(20))
    foto = db.Column(db.String(200))  # caminho foto animal
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

def excluir_animais_vencidos():
    limite = datetime.utcnow() - timedelta(days=30)
    animais_vencidos = Animal.query.filter(Animal.criado_em < limite).all()

    for animal in animais_vencidos:
        if 'usuario_id' in session and session['usuario_id'] == animal.usuario_id:
            flash(f"O anúncio do animal '{animal.nome}' foi removido por estar publicado há mais de 30 dias.", 'warning')
        db.session.delete(animal)

    db.session.commit()

# Função para carregar cidades de um estado específico
def carregar_cidades(estado_sigla):
    caminho = os.path.join(DATA_DIR, f'{estado_sigla}.json')
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# ROTAS

# ROTA PARA FORMATAR NUMERO PARA WHATSAPP
@app.template_filter('formatar_telefone_whatsapp')
def formatar_telefone_whatsapp(telefone):
    if not telefone:
        return ''
    # Remove tudo que não é número
    numeros = re.sub(r'\D', '', telefone)
    # Adiciona o código do Brasil +55 caso não tenha (assumindo)
    if not numeros.startswith('55'):
        numeros = '55' + numeros
    return numeros

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
            foto_file.save(os.path.join(app.config['UPLOAD_FOLDER_USUARIO'], foto_filename))

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
            # 🔥 Adiciona a foto do usuário na sessão
            session['usuario_foto'] = usuario.foto if usuario.foto else None

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

import json

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])

    # ====== Carregar ESTADOS ======
    estados_path = os.path.join(DATA_DIR, 'estados.json')
    with open(estados_path, 'r', encoding='utf-8') as f:
        estados_lista = json.load(f)['estados']  # lista de {id, estado}

    # ====== Carregar CIDADES (mapa UF -> [nomes]) ======
    cidades_dir = os.path.join(DATA_DIR, 'cidades')
    cidades_por_estado = {}

    if os.path.isdir(cidades_dir):
        for arquivo in os.listdir(cidades_dir):
            if arquivo.endswith('.json'):
                caminho = os.path.join(cidades_dir, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # data['cidades'] é lista de { id: "UF", cidade: "Nome", ... }
                    for item in data.get('cidades', []):
                        uf = item.get('id')
                        nome = item.get('cidade')
                        if uf and nome:
                            cidades_por_estado.setdefault(uf, []).append(nome)

    # Ordenar para ficar bonito
    for uf in cidades_por_estado:
        cidades_por_estado[uf].sort(key=lambda s: s.lower())
    estados_lista.sort(key=lambda e: e['estado'].lower())

    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.telefone = request.form.get('telefone')

        # >>> Salvar ESTADO e CIDADE
        usuario.estado = (request.form.get('estado') or '').strip()
        usuario.cidade = (request.form.get('cidade') or '').strip()

        # Foto (opcional)
        foto = request.files.get('foto')
        if foto and foto.filename:
            nome_foto = secure_filename(foto.filename)
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER_USUARIO'], nome_foto)
            foto.save(caminho_foto)
            usuario.foto = nome_foto

        db.session.commit()

        # Atualiza sessão (se quiser manter)
        session['usuario_nome'] = usuario.nome
        session['usuario_foto'] = usuario.foto if usuario.foto else None

        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('editar_perfil'))

    # GET -> renderiza já com as cidades do estado atual (server-side)
    cidades_iniciais = cidades_por_estado.get(usuario.estado or '', [])

    return render_template(
        'editar_perfil.html',
        usuario=usuario,
        estados=estados_lista,                 # lista de {id, estado}
        cidades_por_estado=cidades_por_estado, # dict { "UF": ["Cidade1", ...] }
        cidades_iniciais=cidades_iniciais      # lista para pré-render no select cidade
    )

# Rota cadastrar animal com upload de foto
from PIL import Image

@app.route('/animal', methods=['GET', 'POST'])
@app.route('/animal/<int:id>', methods=['GET', 'POST'])
def cadastrar_ou_editar_animal(id=None):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    animal = None
    if id:
        animal = Animal.query.get_or_404(id)
        if animal.usuario_id != session['usuario_id']:
            flash('Acesso negado.', 'danger')
            return redirect(url_for('listar_animais'))

    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form.get('raca')
        sexo = request.form.get('sexo')
        vacinado = int(request.form.get("vacinado")) if request.form.get("vacinado") else 2
        castrado = int(request.form.get("castrado")) if request.form.get("castrado") else 2
        foto_file = request.files.get('foto')

        if animal is None:
            animal = Animal(usuario_id=session["usuario_id"])
            db.session.add(animal)

        animal.nome = nome
        animal.especie = especie
        animal.raca = raca
        animal.sexo = sexo
        animal.vacinado = vacinado
        animal.castrado = castrado

        if foto_file and foto_file.filename != '':
            try:
                imagem = Image.open(foto_file)
                if imagem.mode in ("RGBA", "P"):
                    imagem = imagem.convert("RGB")
                imagem = imagem.resize((400, 400), Image.Resampling.LANCZOS)
                foto_filename = secure_filename(foto_file.filename)
                caminho = os.path.join(app.config['UPLOAD_FOLDER_ANIMAL'], foto_filename)
                extensao = foto_filename.rsplit('.', 1)[-1].lower()
                formato_pillow = EXTENSOES_PIL.get(extensao)
                if not formato_pillow:
                    flash('Formato de imagem não suportado.', 'danger')
                    return redirect(request.url)
                imagem.save(caminho, format=formato_pillow)
                animal.foto = foto_filename
            except UnidentifiedImageError:
                flash('Formato de imagem não suportado ou arquivo inválido.', 'danger')
                return redirect(request.url)
            except OSError:
                flash('Erro ao processar a imagem: formato não suportado.', 'danger')
                return redirect(request.url)

        db.session.commit()
        flash('Animal salvo com sucesso!', 'success')
        return redirect(url_for('listar_animais'))

    # GET
    return render_template('cadastrar_editar_animal.html', animal=animal)

@app.route('/listar_animais')
def listar_animais():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Exclui anúncios antigos antes de exibir a lista
    excluir_animais_vencidos()

    # Pegando filtros enviados pela URL (GET)
    especie = request.args.get('especie')
    raca = request.args.get('raca')
    sexo = request.args.get('sexo')
    vacinado_value = request.args.get('vacinado')
    castrado_value = request.args.get('castrado')

    query = Animal.query

    # Filtro espécie
    if especie and especie.strip():
        query = query.filter(Animal.especie == especie)

    # Filtro raça
    if raca and raca.strip():
        query = query.filter(Animal.raca == raca)

    # Filtro sexo
    if sexo and sexo.strip():
        query = query.filter(Animal.sexo == sexo)

    if vacinado_value in ('0', '1', '2'):
        query = query.filter(Animal.vacinado == int(vacinado_value))

    if castrado_value in ('0', '1', '2'):
        query = query.filter(Animal.castrado == int(castrado_value))

    # Ordenação: mais recentes primeiro
    animais = query.order_by(Animal.criado_em.desc()).all()

    return render_template(
        'listar_animais.html',
        animais=animais
    )


@app.route('/meus_anuncios')
def meus_anuncios():
    if 'usuario_id' not in session:
        flash('Faça login para acessar essa página.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    anuncios = Animal.query.filter_by(usuario_id=usuario_id).order_by(Animal.criado_em.desc()).all()

    return render_template('meus_anuncios.html', anuncios=anuncios)

@app.route('/excluir_animal/<int:id>', methods=['POST'])
def excluir_animal(id):
    animal = Animal.query.get_or_404(id)

    # Só permite excluir se o dono for o usuário logado
    if animal.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir este animal.', 'danger')
        return redirect(url_for('meus_anuncios'))

    db.session.delete(animal)
    db.session.commit()
    flash('Animal excluído com sucesso!', 'success')

    # Redireciona para a tela que enviou o formulário (padrão: meus_anuncios)
    next_url = request.form.get('next')
    return redirect(next_url or url_for('meus_anuncios'))

if __name__ == '__main__':
    app.run(debug=True)

"""TESTE"""