import csv
import io
import json
import os
import re
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string, jsonify, flash, send_file

APP_TITLE = "Mini Privacy Console (Protótipo Académico)"
DB_PATH = "privacy_demo.db"

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# ----------------------------
# PII patterns (heurístico)
# ----------------------------
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "telefone": re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){8,12}\b"),
    "nif_pt": re.compile(r"\b\d{9}\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.I),
}

NAME_LIKE = re.compile(
    r"\b[A-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ][a-záàâãéèêíìîóòôõúùûç]+"
    r"\s+[A-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ][a-záàâãéèêíìîóòôõúùûç]+\b"
)

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def detect_pii(value: str) -> list[str]:
    if value is None:
        return []
    v = str(value).strip()
    if not v:
        return []

    hits = []
    for k, rgx in PII_PATTERNS.items():
        if rgx.search(v):
            hits.append(k)
    if NAME_LIKE.search(v):
        hits.append("nome")

    out, seen = [], set()
    for h in hits:
        if h not in seen:
            out.append(h)
            seen.add(h)
    return out

def scan_csv(content_bytes: bytes, max_rows: int = 2000):
    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = content_bytes.decode("latin-1")

    f = io.StringIO(text)
    reader = csv.DictReader(f)
    headers = reader.fieldnames or []

    findings = {h: {"pii_types": set(), "examples": {}} for h in headers}
    rows = []
    subject_index = {}  # email -> linhas

    for i, row in enumerate(reader):
        if i >= max_rows:
            break
        rows.append(row)

        row_emails = set()
        for h in headers:
            val = row.get(h, "")
            hits = detect_pii(val)
            for t in hits:
                findings[h]["pii_types"].add(t)
                findings[h]["examples"].setdefault(t, str(val)[:80])
            if "email" in hits:
                row_emails.add(str(val).strip().lower())

        for em in row_emails:
            subject_index.setdefault(em, []).append(row)

    findings_out = {}
    for h in headers:
        findings_out[h] = {
            "pii_types": sorted(list(findings[h]["pii_types"])),
            "examples": findings[h]["examples"],
        }

    return headers, rows, findings_out, subject_index

# ----------------------------
# DB helpers
# ----------------------------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            pii_summary_json TEXT NOT NULL,
            row_count INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS consents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_email TEXT NOT NULL UNIQUE,
            marketing INTEGER NOT NULL,
            analytics INTEGER NOT NULL,
            personalized_ads INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dsar_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_email TEXT NOT NULL,
            dataset_id INTEGER NOT NULL,
            requested_at TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ----------------------------
# UI
# ----------------------------
BASE_HTML = """
<!doctype html>
<html lang="pt">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{{ title }}</title>
  <style>
    body{font-family:system-ui,Segoe UI,Arial;margin:0;background:#f6f7fb}
    header{background:#111827;color:#fff;padding:16px 20px}
    nav a{color:#fff;text-decoration:none;margin-right:14px;font-weight:700;font-size:14px}
    main{max-width:1100px;margin:18px auto;padding:0 16px 40px}
    .card{background:#fff;border-radius:14px;box-shadow:0 6px 18px rgba(0,0,0,.06);padding:16px;margin-bottom:14px}
    .row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
    .btn{display:inline-block;padding:10px 12px;border-radius:10px;border:0;background:#111827;color:#fff;font-weight:800;cursor:pointer;text-decoration:none}
    .btn.secondary{background:#374151}
    input,select{padding:10px 12px;border-radius:10px;border:1px solid #e5e7eb;width:100%;box-sizing:border-box}
    label{font-size:13px;color:#374151;font-weight:800;display:block;margin-bottom:6px}
    table{width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden}
    th,td{text-align:left;padding:10px;border-bottom:1px solid #eef2f7;font-size:13px;vertical-align:top}
    th{background:#f3f4f6;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
    .tag{display:inline-block;padding:4px 8px;border-radius:999px;background:#eef2ff;font-size:12px;font-weight:800;margin-right:6px;margin-bottom:6px}
    .muted{color:#6b7280;font-size:13px}
    .flash{background:#ecfeff;border:1px solid #a5f3fc;color:#0e7490;padding:10px 12px;border-radius:12px;margin-bottom:14px}
    @media(max-width:880px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<header>
  <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-size:18px;font-weight:900;">{{ app_title }}</div>
      <div class="muted" style="color:#cbd5e1;">Protótipo académico inspirado em privacy platforms</div>
    </div>
    <nav>
      <a href="{{ url_for('home') }}">Dashboard</a>
      <a href="{{ url_for('upload') }}">PII Scanner</a>
      <a href="{{ url_for('consent') }}">Consentimentos</a>
      <a href="{{ url_for('dsar') }}">DSAR</a>
    </nav>
  </div>
</header>
<main>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      {% for m in messages %}
        <div class="flash">{{ m }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {{ body|safe }}
</main>
</body>
</html>
"""

def page(body_html: str, title: str):
    return render_template_string(
        BASE_HTML, body=body_html, title=title, app_title=APP_TITLE
    )

# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def home():
    conn = db()
    datasets = conn.execute("SELECT * FROM datasets ORDER BY id DESC").fetchall()
    conn.close()

    body = """
    <div class="card">
      <h2 style="margin:0 0 8px;">Data Inventory</h2>
      <div class="muted">Datasets analisados e resumo de PII.</div>
      <div style="margin-top:12px;">
        {% if datasets %}
          <table>
            <thead><tr><th>ID</th><th>Nome</th><th>Linhas</th><th>Criado</th><th></th></tr></thead>
            <tbody>
              {% for d in datasets %}
                <tr>
                  <td>{{ d["id"] }}</td>
                  <td><strong>{{ d["name"] }}</strong></td>
                  <td>{{ d["row_count"] }}</td>
                  <td>{{ d["created_at"] }}</td>
                  <td><a class="btn secondary" href="{{ url_for('dataset_detail', dataset_id=d['id']) }}">Ver</a></td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        {% else %}
          <p class="muted" style="margin-top:10px;">Ainda não há datasets. Começa pelo PII Scanner.</p>
        {% endif %}
      </div>
    </div>
    """
    return page(render_template_string(body, datasets=datasets), "Dashboard")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        name = (request.form.get("name") or "").strip() or (file.filename if file else "dataset")

        if not file or file.filename == "":
            flash("Escolhe um ficheiro CSV.")
            return redirect(url_for("upload"))

        content = file.read()
        headers, rows, findings, subject_index = scan_csv(content)

        pii_summary = {
            "columns": findings,
            "subjects_detected": sorted(list(subject_index.keys()))[:200],
            "notes": "Deteção por regex/heurísticas para fins académicos."
        }

        conn = db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO datasets (name, created_at, pii_summary_json, row_count) VALUES (?, ?, ?, ?)",
            (name, now_iso(), json.dumps(pii_summary, ensure_ascii=False), len(rows))
        )
        dataset_id = cur.lastrowid
        conn.commit()
        conn.close()

        flash(f"Dataset '{name}' analisado e guardado com ID {dataset_id}.")
        return redirect(url_for("dataset_detail", dataset_id=dataset_id))

    body = """
    <div class="card">
      <h2 style="margin:0 0 6px;">PII Scanner</h2>
      <div class="muted">Faz upload de um CSV e deteta PII (heurístico).</div>

      <form method="post" enctype="multipart/form-data" style="margin-top:14px;">
        <div class="row">
          <div>
            <label>Nome do dataset</label>
            <input name="name" placeholder="ex.: clientes_ficticios_2026" />
            <div class="muted" style="margin-top:6px;font-size:12px;">Opcional.</div>
          </div>
          <div>
            <label>Ficheiro CSV</label>
            <input type="file" name="file" accept=".csv,text/csv" required />
            <div class="muted" style="margin-top:6px;font-size:12px;">Até 2000 linhas para demo.</div>
          </div>
        </div>

        <div style="margin-top:14px;">
          <button class="btn" type="submit">Analisar e guardar</button>
        </div>
      </form>
    </div>
    """
    return page(body, "PII Scanner")

@app.route("/dataset/<int:dataset_id>")
def dataset_detail(dataset_id: int):
    conn = db()
    d = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    conn.close()
    if not d:
        return page("<div class='card'>Dataset não encontrado.</div>", "Erro")

    summary = json.loads(d["pii_summary_json"])
    columns = summary.get("columns", {})
    subjects = summary.get("subjects_detected", [])

    body = """
    <div class="card">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;">
        <div>
          <h2 style="margin:0 0 6px;">Dataset #{{ d["id"] }} — {{ d["name"] }}</h2>
          <div class="muted">Criado: {{ d["created_at"] }} • Linhas: {{ d["row_count"] }}</div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <a class="btn secondary" href="{{ url_for('dataset_json', dataset_id=d['id']) }}">Ver JSON</a>
          <a class="btn" href="{{ url_for('dsar', dataset_id=d['id']) }}">Simular DSAR</a>
        </div>
      </div>

      <hr style="border:none;border-top:1px solid #eef2f7;margin:14px 0;">

      <h3 style="margin:0 0 8px;">Resumo de PII por coluna</h3>
      <table>
        <thead><tr><th>Coluna</th><th>Tipos detetados</th><th>Exemplos</th></tr></thead>
        <tbody>
          {% for col, info in columns.items() %}
            <tr>
              <td><strong>{{ col }}</strong></td>
              <td>
                {% if info["pii_types"] %}
                  {% for t in info["pii_types"] %}
                    <span class="tag">{{ t }}</span>
                  {% endfor %}
                {% else %}
                  <span class="muted">—</span>
                {% endif %}
              </td>
              <td>
                {% if info["examples"] %}
                  {% for k, ex in info["examples"].items() %}
                    <div style="font-size:12px;"><strong>{{ k }}:</strong> <span class="muted">{{ ex }}</span></div>
                  {% endfor %}
                {% else %}
                  <span class="muted">—</span>
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>

      <div style="margin-top:14px;">
        <h3 style="margin:0 0 6px;">Data subjects detetados (por email)</h3>
        {% if subjects %}
          <div class="muted" style="font-size:12px;">Amostra (máx 200):</div>
          <div style="margin-top:8px;">
            {% for s in subjects %}
              <span class="tag">{{ s }}</span>
            {% endfor %}
          </div>
        {% else %}
          <div class="muted">Nenhum email detetado para indexação DSAR.</div>
        {% endif %}
      </div>
    </div>
    """
    return page(render_template_string(body, d=d, columns=columns, subjects=subjects), f"Dataset {dataset_id}")

@app.route("/dataset/<int:dataset_id>.json")
def dataset_json(dataset_id: int):
    conn = db()
    d = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    conn.close()
    if not d:
        return jsonify({"error": "dataset not found"}), 404
    return jsonify({
        "id": d["id"],
        "name": d["name"],
        "created_at": d["created_at"],
        "row_count": d["row_count"],
        "pii_summary": json.loads(d["pii_summary_json"])
    })

@app.route("/consent", methods=["GET", "POST"])
def consent():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if not email or "@" not in email:
            flash("Indica um email válido.")
            return redirect(url_for("consent"))

        marketing = 1 if request.form.get("marketing") == "on" else 0
        analytics = 1 if request.form.get("analytics") == "on" else 0
        ads = 1 if request.form.get("personalized_ads") == "on" else 0

        conn = db()
        conn.execute("""
            INSERT INTO consents (subject_email, marketing, analytics, personalized_ads, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(subject_email) DO UPDATE SET
              marketing=excluded.marketing,
              analytics=excluded.analytics,
              personalized_ads=excluded.personalized_ads,
              updated_at=excluded.updated_at
        """, (email, marketing, analytics, ads, now_iso()))
        conn.commit()
        conn.close()

        flash(f"Consentimentos atualizados para {email}.")
        return redirect(url_for("consent"))

    conn = db()
    items = conn.execute("SELECT * FROM consents ORDER BY updated_at DESC").fetchall()
    conn.close()

    body = """
    <div class="row">
      <div class="card">
        <h2 style="margin:0 0 6px;">Consent Manager</h2>
        <div class="muted">Regista preferências do titular.</div>

        <form method="post" style="margin-top:14px;">
          <label>Email do titular</label>
          <input name="email" placeholder="ex.: ana.silva@exemplo.pt" required />

          <div style="margin-top:12px;">
            <label><input type="checkbox" name="marketing" /> Marketing</label>
            <label><input type="checkbox" name="analytics" /> Analytics</label>
            <label><input type="checkbox" name="personalized_ads" /> Publicidade personalizada</label>
          </div>

          <div style="margin-top:14px;">
            <button class="btn" type="submit">Guardar consentimento</button>
          </div>
        </form>
      </div>

      <div class="card">
        <h2 style="margin:0 0 6px;">Registos</h2>
        {% if items %}
          <table>
            <thead><tr><th>Email</th><th>Marketing</th><th>Analytics</th><th>Ads</th><th>Atualizado</th></tr></thead>
            <tbody>
              {% for c in items %}
                <tr>
                  <td><strong>{{ c["subject_email"] }}</strong></td>
                  <td>{{ "Sim" if c["marketing"] else "Não" }}</td>
                  <td>{{ "Sim" if c["analytics"] else "Não" }}</td>
                  <td>{{ "Sim" if c["personalized_ads"] else "Não" }}</td>
                  <td>{{ c["updated_at"] }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        {% else %}
          <div class="muted">Ainda não há consentimentos.</div>
        {% endif %}
      </div>
    </div>
    """
    return page(render_template_string(body, items=items), "Consentimentos")

@app.route("/dsar", methods=["GET", "POST"])
def dsar():
    conn = db()
    datasets = conn.execute("SELECT id, name FROM datasets ORDER BY id DESC").fetchall()
    conn.close()

    selected_dataset_id = request.args.get("dataset_id", type=int)

    if request.method == "POST":
        subject_email = (request.form.get("subject_email") or "").strip().lower()
        dataset_id = int(request.form.get("dataset_id") or 0)
        if not subject_email or "@" not in subject_email:
            flash("Indica um email válido.")
            return redirect(url_for("dsar"))
        if dataset_id <= 0:
            flash("Escolhe um dataset.")
            return redirect(url_for("dsar"))

        conn = db()
        conn.execute("""
            INSERT INTO dsar_requests (subject_email, dataset_id, requested_at, status)
            VALUES (?, ?, ?, ?)
        """, (subject_email, dataset_id, now_iso(), "COMPLETED"))
        conn.commit()
        conn.close()

        return redirect(url_for("dsar_report", dataset_id=dataset_id, subject_email=subject_email))

    body = """
    <div class="card">
      <h2 style="margin:0 0 6px;">DSAR Simulator</h2>
      <div class="muted">Simula pedido GDPR. Este protótipo devolve um relatório baseado no inventário + consentimentos.</div>

      <form method="post" style="margin-top:14px;">
        <div class="row">
          <div>
            <label>Email do titular</label>
            <input name="subject_email" placeholder="ex.: ana.silva@exemplo.pt" required />
          </div>
          <div>
            <label>Dataset</label>
            <select name="dataset_id" required>
              <option value="">— Escolher —</option>
              {% for d in datasets %}
                <option value="{{ d['id'] }}" {% if selected_dataset_id == d['id'] %}selected{% endif %}>
                  #{{ d['id'] }} — {{ d['name'] }}
                </option>
              {% endfor %}
            </select>
          </div>
        </div>

        <div style="margin-top:14px;">
          <button class="btn" type="submit">Gerar relatório DSAR</button>
        </div>
      </form>
    </div>
    """
    return page(render_template_string(body, datasets=datasets, selected_dataset_id=selected_dataset_id), "DSAR")

@app.route("/dsar/report")
def dsar_report():
    dataset_id = request.args.get("dataset_id", type=int)
    subject_email = (request.args.get("subject_email") or "").strip().lower()
    if not dataset_id or not subject_email:
        return page("<div class='card'>Parâmetros em falta.</div>", "Erro")

    conn = db()
    d = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    consent = conn.execute("SELECT * FROM consents WHERE subject_email = ?", (subject_email,)).fetchone()
    conn.close()

    if not d:
        return page("<div class='card'>Dataset não encontrado.</div>", "Erro")

    summary = json.loads(d["pii_summary_json"])
    cols = summary.get("columns", {})

    consent_obj = None
    if consent:
        consent_obj = {
            "marketing": bool(consent["marketing"]),
            "analytics": bool(consent["analytics"]),
            "personalized_ads": bool(consent["personalized_ads"]),
            "updated_at": consent["updated_at"],
        }

    report = {
        "subject_email": subject_email,
        "dataset": {"id": d["id"], "name": d["name"], "created_at": d["created_at"], "row_count": d["row_count"]},
        "pii_columns_detected": {k: v["pii_types"] for k, v in cols.items() if v.get("pii_types")},
        "consent": consent_obj,
        "generated_at": now_iso(),
        "disclaimer": "Relatório DSAR simulado para fins académicos."
    }

    body = """
    <div class="card">
      <h2 style="margin:0 0 6px;">Relatório DSAR</h2>
      <div class="muted">Titular: <strong>{{ report["subject_email"] }}</strong> • Dataset: <strong>#{{ report["dataset"]["id"] }} — {{ report["dataset"]["name"] }}</strong></div>
      <div class="muted" style="font-size:12px;margin-top:4px;">Gerado em: {{ report["generated_at"] }}</div>

      <hr style="border:none;border-top:1px solid #eef2f7;margin:14px 0;">

      <h3 style="margin:0 0 8px;">PII detetada no inventário</h3>
      {% if report["pii_columns_detected"] %}
        <table>
          <thead><tr><th>Coluna</th><th>Tipos</th></tr></thead>
          <tbody>
            {% for col, types in report["pii_columns_detected"].items() %}
              <tr>
                <td><strong>{{ col }}</strong></td>
                <td>
                  {% for t in types %}
                    <span class="tag">{{ t }}</span>
                  {% endfor %}
                </td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <div class="muted">Nenhuma PII detetada no resumo.</div>
      {% endif %}

      <div style="margin-top:14px;">
        <h3 style="margin:0 0 8px;">Consentimento</h3>
        {% if report["consent"] %}
          <span class="tag">Marketing: {{ "Sim" if report["consent"]["marketing"] else "Não" }}</span>
          <span class="tag">Analytics: {{ "Sim" if report["consent"]["analytics"] else "Não" }}</span>
          <span class="tag">Ads: {{ "Sim" if report["consent"]["personalized_ads"] else "Não" }}</span>
          <div class="muted" style="font-size:12px;margin-top:6px;">Atualizado: {{ report["consent"]["updated_at"] }}</div>
        {% else %}
          <div class="muted">Nenhum consentimento encontrado para este email.</div>
        {% endif %}
      </div>

      <div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap;">
        <a class="btn secondary" href="{{ url_for('dsar_report_json', dataset_id=report['dataset']['id'], subject_email=report['subject_email']) }}">Baixar JSON</a>
        <a class="btn" href="{{ url_for('dsar') }}">Novo DSAR</a>
      </div>
    </div>
    """
    return page(render_template_string(body, report=report), "Relatório DSAR")

@app.route("/dsar/report.json")
def dsar_report_json():
    dataset_id = request.args.get("dataset_id", type=int)
    subject_email = (request.args.get("subject_email") or "").strip().lower()
    if not dataset_id or not subject_email:
        return jsonify({"error": "missing parameters"}), 400

    conn = db()
    d = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    consent = conn.execute("SELECT * FROM consents WHERE subject_email = ?", (subject_email,)).fetchone()
    conn.close()

    if not d:
        return jsonify({"error": "dataset not found"}), 404

    summary = json.loads(d["pii_summary_json"])
    cols = summary.get("columns", {})

    consent_obj = None
    if consent:
        consent_obj = {
            "marketing": bool(consent["marketing"]),
            "analytics": bool(consent["analytics"]),
            "personalized_ads": bool(consent["personalized_ads"]),
            "updated_at": consent["updated_at"],
        }

    report = {
        "subject_email": subject_email,
        "dataset": {"id": d["id"], "name": d["name"], "created_at": d["created_at"], "row_count": d["row_count"]},
        "pii_columns_detected": {k: v["pii_types"] for k, v in cols.items() if v.get("pii_types")},
        "consent": consent_obj,
        "generated_at": now_iso(),
        "disclaimer": "Relatório DSAR simulado para fins académicos."
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
    return send_file(
        io.BytesIO(payload),
        mimetype="application/json; charset=utf-8",
        as_attachment=True,
        download_name=f"dsar_{subject_email.replace('@','_at_')}_dataset_{dataset_id}.json"
    )

if __name__ == "__main__":
    init_db()
    print("🚀 Iniciando Mini Privacy Console...")
    app.run(host="127.0.0.1", port=5000, debug=True)
