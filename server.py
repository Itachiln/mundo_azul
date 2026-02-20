

from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import datetime, os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mensajes = []
fotos = []
libros = []

# Página principal con corazón y accesos grandes
home_html = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Mundo Azul</title>
  <style>
    body { margin:0; font-family:'Helvetica Neue', Arial; background:linear-gradient(135deg,#001f3f,#0074D9,#7FDBFF,#FFDC00,#B10DC9); background-size:400% 400%; animation:fondo 15s ease infinite; color:white; text-align:center; }
    @keyframes fondo { 0%{background-position:0% 50%;} 50%{background-position:100% 50%;} 100%{background-position:0% 50%;} }
    h1 { font-size:48px; margin-top:20px; }
    .corazon { position:relative; width:400px; height:360px; margin:50px auto; }
    .corazon:before, .corazon:after { content:""; position:absolute; width:200px; height:320px; border-radius:200px 200px 0 0; background:red; top:0; }
    .corazon:before { left:200px; transform:rotate(-45deg); transform-origin:0 100%; }
    .corazon:after { left:0; transform:rotate(45deg); transform-origin:100% 100%; }
    .contador { margin-top:20px; font-size:36px; font-weight:bold; color:white; }
    .menu { margin-top:40px; }
    .menu a { display:inline-block; margin:30px; padding:30px; background:#39CCCC; color:#001f3f; border-radius:20px; text-decoration:none; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.3); }
  </style>
</head>
<body>
  <h1>Bienvenida 💙</h1>
  <div class="corazon"></div>
  <div class="contador">Han pasado {{dias}} días 💙</div>
  <div class="menu">
    <a href="/chat">💬 Chat</a>
    <a href="/galeria">📸 Galería</a>
    <a href="/biblioteca">📚 Biblioteca</a>
  </div>
</body>
</html>
"""

chat_html = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Chat</title>
<style>
  body { font-family:'Helvetica Neue', Arial; background:#f0f0f0; margin:0; padding:0; }
  .chatbox { max-width:600px; margin:40px auto; background:white; border-radius:20px; padding:20px; box-shadow:0 4px 15px rgba(0,0,0,0.2); }
  .mensaje { margin:10px; padding:15px; border-radius:20px; max-width:70%; font-size:20px; }
  .yo { background:#007AFF; color:white; margin-left:auto; text-align:right; }
  .ella { background:#E5E5EA; color:black; margin-right:auto; text-align:left; }
  form { margin-top:20px; }
  input { font-size:20px; padding:10px; width:70%; border-radius:10px; border:1px solid #ccc; }
  button { font-size:20px; padding:10px 20px; border:none; border-radius:10px; background:#007AFF; color:white; }
</style>
</head>
<body>
  <div class="chatbox">
    <h2 style="text-align:center;">💬 Chat</h2>
    <div>
      {% for m in mensajes %}
        <div class="mensaje {% if loop.index % 2 == 0 %}yo{% else %}ella{% endif %}">{{m}}</div>
      {% endfor %}
    </div>
    <form method="POST" action="/chat">
      <input type="text" name="mensaje" placeholder="Escribe un mensaje">
      <button type="submit">Enviar</button>
    </form>
    <p style="text-align:center;"><a href="/">Volver</a></p>
  </div>
</body>
</html>
"""

galeria_html = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Galería</title>
<style>
  body { font-family:'Helvetica Neue', Arial; background:#fafafa; margin:0; padding:0; }
  .galeria { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:20px; padding:20px; }
  .foto { border-radius:20px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.2); transition:transform 0.3s; }
  .foto:hover { transform:scale(1.05); }
  .foto img { width:100%; height:auto; display:block; }
  form { text-align:center; margin:20px; }
  input,button { font-size:20px; padding:10px; margin:10px; }
  button { background:#39CCCC; color:#001f3f; border:none; border-radius:10px; }
</style>
</head>
<body>
  <h2 style="text-align:center; font-size:36px;">📸 Galería</h2>
  <form method="POST" action="/galeria" enctype="multipart/form-data">
    <input type="file" name="foto">
    <button type="submit">Subir</button>
  </form>
  <div class="galeria">
    {% for f in fotos %}
      <div class="foto"><img src="/uploads/{{f}}"></div>
    {% endfor %}
  </div>
  <p style="text-align:center;"><a href="/" style="font-size:24px;">Volver</a></p>
</body>
</html>
"""

biblioteca_html = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Biblioteca</title></head>
<body style="font-family:Arial; background:#7FDBFF; color:black; text-align:center;">
  <h2 style="font-size:36px;">📚 Biblioteca</h2>
  <form method="POST" action="/biblioteca" enctype="multipart/form-data">
    <input type="text" name="codigo" placeholder="Introduce tu código" style="font-size:24px; padding:10px;">
    <input type="file" name="libro" style="font-size:24px;">
    <button type="submit" style="font-size:24px; padding:15px;">Entrar</button>
  </form>
  <div style="font-size:24px;">
    {% if acceso %}
      <p>Acceso concedido. Aquí están los libros:</p>
      {% for l in libros %}
        <p><a href="/uploads/{{l}}" download style="font-size:24px;">{{l}}</a></p>
      {% endfor %}
    {% endif %}
  </div>
  <a href="/" style="font-size:24px;">Volver</a>
</body>
</html>
"""

@app.route("/")
def inicio():
    inicio = datetime.date(2026,1,18)
    hoy = datetime.date.today()
    dias = (hoy - inicio).days
    return render_template_string(home_html, dias=dias)

@app.route("/chat", methods=["GET","POST"])
def chat():
    if request.method == "POST":
        mensaje = request.form.get("mensaje")
        if mensaje:
            mensajes.append(mensaje)
        return redirect(url_for("chat"))
    return render_template_string(chat_html, mensajes=mensajes)

@app.route("/galeria", methods=["GET","POST"])
def galeria():
    if request.method == "POST":
        archivo = request.files.get("foto")
        if archivo:
            nombre = archivo.filename
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre))
            fotos.append(nombre)
        return redirect(url_for("galeria"))
    return render_template_string(galeria_html, fotos=fotos)

@app.route("/biblioteca", methods=["GET","POST"])
def biblioteca():
    acceso = False
    if request.method == "POST":
        codigo = request.form.get("codigo")
        archivo = request.files.get("libro")
        if codigo in ["3496","71853"]:
            acceso = True
            if archivo:
                nombre = archivo.filename
                archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre))
                libros.append(nombre)
    return render_template_string(biblioteca_html, libros=libros, acceso=acceso)

@app.route("/uploads/<path:filename>")
def descargar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
