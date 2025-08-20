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
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Chave estrangeira
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(50))
    sexo = db.Column(db.String(10))
    vacinado = db.Column(db.Integer, default=2)
    castrado = db.Column(db.Integer, default=2)
    foto = db.Column(db.String(200))
    estado = db.Column(db.String(50))   # Herdado do usuário
    cidade = db.Column(db.String(50))   # Herdado do usuário
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

# Função global para excluir anúncios de QUALQUER usuário com mais de 30 dias
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
from werkzeug.security import generate_password_hash

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        estado = request.form.get('estado')
        cidade = request.form.get('cidade')

        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('cadastrar'))

        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('cadastrar'))

        # Criptografar senha
        senha_criptografada = generate_password_hash(senha)

        # Foto (opcional)
        foto = request.files.get('foto')
        nome_foto = None
        if foto and foto.filename:
            nome_foto = secure_filename(foto.filename)
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER_USUARIO'], nome_foto)
            foto.save(caminho_foto)

        # Criar usuário e salvar no banco
        usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            senha=senha_criptografada,
            estado=estado,
            cidade=cidade,
            foto=nome_foto
        )
        db.session.add(usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('login'))

    # ====== GET ====== Carregar ESTADOS e CIDADES ======
    estados_path = os.path.join(DATA_DIR, 'estados.json')
    with open(estados_path, 'r', encoding='utf-8') as f:
        estados_lista = json.load(f)['estados']

    cidades_dir = os.path.join(DATA_DIR, 'cidades')
    cidades_por_estado = {}
    if os.path.isdir(cidades_dir):
        for arquivo in os.listdir(cidades_dir):
            if arquivo.endswith('.json'):
                caminho = os.path.join(cidades_dir, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('cidades', []):
                        uf = item.get('id')
                        nome = item.get('cidade')
                        if uf and nome:
                            cidades_por_estado.setdefault(uf, []).append(nome)

    for uf in cidades_por_estado:
        cidades_por_estado[uf].sort(key=lambda s: s.lower())
    estados_lista.sort(key=lambda e: e['estado'].lower())

    return render_template(
        'cadastrar.html',
        estados=estados_lista,
        cidades_por_estado=cidades_por_estado
    )

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

        # ===== Vincular cidade e estado do usuário =====
        usuario = Usuario.query.get(session["usuario_id"])
        if usuario:
            animal.estado = usuario.estado
            animal.cidade = usuario.cidade

        # ===== Upload e processamento da foto =====
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

# Ajuste da rota listar_animais para aceitar estado/cidade
@app.route('/listar_animais')
def listar_animais():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Exclui anúncios antigos
    excluir_animais_vencidos()

    # Pegando filtros enviados pela URL (GET)
    especie = request.args.get('especie')
    raca = request.args.get('raca')
    sexo = request.args.get('sexo')
    vacinado_value = request.args.get('vacinado')
    castrado_value = request.args.get('castrado')
    estado = request.args.get('estado')
    cidade = request.args.get('cidade')

    # Faz join com Usuario para pegar cidade e estado
    query = Animal.query.join(Usuario)

    if especie and especie.strip():
        query = query.filter(Animal.especie == especie)
    if raca and raca.strip():
        query = query.filter(Animal.raca == raca)
    if sexo and sexo.strip():
        query = query.filter(Animal.sexo == sexo)
    if vacinado_value in ('0', '1', '2'):
        query = query.filter(Animal.vacinado == int(vacinado_value))
    if castrado_value in ('0', '1', '2'):
        query = query.filter(Animal.castrado == int(castrado_value))
    if estado and estado != "Indiferente":
        query = query.filter(Usuario.estado == estado)
    if cidade and cidade != "Indiferente":
        query = query.filter(Usuario.cidade == cidade)

    animais = query.order_by(Animal.criado_em.desc()).all()

    # ===== Carregar estados e cidades dos JSON =====
    estados_path = os.path.join(DATA_DIR, 'estados.json')
    with open(estados_path, 'r', encoding='utf-8') as f:
        estados_lista = json.load(f)['estados']

    cidades_por_estado = {}
    cidades_dir = os.path.join(DATA_DIR, 'cidades')
    if os.path.isdir(cidades_dir):
        for arquivo in os.listdir(cidades_dir):
            if arquivo.endswith('.json'):
                caminho = os.path.join(cidades_dir, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('cidades', []):
                        uf = item.get('id')
                        nome = item.get('cidade')
                        if uf and nome:
                            cidades_por_estado.setdefault(uf, []).append(nome)
    for uf in cidades_por_estado:
        cidades_por_estado[uf].sort(key=lambda s: s.lower())
    estados_lista.sort(key=lambda e: e['estado'].lower())

    return render_template('listar_animais.html', animais=animais, meus_anuncios=False,
                           pagina_atual='listar_animais', estados=estados_lista, cidades_por_estado=cidades_por_estado)

@app.route('/perfil_doador/<int:usuario_id>')
def perfil_doador(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('perfil_doador.html', usuario=usuario)

@app.route('/meus_anuncios')
def meus_anuncios():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    # Pega apenas os animais do usuário logado
    animais = Animal.query.filter_by(usuario_id=usuario_id).order_by(Animal.criado_em.desc()).all()

    # ===== Carregar estados e cidades dos JSON =====
    estados_path = os.path.join(DATA_DIR, 'estados.json')
    with open(estados_path, 'r', encoding='utf-8') as f:
        estados_lista = json.load(f)['estados']

    cidades_por_estado = {}
    cidades_dir = os.path.join(DATA_DIR, 'cidades')
    if os.path.isdir(cidades_dir):
        for arquivo in os.listdir(cidades_dir):
            if arquivo.endswith('.json'):
                caminho = os.path.join(cidades_dir, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('cidades', []):
                        uf = item.get('id')
                        nome = item.get('cidade')
                        if uf and nome:
                            cidades_por_estado.setdefault(uf, []).append(nome)
    for uf in cidades_por_estado:
        cidades_por_estado[uf].sort(key=lambda s: s.lower())
    estados_lista.sort(key=lambda e: e['estado'].lower())

    return render_template(
        'listar_animais.html',  # Podemos reutilizar o mesmo template
        animais=animais,
        estados=estados_lista,
        cidades_por_estado=cidades_por_estado,
        filtro_estado="Indiferente",
        filtro_cidade="Indiferente",
        meus_anuncios=True  # Para, se quiser, customizar algo no template
    )


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