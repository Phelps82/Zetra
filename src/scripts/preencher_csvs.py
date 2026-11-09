"""Preenche os CSVs do Zetra com o que as fontes abertas trouxeram.

Fontes:
- Paraibano 2025, jogos da 1ª fase: api-futebol.com.br (rodadas 2 a 7 e 9; rodadas 1 e 8 NÃO consultadas).
- Final 2025: Itatiaia (ida 1x0 sem data/estádio; volta 30/03/2025).
- 2024: classificação final da 1ª fase (Wikipédia) e 2 jogos citados.
- Artilharia 2026: Jornal da Paraíba (página "campeonato-paraibano-2026-artilharia").
"""
import csv
import os
from collections import defaultdict

OUT = "dados_zetra"
os.makedirs(OUT, exist_ok=True)

COLS_PARTIDAS = ["partida_id", "temporada", "fase", "rodada_ou_perna", "data", "mandante", "visitante",
                 "gols_mandante", "gols_visitante", "penaltis_mandante", "penaltis_visitante", "estadio",
                 "publico_total", "publico_pagante", "renda_bruta_rs", "observacao"]

BOT, CAM, TRE, SBR, SOU = "Botafogo-PB", "Campinense", "Treze", "Serra Branca", "Sousa"
NAC, ESP, POM, AUT, PIC = "Nacional de Patos", "Esporte de Patos", "Pombal", "Auto Esporte", "Picuiense"
JC, AMI, ALM, MAR = "José Cavalcanti", "Amigão", "Almeidão", "Marizão"

# (rodada, data, mandante, visitante, gm, gv, estadio)  -- estádio como informado pela fonte
J2025 = [
    (2, "2025-01-15", NAC, POM, 2, 1, JC), (2, "2025-01-15", BOT, ESP, 3, 0, ALM),
    (2, "2025-01-16", SOU, SBR, 2, 0, MAR), (2, "2025-01-22", AUT, CAM, 1, 1, ALM),
    (2, "2025-02-12", PIC, TRE, 2, 6, AMI),
    (3, "2025-01-18", AUT, BOT, 0, 1, ALM), (3, "2025-01-19", CAM, TRE, 2, 0, AMI),
    (3, "2025-01-19", ESP, SOU, 1, 3, JC), (3, "2025-01-20", SBR, POM, 2, 1, AMI),
    (3, "2025-01-22", NAC, PIC, 2, 2, JC),
    (4, "2025-01-25", POM, BOT, 1, 0, JC), (4, "2025-01-25", TRE, SBR, 1, 0, AMI),
    (4, "2025-01-26", AUT, SOU, 0, 0, ALM), (4, "2025-01-26", CAM, PIC, 6, 0, AMI),
    (4, "2025-01-26", ESP, NAC, 2, 2, JC),
    (5, "2025-01-29", PIC, POM, 0, 1, AMI), (5, "2025-01-29", BOT, SBR, 1, 1, ALM),
    (5, "2025-01-29", SOU, CAM, 2, 0, MAR), (5, "2025-01-30", TRE, ESP, 3, 0, AMI),
    (5, "2025-02-16", NAC, AUT, 3, 1, JC),
    (6, "2025-02-01", CAM, NAC, 2, 1, AMI), (6, "2025-02-01", SOU, POM, 1, 0, MAR),
    (6, "2025-02-02", TRE, BOT, 2, 1, AMI), (6, "2025-02-02", AUT, ESP, 2, 3, ALM),
    (6, "2025-02-03", SBR, PIC, 8, 0, AMI),
    (7, "2025-02-08", POM, TRE, 1, 1, JC), (7, "2025-02-08", SOU, NAC, 3, 0, MAR),
    (7, "2025-02-09", BOT, CAM, 4, 1, ALM), (7, "2025-02-09", PIC, AUT, 1, 2, AMI),
    (7, "2025-02-09", ESP, SBR, 0, 2, JC),
    (9, "2025-02-19", PIC, ESP, 0, 5, AMI), (9, "2025-02-22", NAC, TRE, 1, 4, JC),
    (9, "2025-02-22", SOU, BOT, 1, 2, MAR), (9, "2025-02-22", CAM, POM, 1, 1, AMI),
    (9, "2025-02-22", SBR, AUT, 5, 1, ALM),
]

linhas = []
for r, d, m, v, gm, gv, est in J2025:
    obs = "estádio conforme a fonte (pode estar inconsistente)" if (m, est) == (SBR, ALM) else ""
    linhas.append([2025, "1a_fase", r, d, m, v, gm, gv, "", "", est, "", "", "", obs])
linhas.append([2025, "final", "ida", "", SOU, BOT, 1, 0, "", "", "", "", "", "",
               "data e estádio não informados na fonte; Sousa mandou o jogo (Marizão provável)"])
linhas.append([2025, "final", "volta", "2025-03-30", BOT, SOU, 1, 1, "", "", ALM, "", "", "",
               "Sousa campeão (agregado 2x1)"])
# 2024: só jogos citados na fonte consultada
linhas.append([2024, "1a_fase", 1, "2024-01-18", BOT, "São Paulo Crystal", 5, 1, "", "", "", "", "", "", ""])
linhas.append([2024, "1a_fase", 7, "2024-03-01", "São Paulo Crystal", "CSP", 0, 3, "", "", "", "", "", "", ""])

with open(f"{OUT}/historico_partidas_2019_2025.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(COLS_PARTIDAS)
    for i, l in enumerate(linhas, 1):
        w.writerow([f"H-{i:03d}"] + l)
print("historico_partidas_2019_2025.csv:", len(linhas), "jogos")

# Classificação final da 1ª fase: (temporada, pos, clube, P, J, V, E, D, GP, GC, pontos_deduzidos, fonte)
T2025 = [(1, SOU, 20, 6, 2, 1, 14, 3), (2, BOT, 19, 6, 1, 2, 19, 8), (3, TRE, 18, 5, 3, 1, 18, 8),
         (4, SBR, 17, 5, 2, 2, 21, 8), (5, CAM, 14, 4, 2, 3, 14, 10), (6, ESP, 10, 3, 1, 5, 14, 16),
         (7, POM, 9, 2, 3, 4, 7, 11), (8, NAC, 9, 2, 3, 4, 15, 21), (9, AUT, 7, 1, 4, 4, 9, 16),
         (10, PIC, 1, 0, 1, 8, 5, 35)]
T2024 = [(1, TRE, 21, 7, 0, 2, 18, 6, 0), (2, SBR, 17, 5, 2, 2, 13, 6, 0), (3, BOT, 17, 5, 2, 2, 13, 9, 0),
         (4, SOU, 14, 4, 2, 3, 11, 6, 0), (5, "CSP", 13, 4, 1, 4, 10, 9, 0), (6, CAM, 11, 3, 2, 4, 6, 10, 0),
         (7, NAC, 10, 3, 1, 5, 7, 10, 0), (8, POM, 10, 3, 1, 5, 10, 14, 0),
         (9, "São Paulo Crystal", 4, 1, 1, 7, 4, 22, 0), (10, "Atlético Cajazeirense", -2, 3, 2, 4, 8, 8, 13)]
with open(f"{OUT}/classificacao_historica_1a_fase.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["temporada", "pos", "clube", "pontos", "jogos", "vitorias", "empates", "derrotas", "gols_pro",
                "gols_contra", "saldo", "pontos_deduzidos", "fonte"])
    for pos, c, p, v, e, d, gp, gc in T2025:
        w.writerow([2025, pos, c, p, 9, v, e, d, gp, gc, gp - gc, 0, "api-futebol.com.br"])
    for pos, c, p, v, e, d, gp, gc, ded in T2024:
        w.writerow([2024, pos, c, p, 9, v, e, d, gp, gc, gp - gc, ded, "Wikipédia (en)"])

# Artilharia 2026 (Jornal da Paraíba). gols; cartões não constam na fonte.
ART = {
    5: [("Everton Heleno", CAM), ("Pingo", NAC), ("Silvano", TRE)],
    4: [("Isaías", "Confiança"), ("Luis Henrique", SOU), ("Marcelo Toscano", SBR)],
    3: [("Matheus Bambu", SOU), ("Miguel Vinícius", CAM), ("Nenê", BOT), ("Renê", NAC)],
    2: [("Abnner", NAC), ("Anderson Montanha", "Confiança"), ("Cassimiro", "Confiança"),
        ("Cláudio Jr.", ESP), ("Diego Viana", SOU), ("Dudu Nardini", BOT), ("Everton Felipe", POM),
        ("Felipe Azevedo", BOT), ("Felipe Jacaré", SOU), ("Guilherme Santos", BOT),
        ("Henrique Dourado", BOT), ("Joãozinho", CAM), ("Kayon", BOT), ("Pedro Igor", TRE)],
    1: [("Augusto Potiguar", CAM), ("Bruno Gonçalves", "Atlético Cajazeirense"), ("Cézar Juru", "Confiança"),
        ("Dedé", POM), ("Diego Ceará", SBR), ("Dielson", "Confiança"), ("Dudu Hatamoto", BOT),
        ("Edson Kapa", ESP), ("Erik Henrique", CAM), ("Erison", POM), ("Felipinho", NAC), ("França", SBR),
        ("Gabigol", ESP), ("Gean", "Atlético Cajazeirense"), ("Guilherme", POM), ("Gustavo", SBR),
        ("Hugo Borges", TRE), ("Ian Augusto", SBR), ("Igor Maduro", BOT), ("Jadson", SBR), ("Jalison", POM),
        ("Jhônata Varela", BOT), ("Júnior Dindê", SBR), ("Junel", ESP), ("Kiko", POM),
        ("Leandro", "Atlético Cajazeirense"), ("Lucas", "Confiança"), ("Mano Walter", ESP), ("Manú", POM),
        ("Marcelo Duarte", SOU), ("Mateuzinho", SOU), ("Natalício", SOU), ("Nattan", POM), ("Patrik", CAM),
        ("Pedro Vitor", SBR), ("Robson", "Atlético Cajazeirense"), ("Rodriguinho", NAC), ("Rogério", NAC),
        ("Ryan", TRE), ("Santiago", "Atlético Cajazeirense"), ("Thallyson", BOT), ("Thiago Alagoano", TRE),
        ("Vam Baster", "Confiança"), ("Veraldo", SOU), ("Victor Ferraz", SBR), ("Vinícius Bala", TRE),
        ("Wesley", "Atlético Cajazeirense"), ("Yan Souto", BOT)],
}
CONTRA = [("Anderson Montanha", "Confiança"), ("Jadson", SBR), ("Lázaro André", POM), ("Wallace", CAM),
          ("Michael Fracaro", BOT)]

gols_clube = defaultdict(int)
with open(f"{OUT}/artilharia_cartoes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["temporada", "jogador", "clube", "gols", "amarelos", "vermelhos", "fonte"])
    for g, lista in ART.items():
        for jog, clube in lista:
            w.writerow([2026, jog, clube, g, "", "", "Jornal da Paraíba"])
            gols_clube[clube] += g
with open(f"{OUT}/gols_contra_2026.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["temporada", "jogador", "clube_do_jogador", "gols_contra", "fonte"])
    for jog, clube in CONTRA:
        w.writerow([2026, jog, clube, 1, "Jornal da Paraíba"])
n_jog = sum(len(v) for v in ART.values())
print(f"artilharia_cartoes.csv: {n_jog} artilheiros, {sum(gols_clube.values())} gols; gols_contra_2026.csv: {len(CONTRA)}")

# Conferência cruzada: gols por clube na artilharia x gols por clube nos placares de partidas_2026.csv
gf = defaultdict(int)
sem_placar = set()
with open(f"{OUT}/partidas_2026.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["gols_mandante"] == "":
            sem_placar |= {r["mandante"], r["visitante"]}
            continue
        gf[r["mandante"]] += int(r["gols_mandante"])
        gf[r["visitante"]] += int(r["gols_visitante"])
rel = ["Conferência: gols dos artilheiros (artilharia) x gols dos placares de partidas_2026.csv (1ª fase + mata-mata)",
       "Placares - artilharia = gols contra a favor do clube (deveria ser >= 0 e somar 5).",
       "Clubes marcados com * participam do jogo sem placar (Treze x Atlético) e ficam abaixo do esperado.", "",
       f"{'clube':24} {'placares':>9} {'artilharia':>11} {'dif':>5}"]
tot = 0
for c in sorted(gf):
    dif = gf[c] - gols_clube[c]
    tot += dif
    rel.append(f"{c + ('*' if c in sem_placar else ''):24} {gf[c]:>9} {gols_clube[c]:>11} {dif:>5}")
rel += ["", f"Soma das diferenças: {tot} (esperado: 5 gols contra, mais o que falta do jogo sem placar)"]
print("\n".join(rel))
with open(f"{OUT}/relatorio_conferencia_artilharia.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rel) + "\n")
