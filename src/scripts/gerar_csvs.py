"""Gera os CSVs do Paraibano 2026 e valida contra a classificação da apresentação do Zetra.

Fonte dos placares, estádios, público e renda: Jornal da Paraíba (25/03/2026), que cita números
divulgados pela FPF-PB. Fonte da classificação final da 1ª fase: apresentação do projeto
(GE/PB via Wikipédia).
"""
import csv
import os
from collections import defaultdict
from itertools import product

OUT = "dados_zetra"
os.makedirs(OUT, exist_ok=True)

# Nomes padronizados (iguais aos da apresentação)
BOT, CAM, TRE, SBR, SOU = "Botafogo-PB", "Campinense", "Treze", "Serra Branca", "Sousa"
ATL, NAC, ESP, POM, CON = "Atlético Cajazeirense", "Nacional de Patos", "Esporte de Patos", "Pombal", "Confiança"

# (rodada, mandante, visitante, gm, gv, estadio, publico_total, publico_pagante, renda)
# gm/gv = None quando o placar não estava na fonte
R1 = [
    (1, SOU, CON, 3, 0, "Marizão", 1549, 1349, 15010.00),
    (1, CAM, ATL, 2, 0, "Amigão", 3270, 2721, 55225.00),
    (1, BOT, ESP, 1, 1, "Frasqueirão", 708, 573, 6410.00),
    (1, NAC, POM, 3, 0, "José Cavalcanti", 480, 420, 7300.00),
    (1, SBR, TRE, 0, 2, "Amigão", 1989, 1291, 44075.00),
    (2, CON, BOT, 0, 1, "Toca do Papão", 1010, 810, 16200.00),
    (2, ATL, ESP, 1, 0, "Perpetão", 874, 874, 9635.00),
    (2, SBR, SOU, 2, 1, "Amigão", 232, 128, 1170.00),
    (2, CAM, NAC, 1, 2, "Amigão", 3463, 2942, 55475.00),
    (2, POM, TRE, 1, 2, "Pereirão", 1260, 1090, 15100.00),
    (3, BOT, SOU, 1, 1, "Almeidão", 5714, 5109, 123320.00),
    (3, ESP, SBR, 0, 1, "José Cavalcanti", 340, 340, 6200.00),
    (3, POM, CAM, 2, 2, "Pereirão", 1210, 1050, 13500.00),
    (3, NAC, CON, 4, 4, "José Cavalcanti", 1186, 1008, 10320.00),
    (3, TRE, ATL, None, None, "Amigão", 3867, 3355, 58255.00),
    (4, CON, CAM, 2, 2, "Toca do Papão", 833, 483, 4830.00),
    (4, SOU, TRE, 2, 1, "Marizão", 1188, 988, 12390.00),
    (4, BOT, POM, 4, 0, "Almeidão", 2676, 2063, 34735.00),
    (4, SBR, ATL, 1, 0, "Amigão", 371, 140, 1125.00),
    (4, ESP, NAC, 0, 0, "José Cavalcanti", 1600, 1350, 16500.00),
    (5, CAM, BOT, 4, 0, "Amigão", 2356, 1931, 13105.00),
    (5, TRE, CON, 1, 0, "Amigão", 2647, 2327, 24145.00),
    (5, POM, SBR, 3, 1, "Pereirão", 472, 437, 6100.00),
    (5, SOU, ESP, 0, 1, "Marizão", 788, 688, 9480.00),
    (5, ATL, NAC, 1, 0, "Perpetão", 1041, 1041, 13830.00),
    (6, TRE, CAM, 0, 1, "Amigão", 8792, 7487, 240805.00),
    (6, ESP, POM, 0, 1, "José Cavalcanti", 298, 238, 3780.00),
    (6, NAC, BOT, 0, 0, "José Cavalcanti", 1005, 832, 17300.00),
    (6, SBR, CON, 2, 0, "Amigão", 352, 25, 675.00),
    (6, SOU, ATL, 2, 1, "Marizão", 2312, 2112, 28230.00),
    (7, NAC, SOU, 1, 1, "José Cavalcanti", 1254, 1110, 14520.00),
    (7, BOT, TRE, 2, 0, "Almeidão", 6179, 5529, 97755.00),
    (7, CAM, SBR, 1, 0, "Amigão", 2360, 1925, 17240.00),
    (7, CON, ESP, 1, 2, "Toca do Papão", 454, 155, 2110.00),
    (7, POM, ATL, 1, 1, "Pereirão", 1473, 1400, 11180.00),
    (8, CAM, SOU, 1, 1, "Amigão", 3345, 2262, 22745.00),
    (8, ATL, BOT, 0, 2, "Perpetão", 2107, 1921, 35790.00),
    (8, SBR, NAC, 2, 2, "Amigão", 457, 17, 500.00),
    (8, TRE, ESP, 3, 0, "Amigão", 1668, 1346, 11305.00),
    (8, CON, POM, 3, 2, "Toca do Papão", 103, 62, 1240.00),
    (9, SOU, POM, 2, 0, "Marizão", 2183, 1883, 22450.00),
    (9, BOT, SBR, 1, 1, "Almeidão", 4449, 3588, 65435.00),
    (9, TRE, NAC, 1, 2, "Amigão", 3656, 3081, 39725.00),
    (9, ESP, CAM, 1, 0, "José Cavalcanti", 288, 244, 8705.00),
    (9, ATL, CON, 0, 2, "Perpetão", 660, 560, 4935.00),
]

# Classificação final da 1ª fase conforme a apresentação: clube -> (P, V, E, D, GP, GC)
PDF = {
    BOT: (16, 4, 4, 1, 13, 7), CAM: (15, 4, 3, 2, 14, 9), SOU: (15, 4, 3, 2, 13, 8),
    SBR: (14, 4, 2, 3, 11, 10), NAC: (14, 3, 5, 1, 14, 10), TRE: (12, 4, 0, 5, 11, 11),
    ESP: (11, 3, 2, 4, 6, 9), ATL: (10, 3, 1, 5, 6, 11), CON: (8, 2, 2, 5, 12, 17),
    POM: (8, 2, 2, 5, 10, 18),
}


def tabela(jogos):
    t = defaultdict(lambda: dict(P=0, V=0, E=0, D=0, GP=0, GC=0))
    for _, m, v, gm, gv, *_ in jogos:
        for c, gp, gc in ((m, gm, gv), (v, gv, gm)):
            t[c]["GP"] += gp
            t[c]["GC"] += gc
            if gp > gc:
                t[c]["V"] += 1
                t[c]["P"] += 3
            elif gp == gc:
                t[c]["E"] += 1
                t[c]["P"] += 1
            else:
                t[c]["D"] += 1
    return t


def como_tupla(d):
    return (d["P"], d["V"], d["E"], d["D"], d["GP"], d["GC"])


# 1) Monta a lista de jogos. O placar ausente (Treze x Atlético, 3ª rodada) NÃO é inventado.
jogos = []
for j in R1:
    r, m, v, gm, gv, est, pt, pp, renda = j
    obs = ""
    if gm is None:
        gm, gv = "", ""
        obs = ("placar ausente na fonte; pela classificação final o Atlético Cajazeirense venceu "
               "(só o resultado é confirmado, não os gols)")
    jogos.append(dict(fase="1a_fase", rodada=r, mandante=m, visitante=v, gm=gm, gv=gv,
                      pen_m="", pen_v="", estadio=est, pt=pt, pp=pp, renda=renda, obs=obs))

# Mata-mata (ida e volta)
mata = [
    ("semifinal", "ida", SOU, CAM, 0, 1, "", "", "Marizão", 3598, 3298, 36790.00, ""),
    ("semifinal", "volta", CAM, SOU, 0, 1, 2, 4, "Amigão", 8351, 6862, 68340.00, "Sousa avança nos pênaltis (4x2) após 1x1 no agregado"),
    ("semifinal", "ida", SBR, BOT, 1, 0, "", "", "Amigão", 994, 684, 9415.00, ""),
    ("semifinal", "volta", BOT, SBR, 3, 1, "", "", "Almeidão", 8196, 5527, 125475.00, ""),
    ("final", "ida", SOU, BOT, 1, 2, "", "", "Marizão", 5585, 5085, 59720.00, ""),
    ("final", "volta", BOT, SOU, 0, 0, "", "", "Almeidão", 21537, 19330, 734021.20, "Botafogo campeão (agregado 2x1)"),
]
for fase, perna, m, v, gm, gv, pm, pv, est, pt, pp, renda, obs in mata:
    jogos.append(dict(fase=fase, rodada=perna, mandante=m, visitante=v, gm=gm, gv=gv, pen_m=pm,
                      pen_v=pv, estadio=est, pt=pt, pp=pp, renda=renda, obs=obs))

# 2) Validação contra a classificação da apresentação (relatório, sem forçar igualdade)
primeira = [(j["rodada"], j["mandante"], j["visitante"], j["gm"], j["gv"])
            for j in jogos if j["fase"] == "1a_fase" and j["gm"] != ""]
assert len(jogos) - 6 == 45
t = tabela(primeira)
linhas = ["Validação: partidas da 1ª fase (fonte jornalística) x classificação da apresentação",
          "Diferença = apresentação - calculado dos placares (44 jogos com placar; falta Treze x Atlético)", ""]
linhas.append(f"{'clube':24} {'P':>3} {'V':>3} {'E':>3} {'D':>3} {'GP':>4} {'GC':>4}")
dif_gols = 0
for c, pdf in PDF.items():
    d = tuple(p - x for p, x in zip(pdf, como_tupla(t[c])))
    dif_gols += d[4]
    linhas.append(f"{c:24} " + " ".join(f"{x:>3}" if i < 4 else f"{x:>4}" for i, x in enumerate(d)))
gols_fonte = sum(j["gm"] + j["gv"] for j in jogos if j["fase"] == "1a_fase" and j["gm"] != "")
linhas += ["", f"Gols nos 44 jogos com placar: {gols_fonte}; total oficial da 1ª fase na apresentação: 110",
           f"Gols a explicar (jogo sem placar + possíveis erros de placar na fonte): {110 - gols_fonte}",
           "Pontos, vitórias, empates e derrotas batem para todos os clubes, exceto Treze (+1 derrota) e",
           "Atlético Cajazeirense (+1 vitória, +3 pontos), o que é exatamente o jogo sem placar.",
           "Ou seja: os RESULTADOS (V/E/D) estão consistentes; as contagens de GOLS têm lacunas a conferir."]
print("\n".join(linhas))
with open(f"{OUT}/relatorio_validacao.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(linhas) + "\n")

# 3) Escrita dos CSVs
with open(f"{OUT}/partidas_2026.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["partida_id", "temporada", "fase", "rodada_ou_perna", "data", "mandante", "visitante",
                "gols_mandante", "gols_visitante", "penaltis_mandante", "penaltis_visitante", "estadio",
                "publico_total", "publico_pagante", "renda_bruta_rs", "observacao"])
    for i, j in enumerate(jogos, 1):
        w.writerow([f"2026-{i:03d}", 2026, j["fase"], j["rodada"], "", j["mandante"], j["visitante"],
                    j["gm"], j["gv"], j["pen_m"], j["pen_v"], j["estadio"], j["pt"], j["pp"],
                    f'{j["renda"]:.2f}', j["obs"]])

ordem = list(PDF)  # já na ordem de classificação da apresentação
with open(f"{OUT}/classificacao_2026_1a_fase.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pos", "clube", "pontos", "jogos", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra",
                "saldo", "situacao"])
    for pos, c in enumerate(ordem, 1):
        p, v, e, d_, gp, gc = PDF[c]
        sit = "semifinal" if pos <= 4 else ("rebaixado" if pos >= 9 else "copa_paraiba")
        w.writerow([pos, c, p, 9, v, e, d_, gp, gc, gp - gc, sit])

clubes = [
    (BOT, "João Pessoa", "Almeidão", ""), (CAM, "Campina Grande", "Amigão", ""),
    (TRE, "Campina Grande", "Amigão", ""), (SBR, "Campina Grande", "Amigão", ""),
    (SOU, "Sousa", "Marizão", ""), (ATL, "Cajazeiras", "Perpetão", ""),
    (NAC, "Patos", "José Cavalcanti", ""), (ESP, "Patos", "José Cavalcanti", ""),
    (POM, "Pombal", "Pereirão", "sim"), (CON, "Sapé", "Toca do Papão", "sim"),
]
# Pombal e Confiança foram rebaixados em 2026; campo mantido só nesses dois
with open(f"{OUT}/clubes_2026.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["clube_id", "nome", "cidade", "estadio_mandante", "rebaixado_ao_fim_de_2026"])
    for i, (n, cid, est, reb) in enumerate(clubes, 1):
        w.writerow([f"C{i:02d}", n, cid, est, reb or "nao"])

# Modelos vazios para o que as fontes consultadas não trazem
def vazio(nome, cab):
    with open(f"{OUT}/{nome}", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(cab)

vazio("historico_partidas_2019_2025_modelo.csv",
      ["partida_id", "temporada", "fase", "rodada_ou_perna", "data", "mandante", "visitante",
       "gols_mandante", "gols_visitante", "penaltis_mandante", "penaltis_visitante", "estadio",
       "publico_total", "publico_pagante", "renda_bruta_rs", "observacao"])
vazio("elencos_modelo.csv",
      ["jogador_id", "nome", "clube", "posicao", "idade", "jogos", "minutos", "gols", "assistencias",
       "amarelos", "vermelhos", "fonte"])
vazio("eventos_partida_modelo.csv",
      ["partida_id", "minuto", "tipo_evento", "clube", "jogador", "detalhe"])
vazio("ambiente_partida_modelo.csv",
      ["partida_id", "chuva_mm", "temperatura_c", "vento_kmh", "condicao_gramado", "fonte"])
vazio("artilharia_cartoes_modelo.csv",
      ["temporada", "jogador", "clube", "gols", "amarelos", "vermelhos", "fonte"])
print("Arquivos gerados em", OUT)
