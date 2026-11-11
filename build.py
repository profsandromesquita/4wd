"""Empacota app.html + biblioteca/ em um unico arquivo: dist/index.html."""
import base64
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(BASE, "biblioteca", "catalogo.json"), encoding="utf-8"))
glb = {m["id"]: base64.b64encode(open(os.path.join(BASE, "biblioteca", m["id"] + ".glb"), "rb").read()).decode()
       for m in cat}
html = open(os.path.join(BASE, "app.html"), encoding="utf-8").read()
html = html.replace("/*__CATALOGO__*/[]", json.dumps(cat, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*__GLB__*/{}", json.dumps(glb, separators=(",", ":")))
os.makedirs(os.path.join(BASE, "dist"), exist_ok=True)
out = os.path.join(BASE, "dist", "index.html")
open(out, "w", encoding="utf-8").write(html)
print(out, round(os.path.getsize(out) / 1e6, 2), "MB")
