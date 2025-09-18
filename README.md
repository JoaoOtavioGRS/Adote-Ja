# Adote-Já 🐾

Adote-Já é um **marketplace para adoção e doação de cães e gatos**, desenvolvido com **Flask** e **MySQL**, com o objetivo de ajudar a reduzir o número de animais de rua e facilitar o processo para quem resgata ou deseja adotar. O sistema é responsivo, podendo ser acessado via navegador em **computador, tablet ou celular**.

---

## Tecnologias Utilizadas

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Mail  
- **Banco de Dados:** MySQL (com PyMySQL)  
- **Front-end:** HTML, Bootstrap 5.3.3, Select2, JS/jQuery  
- **Manipulação de Imagens:** Pillow  
- **Segurança e Sessões:** Werkzeug, itsdangerous  
- **Fuso Horário e Datas:** pytz  

---

## Funcionalidades

- **Usuário**
  - Cadastro e login/logout com sessão  
  - Recuperação de senha via email  
  - Edição de perfil com foto de usuário  

- **Animais**
  - Cadastro de animais com fotos  
  - Edição e exclusão de animais  
  - Listagem de animais com filtros dinâmicos:
    - Espécie (Cachorro/Gato)  
    - Raça (com listas pré-definidas e opção "Outros")  
    - Sexo, vacinado, castrado  
  - Detalhes do animal com botão para copiar telefone  

- **Interface**
  - Templates responsivos com Bootstrap  
  - Uso de Select2 para filtros e campos de formulário  
  - Rodapé consistente em todas as páginas  
  - Mensagens de boas-vindas personalizadas  

---

## 📂 Estrutura de Pastas (Resumo)

adote-ja/
│
├── app.py # Aplicação principal Flask
├── requirements.txt # Dependências Python
├── templates/ # Templates HTML
│ ├── base.html
│ ├── home.html
│ ├── login.html
│ ├── cadastrar_usuario.html
│ ├── cadastrar_animal.html
│ ├── listar_animais.html
│ ├── editar_animal.html
│ └── ...
├── static/ # Arquivos estáticos (CSS, JS, imagens)
│ ├── css/
│ ├── js/
│ └── fotos_perfil/
├── uploads/ # Fotos dos animais
└── README.md

---

## Instalação

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

