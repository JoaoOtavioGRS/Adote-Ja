# 🐾 Adote Já

O **Adote Já** é uma aplicação web desenvolvida para facilitar a adoção responsável de animais, conectando pessoas que desejam adotar com tutores ou abrigos que têm pets disponíveis.  
O sistema oferece filtros de busca, gerenciamento de cadastros e integração com WhatsApp para contato rápido.

---

## 📸 Funcionalidades

- **Listagem de Animais** com fotos e informações detalhadas.
- **Filtros Avançados** para busca por:
  - Espécie
  - Raça
  - Sexo
  - Status de vacinação
  - Status de castração
- **Cadastro e Edição de Animais** pelo usuário que anunciou.
- **Integração com WhatsApp** para contato direto com o anunciante.
- **Imagens de Placeholder** para animais sem foto cadastrada.
- **Interface Responsiva** e amigável, com uso de Bootstrap e Select2.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap, Select2
- **Banco de Dados:** SQLite (padrão) – pode ser adaptado para outros SGBDs
- **Integrações:** API do WhatsApp (link direto via `wa.me`)
- **Controle de Versão:** Git + GitHub

---

## 📂 Estrutura de Pastas (Resumo)

├── app.py # Arquivo principal da aplicação
├── templates/ # Páginas HTML (Jinja2)
├── static/ # CSS, JS, imagens e uploads
├── requirements.txt # Dependências
└── README.md # Documentação

## 🚀 Como Executar Localmente
1. Clone este repositório:  
`git clone https://github.com/seu-usuario/adote-ja.git && cd adote-ja`  
2. Crie e ative um ambiente virtual:  
No **Windows**:  
`python -m venv venv && venv\Scripts\activate`  
No **Linux/Mac**:  
`python -m venv venv && source venv/bin/activate`  
3. Instale as dependências:  
`pip install -r requirements.txt`  
4. Execute a aplicação:  
`flask run`  
5. Acesse no navegador:  
`http://127.0.0.1:5000`

## 📋 Pré-requisitos
- Python 3.9+
- pip
- Git

## 🤝 Contribuindo
1. Faça um fork do projeto  
2. Crie uma branch (`git checkout -b minha-feature`)  
3. Commit suas alterações (`git commit -m 'Minha nova feature'`)  
4. Push para a branch (`git push origin minha-feature`)  
5. Abra um Pull Request  

## 📜 Licença
Licenciado sob a MIT License — sinta-se livre para usar e modificar, mantendo os créditos.

## ❤️ Agradecimentos
- A todos que incentivam a adoção responsável
- Comunidade open source
