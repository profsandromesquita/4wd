"""Gera a biblioteca de pecas do carro 4WD: GLB (web), STEP (CAD) e meta.json.

Unidades: mm. Eixo Z para cima. Uso: python gerar_pecas.py
"""
import json
import os

import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca")

# ---------------------------------------------------------------- cores
C = {
    "pcb_azul": (0.05, 0.25, 0.55, 1), "pcb_verde": (0.10, 0.42, 0.25, 1),
    "preto": (0.07, 0.07, 0.08, 1), "prata": (0.75, 0.76, 0.78, 1),
    "ouro": (0.83, 0.68, 0.22, 1), "amarelo": (0.98, 0.80, 0.08, 1),
    "branco": (0.93, 0.93, 0.90, 1), "vermelho": (0.80, 0.10, 0.10, 1),
    "azul_borne": (0.10, 0.45, 0.85, 1), "azul_bat": (0.15, 0.50, 0.80, 1),
    "latao": (0.78, 0.60, 0.25, 1), "cinza": (0.30, 0.31, 0.33, 1),
    "acrilico": (0.72, 0.86, 0.92, 0.45), "verde": (0.15, 0.70, 0.25, 1),
    "pneu": (0.09, 0.09, 0.10, 1),
}


# ---------------------------------------------------------------- helpers
def box(x0, y0, z0, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def cbox(cx, cy, cz, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz).translate((cx, cy, cz))


def cyl(x, y, z0, d, h):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def ycyl(d, y0, y1, x=0, z=0):
    """Cilindro com eixo em Y."""
    s = cq.Workplane("XY").circle(d / 2).extrude(y1 - y0)
    return s.rotate((0, 0, 0), (1, 0, 0), -90).translate((x, y0, z))


def xcyl(d, x0, x1, y=0, z=0):
    s = cq.Workplane("XY").circle(d / 2).extrude(x1 - x0)
    return s.rotate((0, 0, 0), (0, 1, 0), 90).translate((x0, y, z))


def drill(s, pts, d, z0=-5, h=60):
    cutter = cq.Workplane("XY").pushPoints(pts).circle(d / 2).extrude(h).translate((0, 0, z0))
    return s.cut(cutter)


def union(items):
    r = items[0]
    for i in items[1:]:
        r = r.union(i)
    return r


def pins(pts, z0, h, w=0.64):
    return union([cbox(x, y, z0 + h / 2, w, w, h) for x, y in pts])


def anc(i, tipo, x, y, z):
    return {"id": i, "tipo": tipo, "pos": [round(x, 3), round(y, 3), round(z, 3)]}


UNO_OUTLINE = [(0, 0), (64.52, 0), (66.04, 1.52), (66.04, 12.95), (68.58, 15.49),
               (68.58, 48.26), (66.04, 50.8), (66.04, 53.34), (0, 53.34)]
UNO_HOLES = [(13.97, 2.54), (15.24, 50.8), (66.04, 7.62), (66.04, 35.56)]
# (x0, x1, y) de cada barra de pinos do padrao Uno
UNO_HEADERS = [(44.45, 64.77, 50.8), (17.526, 42.926, 50.8), (26.67, 46.99, 2.54), (49.53, 64.77, 2.54)]


# ---------------------------------------------------------------- pecas
def arduino_uno():
    pcb = drill(cq.Workplane("XY").polyline(UNO_OUTLINE).close().extrude(1.6), UNO_HOLES, 3.2)
    t = 1.6
    headers = union([box(x0, y - 1.27, t, x1 - x0, 2.54, 8.5) for x0, x1, y in UNO_HEADERS])
    pretos = union([
        box(-1.8, 3.2, t, 13.3, 9.0, 10.9),          # jack P4
        box(28.5, 10.2, t, 35.6, 7.6, 6.5),          # ATmega328P + soquete
        box(20.0, 33.0, t, 6.0, 6.0, 1.0),           # ATmega16U2
        box(62.23, 25.4, t, 5.08, 7.62, 2.5),        # base ICSP
        box(13.0, 14.5, t, 6.5, 6.5, 2.3),           # regulador
    ])
    pratas = union([
        box(-6.2, 32.0, t, 16.0, 12.0, 10.9),        # USB-B
        cyl(17.5, 8.0, t, 6.3, 6.0), cyl(24.5, 8.0, t, 6.3, 6.0),
        box(22.0, 25.5, t, 11.0, 4.6, 3.5),          # cristal
        box(3.0, 46.5, t, 6.0, 6.0, 3.4),            # botao reset
    ])
    ouro = pins([(63.5 + dx, 26.67 + dy) for dx in (0, 2.54) for dy in (0, 2.54, 5.08)], t, 8.5)
    botao = cyl(6.0, 49.5, t + 3.4, 3.2, 1.0)
    a = [anc(f"furo{i+1}", "m3", x, y, 0) for i, (x, y) in enumerate(UNO_HOLES)]
    a.append(anc("soquete-shield", "uno-socket", 0, 0, t + 8.5))
    return [("pcb", pcb, "pcb_azul"), ("barras", headers, "preto"), ("ci", pretos, "preto"),
            ("metal", pratas, "prata"), ("nc_icsp", ouro, "ouro"), ("reset", botao, "vermelho")], a


def motor_shield():
    pcb = drill(cq.Workplane("XY").polyline(UNO_OUTLINE).close().extrude(1.6), UNO_HOLES[:2], 3.2)
    t = 1.6
    espac = union([box(x0, y - 1.27, -2.5, x1 - x0, 2.54, 2.5) for x0, x1, y in UNO_HEADERS])
    pinos = union([box(x0 + 0.9, y - 0.32, -11.0, x1 - x0 - 1.8, 0.64, 8.5) for x0, x1, y in UNO_HEADERS])
    cis = union([box(x, 19.0, t, 7.2, 20.0, 7.0) for x in (11.5, 29.0, 47.5)]
                + [box(1.0, 45.0, t, 7.62, 5.08, 2.5)])
    bornes = union([box(0.5, 9.0, t, 7.6, 21.0, 10.0), box(60.4, 15.0, t, 7.6, 21.0, 10.0),
                    box(9.0, 0.5, t, 10.2, 7.6, 10.0)])
    caps = union([cyl(x, y, t, 5.0, 7.0) for x, y in ((24.0, 44.5), (57.0, 44.5), (24.5, 14.0), (42.5, 12.0))])
    servo = pins([(2.27 + 2.54 * i, 46.27 + 2.54 * j) for i in range(3) for j in range(2)], t, 8.5)
    led = cyl(40.0, 20.0, t, 3.0, 4.5)
    reset = box(2.0, 1.5, t, 6.0, 6.0, 4.0)
    a = [anc("pinos-uno", "uno-plug", 0, 0, -2.5)]
    return [("pcb", pcb, "pcb_azul"), ("espacadores", espac, "preto"), ("nc_pinos", pinos, "ouro"),
            ("ci", cis, "preto"), ("bornes", bornes, "azul_borne"), ("caps", caps, "prata"),
            ("nc_servo", servo, "ouro"), ("led", led, "verde"), ("reset", reset, "prata")], a


def lm2596():
    holes = [(6.6, 18.4), (36.6, 2.6)]
    t = 1.6
    pcb = drill(box(0, 0, 0, 43.2, 21.0, t), holes, 3.0)
    caps = union([cyl(5.5, 7.5, t, 8.0, 10.5), cyl(37.7, 13.5, t, 8.0, 10.5)])
    escuros = union([box(12.0, 6.0, t, 10.2, 9.0, 4.5), box(20.6, 2.0, t, 12.0, 12.0, 7.0),
                     box(8.5, 1.0, t, 4.5, 2.6, 2.3)])
    aba = box(12.0, 15.0, t, 10.2, 4.5, 1.3)
    trim = box(23.5, 15.6, t, 9.5, 4.8, 10.0)
    paraf = cyl(24.8, 18.0, t + 10.0, 2.3, 1.2)
    a = [anc(f"furo{i+1}", "m3", x, y, 0) for i, (x, y) in enumerate(holes)]
    return [("pcb", pcb, "pcb_azul"), ("caps", caps, "prata"), ("ci", escuros, "cinza"),
            ("aba", aba, "prata"), ("trimpot", trim, "azul_borne"), ("ajuste", paraf, "latao")], a


def motor_passo():
    corpo = cyl(0, 0, 0, 28.0, 19.0)
    orelha = cbox(0, 0, 18.6, 35.0, 7.0, 0.8).union(cyl(17.5, 0, 18.2, 7.0, 0.8)).union(cyl(-17.5, 0, 18.2, 7.0, 0.8))
    orelha = drill(orelha, [(17.5, 0), (-17.5, 0)], 4.2)
    corpo = corpo.union(orelha).union(cyl(0, 8.0, 19.0, 9.0, 1.5))
    eixo = cyl(0, 8.0, 20.5, 5.0, 4.0).union(cyl(0, 8.0, 24.5, 5.0, 6.0).intersect(cbox(0, 8.0, 27.5, 3.0, 6.0, 6.0)))
    tampa = box(-7.3, -17.0, 0, 14.6, 6.0, 16.5)
    a = [anc("orelha1", "m3", 17.5, 0, 19.0), anc("orelha2", "m3", -17.5, 0, 19.0),
         anc("orelha1b", "m3", 17.5, 0, 18.2), anc("orelha2b", "m3", -17.5, 0, 18.2)]
    return [("corpo", corpo, "prata"), ("eixo", eixo, "latao"), ("tampa", tampa, "azul_bat")], a


def driver_uln2003():
    holes = [(2.5, 2.5), (32.5, 2.5), (2.5, 29.5), (32.5, 29.5)]
    t = 1.6
    pcb = drill(box(0, 0, 0, 35.0, 32.0, t), holes, 3.0)
    ci = union([box(7.5, 9.5, t, 20.0, 7.0, 5.5), box(9.5, 1.0, t, 10.16, 2.54, 2.5), box(27.0, 14.0, t, 2.54, 10.16, 2.5)])
    con = box(10.0, 22.5, t, 14.9, 5.8, 7.0)
    leds = union([cyl(9.0 + 3.6 * i, 19.0, t, 3.0, 5.0) for i in range(4)])
    pin = pins([(10.77 + 2.54 * i, 2.27) for i in range(4)] + [(28.27, 15.27 + 2.54 * i) for i in range(4)], t, 8.5)
    a = [anc(f"furo{i+1}", "m3", x, y, 0) for i, (x, y) in enumerate(holes)]
    return [("pcb", pcb, "pcb_verde"), ("ci", ci, "preto"), ("conector", con, "branco"),
            ("leds", leds, "vermelho"), ("nc_pinos", pin, "ouro")], a


def hc_sr04():
    holes = [(1.5, 1.5), (43.5, 1.5), (1.5, 18.5), (43.5, 18.5)]
    t = 1.6
    pcb = drill(box(0, 0, 0, 45.0, 20.0, t), holes, 2.0)
    tr = union([cyl(9.5, 10.0, t, 16.0, 12.0), cyl(35.5, 10.0, t, 16.0, 12.0), box(17.0, 14.8, t, 11.0, 4.6, 3.5)])
    tela = union([cyl(9.5, 10.0, t + 12.0, 12.5, 0.3), cyl(35.5, 10.0, t + 12.0, 12.5, 0.3)])
    base = box(17.42, 0.0, -2.54, 10.16, 2.54, 2.54)
    pin = union([cbox(18.69 + 2.54 * i, -2.5, -1.27, 0.64, 7.0, 0.64) for i in range(4)])
    a = [anc(f"furo{i+1}", "m2", x, y, 0) for i, (x, y) in enumerate(holes)]
    return [("pcb", pcb, "pcb_azul"), ("transdutores", tr, "prata"), ("tela", tela, "cinza"),
            ("base", base, "preto"), ("nc_pinos", pin, "ouro")], a


def chave():
    flange = cbox(0, 0, 1.0, 15.0, 10.5, 2.0)
    corpo = cbox(0, 0, -5.75, 13.0, 8.5, 11.5)
    tecla = cbox(0, 0, 2.6, 11.0, 7.0, 2.2).rotate((0, 0, 2), (0, 1, 2), 9)
    term = union([cbox(x, 0, -15.0, 0.8, 4.8, 7.0) for x in (-3.5, 3.5)])
    return [("corpo", flange.union(corpo), "preto"), ("tecla", tecla, "vermelho"), ("nc_terminais", term, "prata")], []


def bateria():
    corpo = xcyl(18.4, -32.5, 32.0)
    polo = xcyl(11.0, 32.0, 32.5).union(xcyl(18.4, -32.5, -32.3))
    return [("corpo", corpo, "azul_bat"), ("polos", polo, "prata")], [anc("centro", "cel-18650", 0, 0, 0)]


def suporte_bateria():
    L, W, H, w, f = 77.0, 41.0, 19.0, 1.3, 1.5
    bay = (W - 3 * w) / 2
    corpo = cbox(0, 0, H / 2, L, W, H)
    for s in (1, -1):
        corpo = corpo.cut(cbox(0, s * (bay / 2 + w / 2), f + H / 2, L - 2 * w, bay, H))
    corpo = corpo.cut(cbox(26, 0, f + H / 2, 22, w + 0.2, H)).cut(cbox(-26, 0, f + H / 2, 22, w + 0.2, H))
    corpo = drill(corpo, [(27, 0), (-27, 0)], 3.2)
    yc, zc = bay / 2 + w / 2, f + 9.3
    molas = union([xcyl(8.0, 29.0, L / 2 - w, -yc, zc), xcyl(8.0, -(L / 2 - w), -29.0, yc, zc),
                   cbox(-(L / 2 - w) + 0.5, -yc, zc, 1.0, 8.0, 10.0), cbox((L / 2 - w) - 0.5, yc, zc, 1.0, 8.0, 10.0)])
    fio_v = xcyl(1.6, L / 2, L / 2 + 12, -yc, 4.0)
    fio_p = xcyl(1.6, L / 2, L / 2 + 12, yc, 4.0)
    a = [anc("celula1", "slot-18650", -3.5, -yc, zc), anc("celula2", "slot-18650", 3.5, yc, zc),
         anc("furo1", "m3", 27, 0, 0), anc("furo2", "m3", -27, 0, 0),
         anc("furo1t", "m3", 27, 0, f), anc("furo2t", "m3", -27, 0, f)]
    return [("corpo", corpo, "preto"), ("nc_contatos", molas, "prata"),
            ("nc_fio_pos", fio_v, "vermelho"), ("nc_fio_neg", fio_p, "preto")], a


def motor_tt():
    cx = cq.Workplane("XY").box(37.25, 18.8, 22.5, centered=False).translate((-11.25, -9.4, -11.25))
    cx = cx.edges("|Y and <X").fillet(8.0)
    furos = ycyl(3.0, -15, 15, 20.5, 8.75).union(ycyl(3.0, -15, 15, 20.5, -8.75))
    aba = cbox(-13.8, 0, 0, 5.4, 2.5, 5.0).cut(ycyl(2.2, -3, 3, -14.2, 0))
    cx = cx.cut(furos).union(aba).union(ycyl(7.5, -10.4, 10.4))
    lata = xcyl(20.0, 26.0, 53.0).intersect(cbox(39.5, 0, 0, 27.0, 15.4, 20.0))
    tampa = xcyl(10.0, 53.0, 58.5)
    eixo = ycyl(5.4, -18.4, 18.4).intersect(cbox(0, 0, 0, 3.7, 40, 6))
    a = [anc("eixo+", "eixo-tt", 0, 13.9, 0), anc("eixo-", "eixo-tt", 0, -13.9, 0)]
    for sy in (1, -1):
        for sz in (1, -1):
            a.append(anc(f"furo{'+' if sy > 0 else '-'}{'s' if sz > 0 else 'i'}", "m3", 20.5, sy * 9.4, sz * 8.75))
    return [("redutor", cx, "amarelo"), ("motor", lata, "prata"), ("tampa", tampa, "preto"),
            ("nc_eixo", eixo, "branco")], a


def roda():
    pneu = ycyl(65.0, 0, 26.0).cut(ycyl(52.0, -1, 27))
    try:
        pneu = pneu.edges(cq.selectors.RadiusNthSelector(1)).fillet(3.0)
    except Exception:
        pass
    aro = ycyl(52.0, 1.0, 25.0).cut(ycyl(45.0, 0, 26))
    disco = ycyl(45.0, 13.0, 16.0)
    import math
    for k in range(5):
        ang = math.radians(90 + 72 * k)
        disco = disco.cut(ycyl(13.0, 10, 20, 14.5 * math.cos(ang), 14.5 * math.sin(ang)))
    cubo = ycyl(14.0, 0, 19.0).cut(ycyl(5.6, -1, 13.0))
    return [("pneu", pneu, "pneu"), ("aro", aro.union(disco).union(cubo), "amarelo")], [anc("cubo", "cubo-tt", 0, 0, 0)]


def disco_encoder():
    import math
    d = ycyl(26.0, 3.0, 4.2)
    for k in range(20):
        slot = cbox(10.2, 3.6, 0, 3.6, 3.0, 1.5).rotate((0, 0, 0), (0, 1, 0), 18 * k)
        d = d.cut(slot)
    d = d.union(ycyl(9.0, 0, 4.5)).cut(ycyl(5.6, -1, 6))
    return [("disco", d, "preto")], [anc("cubo", "cubo-tt", 0, 0, 0)]


MOTOR_X, MOTOR_FURO_X = 68.0, 47.5
Y_SUP_EXT, Y_SUP_INT, Y_ENC = 48.5, 26.7, 20.1
ESPACADORES = [(112, 56), (112, -56), (-112, 56), (-112, -56), (0, 68), (0, -68)]


def placa(superior):
    L, W, T = 256.0, 150.0, 3.0
    p = cq.Workplane("XY").rect(L, W).extrude(T).edges("|Z").fillet(35.0)
    a = []
    for sx in (1, -1):
        for sy in (1, -1):
            recorte = cq.Workplane("XY").rect(72, 26).extrude(T + 2).edges("|Z").fillet(4.0)
            p = p.cut(recorte.translate((sx * MOTOR_X, sy * 63, -1)))
    furos = list(ESPACADORES)
    if superior:
        grade = [(x, y) for x in range(-80, 81, 20) for y in (-40, -20, 0, 20, 40) if not (x == 0 and y == 0)]
    else:
        grade = [(x, y) for x in (-80, -40, 0, 40, 80) for y in (-20, 20)]
        for sx in (1, -1):
            for sy in (1, -1):
                tag = f"{'F' if sx > 0 else 'T'}{'E' if sy > 0 else 'D'}"
                p = p.cut(cbox(sx * MOTOR_FURO_X, sy * Y_SUP_INT, T / 2, 6.4, 3.3, T + 2))
                p = p.cut(cbox(sx * MOTOR_FURO_X, sy * (Y_SUP_EXT + 1.0), T / 2, 6.4, 5.3, T + 2))
                p = p.cut(cbox(sx * MOTOR_X, sy * Y_ENC, T / 2, 16.0, 3.2, T + 2))
                a.append(anc(f"rasgo-int-{tag}", "rasgo", sx * MOTOR_FURO_X, sy * Y_SUP_INT, T))
                a.append(anc(f"rasgo-ext-{tag}", "rasgo", sx * MOTOR_FURO_X, sy * Y_SUP_EXT, T))
    p = drill(p, furos + grade, 3.2)
    p = drill(p, [(100, 0), (-100, 0)], 16.0)
    for sx in (1, -1):
        p = p.cut(cq.Workplane("XY").slot2D(40, 5, 90).extrude(T + 2).translate((sx * 120, 0, -1)))
    p = p.cut(cq.Workplane("XY").rect(24, 12).extrude(T + 2).edges("|Z").fillet(3).translate((0, 0, -1)))
    for i, (x, y) in enumerate(furos):
        a += [anc(f"espacador{i+1}-cima", "m3", x, y, T), anc(f"espacador{i+1}-baixo", "m3", x, y, 0)]
    for i, (x, y) in enumerate(grade):
        a += [anc(f"furo{i+1}-cima", "m3", x, y, T), anc(f"furo{i+1}-baixo", "m3", x, y, 0)]
    return [("placa", p, "acrilico")], a


def suporte_motor():
    s = cbox(0, 0, 11.75, 12.0, 3.0, 23.5).union(cbox(0, 0, -1.5, 6.0, 3.0, 3.0))
    s = s.cut(ycyl(3.2, -3, 3, 0, 2.5)).cut(ycyl(3.2, -3, 3, 0, 20.0))
    a = [anc("aba", "aba", 0, 0, 0)]
    for z, n in ((2.5, "i"), (20.0, "s")):
        a += [anc(f"furo-{n}+", "m3", 0, 1.5, z), anc(f"furo-{n}-", "m3", 0, -1.5, z)]
    return [("suporte", s, "acrilico")], a


def espacador():
    s = cq.Workplane("XY").polygon(6, 6.35).extrude(30.0).cut(cyl(0, 0, -1, 3.0, 32))
    return [("espacador", s, "latao")], [anc("base", "m3", 0, 0, 0), anc("topo", "m3", 0, 0, 30.0)]


def parafuso(comp):
    def f():
        s = cyl(0, 0, 0, 5.6, 2.0).union(cyl(0, 0, -comp, 2.9, comp))
        s = s.cut(cbox(0, 0, 1.6, 3.6, 0.8, 1.0)).cut(cbox(0, 0, 1.6, 0.8, 3.6, 1.0))
        return [("parafuso", s, "prata")], [anc("cabeca", "m3", 0, 0, 0)]
    return f


def porca():
    s = cq.Workplane("XY").polygon(6, 6.35).extrude(2.4).cut(cyl(0, 0, -1, 3.0, 5))
    return [("porca", s, "prata")], [anc("face1", "m3", 0, 0, 0), anc("face2", "m3", 0, 0, 2.4)]


def jumpers():
    cores = [(0.45, 0.25, 0.10), (0.85, 0.10, 0.10), (0.95, 0.50, 0.10), (0.95, 0.85, 0.10), (0.15, 0.65, 0.25),
             (0.10, 0.35, 0.85), (0.55, 0.25, 0.70), (0.55, 0.55, 0.55), (0.95, 0.95, 0.95), (0.08, 0.08, 0.08)]
    out, caps, pin = [], [], []
    for i, c in enumerate(cores):
        y = 2.54 * i
        out.append((f"fio{i}", box(14, y - 0.65, 0.6, 172, 1.3, 1.3), c + (1,)))
        caps += [box(0, y - 1.2, 0, 14, 2.4, 2.5), box(186, y - 1.2, 0, 14, 2.4, 2.5)]
        pin.append(cbox(-3, y, 1.25, 6, 0.64, 0.64))
    out += [("conectores", union(caps), "preto"), ("nc_pinos", union(pin), "prata")]
    return out, []


def modulo_sd():
    holes = [(2.2, 2.2), (2.2, 21.8)]
    t = 1.6
    pcb = drill(box(0, 0, 0, 42.0, 24.0, t), holes, 2.2)
    soq = box(1.0, 5.0, t, 14.5, 14.0, 1.9)
    ci = union([box(20.0, 4.0, t, 6.5, 3.5, 1.6), box(22.0, 13.0, t, 5.0, 6.5, 1.2),
                box(36.9, 4.38, t, 2.54, 15.24, 2.54)])
    pin = union([cbox(43.0, 5.65 + 2.54 * i, t + 1.27, 7.0, 0.64, 0.64) for i in range(6)])
    a = [anc(f"furo{i+1}", "m2", x, y, 0) for i, (x, y) in enumerate(holes)]
    a.append(anc("slot", "sd-slot", 4.5, 12.0, t + 0.95))
    return [("pcb", pcb, "pcb_azul"), ("nc_soquete", soq, "prata"), ("ci", ci, "preto"), ("nc_pinos", pin, "ouro")], a


def cartao_sd():
    s = cbox(0, 0, 0, 15.0, 11.0, 1.0).cut(cbox(4.5, 5.5, 0, 6.0, 1.6, 2.0))
    cont = union([cbox(-6.0, -4.2 + 1.1 * i, 0.5, 2.5, 0.7, 0.06) for i in range(8)])
    return [("cartao", s, "preto"), ("nc_contatos", cont, "ouro")], [anc("centro", "sd-card", 0, 0, 0)]


# ---------------------------------------------------------------- catalogo
DS = "Dimensoes oficiais (desenho mecanico do fabricante)."
TIP = "Medidas tipicas de mercado; confira com paquimetro na peca real."
PECAS = [
    ("arduino_uno", "Arduino Uno R3", "Eletrônica", 1, arduino_uno, False,
     "Placa controladora: o cérebro do carro. Recebe os sensores e comanda os motores.", DS),
    ("motor_shield_l293d", "Motor Shield L293D", "Eletrônica", 1, motor_shield, True,
     "Encaixa sobre o Arduino e fornece a corrente para até 4 motores DC (bornes M1 a M4).",
     "Contorno e pinos no padrão Uno (oficial); posição dos componentes aproximada."),
    ("lm2596", "Regulador LM2596", "Eletrônica", 1, lm2596, True,
     "Conversor step-down: reduz a tensão das baterias para um valor estável (ex.: 5 V).",
     "Placa 43,2 x 21 x 14 mm (confirmado em datasheet de módulo); posição dos furos aproximada."),
    ("motor_28byj48", "Motor de passo 28BYJ-48", "Motores", 1, motor_passo, False,
     "Motor de passo com redução: gira em ângulos precisos. Útil para apontar o sensor.",
     "Datasheet 28BYJ-48: corpo 28 mm, furos a 35 mm, eixo 5 mm deslocado 8 mm."),
    ("driver_uln2003", "Driver ULN2003", "Eletrônica", 1, driver_uln2003, True,
     "Placa que amplifica os sinais do Arduino para acionar o motor de passo.", TIP),
    ("hc_sr04", "Sensor ultrassônico HC-SR04", "Sensores", 1, hc_sr04, True,
     "Mede distância por eco de ultrassom (2 a 400 cm). Um transdutor emite, o outro recebe.",
     "Placa 45 x 20 mm, transdutores de 16 mm a 26 mm entre centros; furos aproximados."),
    ("chave_kcd11", "Chave liga/desliga KCD11", "Energia", 1, chave, True,
     "Interruptor geral: corta a alimentação das baterias.", TIP),
    ("bateria_18650", "Bateria 18650", "Energia", 2, bateria, False,
     "Célula de íon-lítio de 3,7 V. Duas em série fornecem cerca de 7,4 V.",
     "Padrão 18650: 18 mm de diâmetro por 65 mm de comprimento."),
    ("suporte_2x18650", "Suporte para 2 baterias 18650", "Energia", 1, suporte_bateria, True,
     "Aloja as duas células e as liga em série.", "Varia por fabricante (74 a 80 mm de comprimento); modelado com 77 x 41 x 19 mm."),
    ("motor_tt", "Motor DC TT com redução 1:48", "Motores", 4, motor_tt, True,
     "Motor amarelo com caixa de redução. Cada roda tem o seu.",
     "Medidas típicas: 70 x 22,5 x 18,8 mm, furos de fixação a 17,5 mm."),
    ("roda_65mm", "Roda 65 mm", "Mecânica", 4, roda, True,
     "Roda com pneu de borracha; encaixa por pressão no eixo do motor TT.", "Diâmetro 65 mm, largura 26 mm (típico)."),
    ("disco_encoder", "Disco encoder", "Mecânica", 4, disco_encoder, True,
     "Disco com 20 fendas; com um sensor óptico permite medir a rotação da roda.", TIP),
    ("placa_inferior", "Placa inferior do chassi", "Chassi", 1, lambda: placa(False), True,
     "Base de acrílico onde ficam os 4 motores.",
     "Contorno 256 x 150 mm e 30 mm entre placas conforme o anúncio; furação estimada pela foto."),
    ("placa_superior", "Placa superior do chassi", "Chassi", 1, lambda: placa(True), True,
     "Tampa de acrílico que recebe a eletrônica e as baterias.",
     "Contorno 256 x 150 mm conforme o anúncio; furação estimada pela foto."),
    ("suporte_motor", "Suporte de motor (acrílico)", "Chassi", 8, suporte_motor, True,
     "Prende o motor na placa inferior: dois por motor, um de cada lado.", "Estimado pela foto do kit."),
    ("espacador_m3x30", "Espaçador M3 x 30 mm", "Fixação", 6, espacador, False,
     "Coluna de latão que mantém as duas placas a 30 mm de distância.", "Sextavado 5,5 mm, rosca M3."),
    ("parafuso_m3x30", "Parafuso M3 x 30 mm", "Fixação", 8, parafuso(30.0), False,
     "Atravessa os dois suportes e o motor.", "Rosca M3 padrão."),
    ("parafuso_m3x6", "Parafuso M3 x 6 mm", "Fixação", 16, parafuso(6.0), False,
     "Fixa as placas nos espaçadores e os módulos no chassi.", "Rosca M3 padrão."),
    ("porca_m3", "Porca M3", "Fixação", 16, porca, False, "Trava os parafusos M3.", "Sextavada 5,5 mm x 2,4 mm."),
    ("jumpers", "Jumpers (fita com 10)", "Eletrônica", 4, jumpers, True,
     "Cabos de ligação entre os módulos e o Arduino. Na montagem real são flexíveis.", "Comprimento de 20 cm."),
    ("modulo_microsd", "Módulo leitor microSD", "Eletrônica", 1, modulo_sd, True,
     "Grava e lê dados no cartão de memória por SPI.", "Placa 42 x 24 mm; furos M2 aproximados."),
    ("cartao_microsd", "Cartão microSD", "Eletrônica", 1, cartao_sd, False,
     "Memória removível para registrar dados do carro.", "Padrão SD Association: 15 x 11 x 1 mm."),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    catalogo = []
    for pid, nome, cat, qtd, fn, aprox, desc, fonte in PECAS:
        solids, anchors = fn()
        asm = cq.Assembly(name=pid)
        bb = None
        for n, s, cor in solids:
            rgba = C[cor] if isinstance(cor, str) else cor
            asm.add(s, name=n, color=cq.Color(*rgba))
            b = s.val().BoundingBox()
            bb = b if bb is None else bb.add(b)
        asm.save(os.path.join(OUT, pid + ".glb"), tolerance=0.08, angularTolerance=0.35)
        asm.save(os.path.join(OUT, pid + ".step"))
        meta = {"id": pid, "nome": nome, "categoria": cat, "qtd_kit": qtd, "descricao": desc,
                "aproximado": aprox, "fonte": fonte,
                "dim": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                "bbox": [[round(bb.xmin, 2), round(bb.ymin, 2), round(bb.zmin, 2)],
                         [round(bb.xmax, 2), round(bb.ymax, 2), round(bb.zmax, 2)]],
                "encaixes": anchors}
        catalogo.append(meta)
        kb = os.path.getsize(os.path.join(OUT, pid + ".glb")) / 1024
        print(f"{pid:22s} {meta['dim']}  {kb:7.1f} KB  {len(anchors)} encaixes")
    with open(os.path.join(OUT, "catalogo.json"), "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
