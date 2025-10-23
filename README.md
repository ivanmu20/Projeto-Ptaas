---


# 🛡️ PTaaS — Penetration Testing as a Service

O **PTaaS** é uma plataforma web desenvolvida em **Python** que automatiza testes de penetração em websites.  
A aplicação permite ao usuário inserir uma URL, realizar varreduras de segurança com ferramentas como **OWASP ZAP** e **Nikto**, e gerar relatórios detalhados em **HTML/PDF**.  

O objetivo é oferecer uma solução **segura**, **automatizada** e **escalável** de análise de vulnerabilidades para empresas, profissionais de cibersegurança e desenvolvedores.

---

## 🚀 Stack Tecnológica

**Frontend:**  
- React.js / Next.js  
- TypeScript  
- TailwindCSS  

**Backend:**  
- Python (FastAPI + SQLAlchemy + Pydantic)  
- OWASP ZAP / Nikto (para varreduras automatizadas)  
- Celery + Redis (para filas de tarefas e monitoramento)  
- PostgreSQL (via Supabase)  

**Infraestrutura:**  
- Docker e Docker Compose  
- Nginx (proxy reverso e SSL/TLS)  
- CI/CD (GitHub Actions)  

**Segurança:**  
- JWT (autenticação segura)  
- Criptografia AES/RSA  
- HTTPS com certificados SSL  

---

## 📐 Arquitetura (MVC)

O projeto segue a arquitetura **MVC (Model-View-Controller)** adaptada para **FastAPI + React**.

### 🔹 Model (M)
Define as estruturas de dados e as regras de negócio.  
Inclui **Usuários**, **Relatórios**, **Scans**, **Histórico de Execuções** e **Agendamentos**.  
Implementado com **SQLAlchemy**, garantindo consistência e segurança dos dados.

### 🔹 View (V)
Interface web desenvolvida em **React/Next.js**.  
Permite:
- Inserir URLs para análise  
- Acompanhar progresso das varreduras  
- Visualizar e baixar relatórios  
- Gerir usuários e histórico de testes  

### 🔹 Controller (C)
Camada de controle (API FastAPI).  
Gerencia:
- Criação de scans (`/scan/start`)  
- Consulta de resultados (`/scan/report/{id}`)  
- Autenticação (`/auth/login`, `/auth/register`)  
- Agendamento de tarefas com Celery  

---

## 📂 Estrutura de Diretórios

```

ptaas/
├── backend/
│   ├── app/
│   │   ├── controllers/         # Rotas e controladores FastAPI
│   │   ├── models/              # Models SQLAlchemy
│   │   ├── schemas/             # Pydantic (validação de dados)
│   │   ├── services/            # Lógica de negócios e integração ZAP/Nikto
│   │   ├── middlewares/         # Autenticação, logs, CORS, etc.
│   │   ├── config/              # Variáveis de ambiente e inicialização
│   │   └── main.py              # Ponto de entrada FastAPI
│   ├── tests/                   # Testes unitários e integração
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/          # Componentes reutilizáveis (Cards, Modals, Tables)
│   │   ├── pages/               # Páginas principais (Dashboard, Scan, Login)
│   │   ├── hooks/               # Hooks personalizados
│   │   ├── services/            # Comunicação com API (Axios)
│   │   └── styles/              # Tailwind e CSS global
│   └── package.json
│
├── docs/                        # Documentação técnica e relatórios
├── infra/                       # Configurações Docker/Kubernetes
├── .env.example                 # Variáveis de ambiente de exemplo
├── docker-compose.yml
└── README.md

````

---

## 🔧 Configuração de Ambiente com Git

### Estrutura de Branches
- **main** → Produção (versão estável).  
- **staging** → Homologação e testes.  
- **dev-nome** → Branch individual de desenvolvimento.

### Setup do Repositório
```bash
# Clonar o repositório
git clone git@github.com:org/ptaas.git
cd ptaas

# Criar branches principais
git checkout -b main
git checkout -b staging
git checkout -b dev-meu_nome
````

### Workflow Sugerido

1. Desenvolva na sua branch (`dev-meu_nome`).
2. Envie PR para `staging` após concluir a feature.
3. Após revisão, merge para `main` (produção).

---

## 🧰 Git Cheat Sheet

| Ação                    | Comando                                    |
| ----------------------- | ------------------------------------------ |
| Configurar nome e email | `git config --global user.name "Seu Nome"` |
| Clonar repositório      | `git clone <url>`                          |
| Criar nova branch       | `git checkout -b feature/nome`             |
| Adicionar mudanças      | `git add .`                                |
| Fazer commit            | `git commit -m "Descrição da mudança"`     |
| Enviar para remoto      | `git push origin feature/nome`             |
| Atualizar branch local  | `git pull origin main`                     |
| Criar Pull Request      | via GitHub                                 |
| Fazer merge             | `git merge feature/nome`                   |

---

## 🧪 Como Rodar o Projeto (Ambiente Dev)

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Com Docker

```bash
docker-compose up --build
```

---

## ✅ Próximos Passos

* Implementar módulo de **agendamento automático de scans**
* Adicionar **exportação em PDF e envio por e-mail**
* Integrar **notificações em tempo real** (WebSockets)
* Configurar **monitoramento de logs e métricas (Prometheus + Grafana)**

---

## 👥 Contribuidores

Equipe **PTaaS Development** – CyberVigil

* Ruben Baqui
* Artur Lopes
* Thiago Lima
* Francisco Fernandes
* Ivan Mubai
* António Urdaneta




