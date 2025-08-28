# 🐾 Adote Já

O **Adote Já** é uma aplicação web desenvolvida para facilitar a adoção responsável de animais, conectando pessoas que desejam adotar com tutores ou abrigos que têm pets disponíveis.  
O sistema oferece filtros de busca, gerenciamento de cadastros, upload de fotos de animais e integração com WhatsApp para contato rápido.

---

## 📸 Funcionalidades

- **Listagem de Animais** com fotos e informações detalhadas.
- **Filtros Avançados** para busca por:
  - Espécie
  - Raça (listas dinâmicas para cães e gatos)
  - Sexo
  - Status de vacinação
  - Status de castração
  - Estado e cidade (apenas locais com animais cadastrados)
- **Cadastro, Edição e Exclusão de Animais** pelo usuário que anunciou.
- **Controle de Anúncios**:
  - Anúncios ativos e inativos
  - Alertas de expiração próximos
  - Possibilidade de reativar anúncios inativos
- **Integração com WhatsApp** para contato direto com o anunciante.
- **Uploads de Fotos de Animais** com placeholders para fotos não cadastradas.
- **Cadastro e Edição de Perfil do Usuário**, incluindo foto e telefone.
- **Interface Responsiva e Amigável**, utilizando Bootstrap 5 e Select2 para filtros e formulários.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3.3, Select2
- **Banco de Dados:** MySQL (via SQLAlchemy)
- **Uploads de Arquivos:** PIL (Pillow) para validação e manipulação de imagens
- **Autenticação:** Sessão de usuário com login/senha
- **Integrações:** WhatsApp (link direto via `wa.me`)
- **Controle de Versão:** Git + GitHub

---

## 📂 Estrutura de Pastas (Resumo)

├── app.py # Arquivo principal da aplicação
├── templates/ # Páginas HTML (Jinja2)
├── static/ # CSS, JS, imagens e uploads
│ ├── uploads/img_animais/
│ └── fotos_perfil/
├── requirements.txt # Dependências
└── README.md # Documentação

---

## 🖥️ Configuração do Banco de Dados MySQL

1. Instale o MySQL se ainda não tiver.
2. Acesse o MySQL via terminal ou Workbench.
3. Crie o banco de dados:
CREATE DATABASE adoteja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


## Crie o usuário e conceda permissões (substitua senha_segura pelo que desejar):

CREATE USER 'adoteja_user'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON adoteja.* TO 'adoteja_user'@'localhost';
FLUSH PRIVILEGES;

## Configure a string de conexão no app.py:

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://adoteja_user:senha_segura@localhost/adoteja'

## Crie as tabelas no banco:

-- ===============================
-- Tabela de Usuários
-- ===============================

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    foto VARCHAR(255),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- Tabela de Animais
-- ===============================

CREATE TABLE animal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raca VARCHAR(50),
    sexo VARCHAR(10),
    vacinado TINYINT(1) DEFAULT 2, -- 0: Sim, 1: Não, 2: Não sei
    castrado TINYINT(1) DEFAULT 2, -- 0: Sim, 1: Não, 2: Não sei
    foto VARCHAR(255),
    ativo BOOLEAN DEFAULT TRUE,
    data_validade DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 30 DAY),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

## Inicialize as tabelas (executar via Flask shell ou script):

from app import db
db.create_all()


🚀 Como Executar Localmente

1. Clone este repositório:
git clone https://github.com/seu-usuario/adote-ja.git
cd adote-ja

2. Crie e ative um ambiente virtual:

No Windows:
python -m venv venv
venv\Scripts\activate

No Linux/Mac:
python -m venv venv
source venv/bin/activate

3. Instale as dependências:
pip install -r requirements.txt

4. Configure o banco de dados MySQL como descrito acima.

5. Execute a aplicação:
flask run

6. Acesse no navegador:
http://127.0.0.1:5000

---

📋 Pré-requisitos

° Python 3.9+
° pip
° MySQL
° Git

---

🤝 Contribuindo

Faça um fork do projeto

Crie uma branch (git checkout -b minha-feature)

Commit suas alterações (git commit -m 'Minha nova feature')

Push para a branch (git push origin minha-feature)

Abra um Pull Request

---

📜 Licença

Licenciado sob a MIT License — sinta-se livre para usar e modificar, mantendo os créditos.

---

❤️ Agradecimentos

A todos que incentivam a adoção responsável

Comunidade open source

Tutores que compartilham seus animais para adoção