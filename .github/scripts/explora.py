"""Explora arquivos baixados: tamanho, cabeçalho, linhas de exemplo e contagem (CSV, ZIP com CSV, JSON).
Uso: python3 explora.py <pasta de entrada> <pasta de saída>"""
import io, json, os, sys, zipfile
from pathlib import Path

ent, sai = Path(sys.argv[1]), Path(sys.argv[2])
sai.mkdir(parents=True, exist_ok=True)
rel = []


def le_txt(b):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return b.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", "replace"), "?"


def resumo_csv(nome, b):
    t, enc = le_txt(b)
    linhas = t.splitlines()
    rel.append(f"== {nome}  {len(b):,} bytes  enc={enc}  linhas={len(linhas):,}")
    for l in linhas[:3]:
        rel.append("   " + l[:700])


def resumo_json(nome, b):
    t, enc = le_txt(b)
    try:
        d = json.loads(t)
    except Exception as e:
        rel.append(f"== {nome}  {len(b):,} bytes  JSON inválido: {e}; início: {t[:300]!r}")
        return

    def forma(x, n=0):
        if n > 4:
            return "..."
        if isinstance(x, dict):
            return "{" + ", ".join(f"{k}: {forma(v, n + 1)}" for k, v in list(x.items())[:25]) + "}"
        if isinstance(x, list):
            return f"[{len(x)}× " + (forma(x[0], n + 1) if x else "") + "]"
        return type(x).__name__ + "=" + repr(x)[:60]
    rel.append(f"== {nome}  {len(b):,} bytes  JSON  {forma(d)[:3000]}")


for f in sorted(ent.iterdir()):
    b = f.read_bytes()
    if b[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(b))
        rel.append(f"== {f.name}  ZIP {len(b):,} bytes: {[(i.filename, i.file_size) for i in z.infolist()][:10]}")
        for i in z.infolist()[:2]:
            with z.open(i) as h:
                resumo_csv(f.name + "::" + i.filename, h.read(400_000) if i.file_size > 50_000_000 else h.read())
    elif b.lstrip()[:1] in (b"{", b"["):
        resumo_json(f.name, b)
    else:
        resumo_csv(f.name, b)

txt = "\n".join(rel)
(sai / "explora.txt").write_text(txt, encoding="utf-8")
print(txt[-60000:])
