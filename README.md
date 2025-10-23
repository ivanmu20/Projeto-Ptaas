# Projeto-Ptaas
PTaaS (Penetration Testing as a Service) é uma aplicação web em Python que automatiza a análise de vulnerabilidades em websites com ferramentas como OWASP ZAP e Nikto. O sistema permite inserir uma URL, executar o scan e gerar relatórios HTML claros com níveis de severidade das falhas.

Perfeito, Ivan 👏
Aqui vai o **`README.md` completo e profissional**, já formatado para GitHub, com:

* 🧠 Descrição do projeto
* 🛠️ Stack usada
* ⚙️ Instruções de uso
* 📂 Estrutura completa (frontend + backend + docs)
* ✅ TODO list (tree visual com as tarefas por fazer)

---

````markdown
# 🛡️ PTaaS – Penetration Testing as a Service

O **PTaaS (Penetration Testing as a Service)** é uma aplicação web em Python que automatiza a análise de vulnerabilidades em websites.  
O sistema permite inserir uma URL, executar o scan com ferramentas como **OWASP ZAP**, **Nikto** ou **Wapiti**, e gerar relatórios em **HTML** com níveis de severidade (Alta, Média, Baixa).

> 🎯 Objetivo da MVP: Criar um protótipo funcional (MVP) que realiza um scan de vulnerabilidades e exibe um relatório simples via interface web.

---

## 🧱 Stack Tecnológica

| Camada | Tecnologias | Descrição |
|--------|--------------|------------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap, Jinja2 (via Flask) | Interface leve e funcional |
| **Backend** | Python 3 + Flask (ou FastAPI) | API simples para envio de URLs e execução do scanner |
| **Scanner** | OWASP ZAP (CLI ou Daemon), Nikto, Wapiti | Ferramentas de segurança open-source |
| **Relatórios** | JSON → HTML (renderizado com Jinja2) | Exibição de vulnerabilidades e recomendações |
| **Hospedagem** | Localhost / Render / Glitch | Gratuito para testes e apresentação |
| **Controle de versão** | Git + GitHub | Organização e colaboração da equipa |

---

## ⚙️ Como Executar o Projeto

### 🔸 1. Clonar o repositório principal
```bash
git clone https://github.com/ivanmu20/Projeto-Ptaas.git
cd Projeto-Ptaas
````

### 🔸 2. Configurar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 🔸 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 🔸 4. Executar o servidor Flask

```bash
python backend/app.py
```

### 🔸 5. Aceder à aplicação

Abra no navegador:
👉 [http://localhost:5000](http://localhost:5000)

---

## 📂 Estrutura do Projeto (Tree)

```
Projeto-Ptaas/
│
├── backend/
│   ├── app.py                # API principal (Flask ou FastAPI)
│   ├── scanner.py            # Integração com ZAP, Nikto ou Wapiti
│   ├── reports/              # Relatórios gerados
│   └── utils/                # Funções auxiliares
│
├── frontend/
│   ├── templates/
│   │   ├── index.html        # Página inicial (formulário para URL)
│   │   └── report.html       # Página de relatório
│   ├── static/
│   │   ├── style.css         # Estilos da interface
│   │   └── script.js         # Lógica de front
│
├── docs/
│   ├── README.md             # Documentação técnica e instruções
│   ├── slides.pdf            # Apresentação final
│   └── screenshots/          # Imagens do sistema
│
├── tests/
│   ├── test_api.py           # Testes do backend
│   └── test_frontend.py      # Testes básicos da UI
│
├── requirements.txt          # Dependências do Python
├── .gitignore                # Ignora arquivos desnecessários
├── LICENSE                   # Licença MIT
└── README.md                 # Este arquivo
```

---

## ✅ TODO Tree (Planeamento do Desenvolvimento)

### 📅 Semana 1 – Planeamento

* [x] Definir funcionalidade da MVP
* [x] Escolher ferramentas (ZAP, Nikto, Wapiti)
* [ ] Criar protótipo da UI
* [ ] Montar estrutura inicial de pastas

### 🧠 Semana 2 – Desenvolvimento inicial

* [ ] Implementar API Flask para receber URLs
* [ ] Executar scanner via subprocess
* [ ] Criar interface básica (HTML + formulário)
* [ ] Conectar frontend → backend

### ⚙️ Semana 3 – Integração e Relatórios

* [ ] Tratar saída JSON/XML dos scanners
* [ ] Gerar relatório formatado em HTML
* [ ] Exibir severidade e recomendações

### 🧪 Semana 4 – Testes e Entrega

* [ ] Realizar testes completos (URLs válidas e inválidas)
* [ ] Criar documentação técnica (stack, arquitetura, screenshots)
* [ ] Preparar slides e apresentação final

---

## 💡 Exemplo de Execução do Scanner

OWASP ZAP:

```bash
zap-cli quick-scan --self-contained --spider --scanners all https://exemplo.com
```

Nikto:

```bash
nikto -h https://exemplo.com -output report.json
```

Wapiti:

```bash
wapiti -u https://exemplo.com -f json -o report.json
```

---

## 🧾 Estrutura do Relatório (JSON → HTML)

```json
{
  "url": "https://exemplo.com",
  "scan_date": "2025-10-23",
  "vulnerabilities": [
    {
      "id": "SQLI-01",
      "type": "SQL Injection",
      "severity": "High",
      "description": "Input não validado em formulário de login.",
      "recommendation": "Usar consultas parametrizadas e sanitização."
    }
  ]
}
```

---

## 🧑‍💻 Equipa

* **Dupla 1:** Backend + Scanner
* **Dupla 2:** Frontend + Relatórios
* **Dupla 3:** Testes + Documentação + Apresentação

---

## 📄 Licença

Licença MIT © 2025 – Equipa PTaaS

---

### 🚀 Próximos Passos (v2.0)

* Autenticação de usuários
* Banco de dados para histórico de scans
* Relatórios com gráficos
* Agendamento de varreduras automáticas

```

---

Se quiser, posso também gerar o **`requirements.txt` básico** com Flask, zap-cli, requests, e jinja2 — assim já podes fazer o primeiro `git push` com tudo preparado.  
Quer que eu gere esse arquivo também?
```
