"""Autoria, licença e marca d'água comuns a todo o material da Banquinha Vira-Voto."""
import io, json
from pathlib import Path
from urllib.parse import quote

import qrcode, qrcode.image.svg

B = Path(__file__).parent
AUTOR = "Prof. Bruno Chapadeiro"
IG = "@brunochapadeiro"
IG_URL = "https://instagram.com/brunochapadeiro"
LIC = "CC BY-NC-SA 4.0"
LIC_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br"
LIC_CURTA = "Pode copiar, imprimir e adaptar, sem fins comerciais, com crédito e a mesma licença."
LIC_TXT = (f"© 2026 {AUTOR}. Licença Creative Commons {LIC}: você pode copiar, imprimir, compartilhar e adaptar "
           f"este material, sem fins comerciais, desde que cite {AUTOR} ({IG}) e distribua o resultado sob a mesma licença.")
QUIZ = "https://claude.ai/artifact/2gjCy8t4escdJPcuaYQcwf"
TABLET = "https://claude.ai/artifact/4yJsk6hwXfsbEjXwj8JyKi"
HUB = "https://claude.ai/artifact/6RSdWwaWbtrtMnkK4ii9gq"
GAMES_ARTEFATO = "https://claude.ai/artifact/RVDCxdyzLw9Ncxv53KQXaS"
FLIPER = "https://jogaviravoto.brunochapadeiro.workers.dev/"  # site dos Games Vira-Voto (Cloudflare)

ALPHA_WM = 0.07
_IC = json.loads((B / "icons.json").read_text())
_NAMES = {"cc": "faCreativeCommons", "by": "faCreativeCommonsBy", "nc": "faCreativeCommonsNc",
          "sa": "faCreativeCommonsSa", "ig": "faInstagram", "wa": "faWhatsapp"}


def icon(name, cls="ic", label=None):
    d = _IC[_NAMES[name]]
    a = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 {d["w"]} {d["h"]}" {a}><path fill="currentColor" d="{d["d"]}"/></svg>'


def cc_icons(cls="ic"):
    """Os quatro ícones oficiais da licença (cc, by, nc, sa)."""
    return "".join(icon(n, cls) for n in ("cc", "by", "nc", "sa"))


def selo_html(cls="selo"):
    """Selo compacto: ícones + 'CC BY-NC-SA 4.0', com link para a licença."""
    return (f'<a class="{cls}" href="{LIC_URL}" title="Licença Creative Commons {LIC}">'
            f'<span class="selo-ic">{cc_icons()}</span><span class="selo-tx">{LIC}</span></a>')


def qr_svg(url, cls="qr"):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    buf = io.BytesIO(); img.save(buf)
    s = buf.getvalue().decode()
    s = s[s.index("<svg"):]
    return s.replace("<svg ", f'<svg class="{cls}" ', 1)


def wm_tile_uri(rgba="rgba(20,24,30,.055)", size=360):
    """Ladrilho SVG com o nome em diagonal, para fundo de página web."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">'
           f'<text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" '
           f'transform="rotate(-30 {size/2} {size/2})" font-family="Arial, sans-serif" font-weight="700" '
           f'font-size="22" fill="{rgba}">{AUTOR}</text></svg>')
    return "url(\"data:image/svg+xml," + quote(svg) + "\")"


# ---------- carimbo de PDF: marca d'água, selo CC e botão do Instagram em toda página ----------
def stamp_pdf(src, dst=None, alpha=ALPHA_WM, edge=True, layout="edge", rotulo=""):
    """Carimba cada página: marca d'água diagonal + faixa vertical na borda direita com o selo CC (link para a
    licença), o crédito e o botão "Siga @brunochapadeiro" (link para o Instagram). Mantém as marcações de
    acessibilidade do PDF (clone_from), marca o carimbo como artefato e descreve os links para leitores de tela."""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, TextStringObject
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader

    try:
        pdfmetrics.registerFont(TTFont("InterSB", str(B / "fonts/Inter-SemiBold.ttf")))
        pdfmetrics.registerFont(TTFont("InterB", str(B / "fonts/Inter-Bold.ttf")))
    except Exception:
        pass
    dst = dst or src
    wr = PdfWriter(clone_from=str(src))
    def _badge(nome):  # versão leve (cerca de 400 dpi no tamanho impresso)
        f = B / "badges" / f"{nome}.png"
        if not f.exists():
            return None
        from PIL import Image as _I
        im = _I.open(f); im = im.resize((round(im.width * 72 / im.height), 72), _I.LANCZOS)
        bio = io.BytesIO(); im.save(bio, "PNG", optimize=True); bio.seek(0)
        return ImageReader(bio)
    cc_img, ig_img = _badge("cc"), _badge("ig")
    DESC = {LIC_URL: f"Licença Creative Commons {LIC}", IG_URL: f"Instagram de {AUTOR}, {IG}"}
    for page in wr.pages:
        w = float(page.mediabox.width); h = float(page.mediabox.height)
        buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(w, h))
        c._code.append("/Artifact BMC")  # leitor de tela ignora o carimbo
        c.saveState(); c.setFillColorRGB(0.1, 0.12, 0.15, alpha=alpha); c.setFont("InterB", 15)
        step_x, step_y = 92 * mm, 46 * mm
        c.translate(w / 2, h / 2); c.rotate(32)
        span = int(max(w, h) / step_y) + 3
        for j in range(-span, span + 1):
            off = (j % 2) * step_x / 2
            for i in range(-span, span + 1):
                c.drawCentredString(i * step_x + off, j * step_y, AUTOR)
        c.restoreState()
        links = []
        if layout == "bottom":
            # rodapé horizontal: [selo CC]  © autor · rótulo · p. X/Y  [Siga @brunochapadeiro]
            pequeno = w < 400
            H = (3.7 if pequeno else 4.6) * mm
            fs = 5.6 if pequeno else 7.2
            num = wr.pages.index(page) + 1 if False else None
            txt = f"© {AUTOR}" + (f" · {rotulo}" if rotulo and not pequeno else "") + " · p. {p}/{t}"
            items = []
            if cc_img: iw, ih = cc_img.getSize(); items.append(("img", cc_img, LIC_URL, H * iw / ih))
            items.append(("txt", txt, None, 0))
            if ig_img: iw, ih = ig_img.getSize(); items.append(("img", ig_img, IG_URL, H * iw / ih))
            _foot.append((page, w, h, H, fs, items))
        elif edge:
            H = 4.4 * mm  # altura dos selos (atravessando a borda)
            txt = f"© {AUTOR}"
            fs = 6.4
            tw = pdfmetrics.stringWidth(txt, "InterSB", fs)
            parts = []
            if cc_img: parts.append(("img", cc_img, LIC_URL))
            parts.append(("txt", txt, None))
            if ig_img: parts.append(("img", ig_img, IG_URL))
            gap = 2.2 * mm
            lens = []
            for k, obj, _ in parts:
                if k == "img":
                    iw, ih = obj.getSize(); lens.append(H * iw / ih)
                else:
                    lens.append(tw)
            total = sum(lens) + gap * (len(parts) - 1)
            if total > h - 12 * mm:  # página pequena: diminui tudo
                f = (h - 12 * mm) / total; H *= f; fs *= f; gap *= f
                lens = [l * f for l in lens]; tw *= f; total *= f
            x = w - 3.6 * mm; yc = h / 2
            c.saveState(); c.translate(x, yc); c.rotate(90)
            pos = -total / 2
            for (k, obj, url), L in zip(parts, lens):
                if k == "img":
                    c.drawImage(obj, pos, -H / 2, L, H, mask="auto")
                    links.append((url, (x - H / 2, yc + pos, x + H / 2, yc + pos + L)))
                else:
                    c.setFillColorRGB(0.25, 0.27, 0.3); c.setFont("InterSB", fs)
                    c.drawString(pos, -fs * 0.35, obj)
                pos += L + gap
            c.restoreState()
        c._code.append("EMC")
        for url, rect in links:
            c.linkURL(url, rect, relative=0, thickness=0)
        c.save(); buf.seek(0)
        ov = PdfReader(buf).pages[0]
        page.merge_page(ov)
        for a in page.get("/Annots", []) or []:
            o = a.get_object()
            uri = o.get("/A", {}).get("/URI") if o.get("/A") else None
            if uri in DESC and "/Contents" not in o:
                o[NameObject("/Contents")] = TextStringObject(DESC[uri])
    try:
        wr.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    except Exception:
        pass
    with open(dst, "wb") as fh:
        wr.write(fh)
    return dst

IA = "Arte e programação feitas com auxílio de inteligência artificial (IA). Os fatos têm fonte em cada resposta."
IA_CURTA = "Arte feita com auxílio de IA"

QUIZ_PUB = FLIPER + "quiz"        # quiz no site público (qualquer pessoa abre)
BARALHO_PUB = FLIPER + "baralho"  # baralho para tablet no site público
KIT_PUB = FLIPER + "kit"          # plano e kit de postagem

CONTADOR = FLIPER + "api/placar"  # placar público dentro do próprio site (Worker jogaviravoto + Durable Object)
