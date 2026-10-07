import os

def simular_mlfq(nome_ficheiro, descricao):
    print(f"\n================ {descricao} ({nome_ficheiro}) ================")
    if not os.path.exists(nome_ficheiro):
        print(f"Ficheiro {nome_ficheiro} não encontrado.")
        return

    processos = []
    with open(nome_ficheiro, "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = [p.strip() for p in linha.split(",")]
            if len(partes) >= 3:
                processos.append({
                    "pid": int(partes[0]),
                    "arrival": int(partes[1]),
                    "burst": int(partes[2]),
                    "remaining": int(partes[2]),
                    "first_run": -1,
                    "queue": 0 # Começa na fila de topo (Q0)
                })

    # Simulação MLFQ simplificada (3 filas: Q0 q=1, Q1 q=2, Q2 q=4)
    q0, q1, q2 = [], [], []
    nao_chegados = sorted(processos, key=lambda x: x['arrival'])
    tempo = 0
    concluidos = 0
    n = len(processos)
    estats = {}

    while concluidos < n:
        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            q0.append(nao_chegados.pop(0))

        fila_atual, q_quantum = None, 1
        if q0: fila_atual = q0; q_quantum = 1
        elif q1: fila_atual = q1; q_quantum = 2
        elif q2: fila_atual = q2; q_quantum = 4
        else:
            if nao_chegados:
                tempo = nao_chegados[0]['arrival']
                continue
            else:
                break

        p = fila_atual.pop(0)
        if p['first_run'] == -1:
            p['first_run'] = tempo

        exec_time = min(q_quantum, p['remaining'])
        p['remaining'] -= exec_time
        tempo += exec_time

        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            q0.append(nao_chegados.pop(0))

        if p['remaining'] > 0:
            # Despromoção de fila se esgotou o quantum sem acabar
            if fila_atual == q0: q1.append(p)
            elif fila_atual == q1: q2.append(p)
            else: q2.append(p)
            print(f" [Tempo {tempo}] Processo {p['pid']} despromovido (Restam: {p['remaining']})")
        else:
            turnaround = tempo - p['arrival']
            espera = turnaround - p['burst']
            resposta = p['first_run'] - p['arrival']
            estats[p['pid']] = (espera, turnaround, resposta)
            concluidos += 1
            print(f" [Tempo {tempo}] Processo {p['pid']} CONCLUÍDO. (Espera: {espera}, Resposta: {resposta})")

    if estats:
        esps = [v[0] for v in estats.values()]
        tas = [v[1] for v in estats.values()]
        resps = [v[2] for v in estats.values()]
        print(f">> Média Geral -> Espera: {sum(esps)/len(esps):.2f} | Turnaround: {sum(tas)/len(tas):.2f} | Resposta: {sum(resps)/len(resps):.2f}")

if __name__ == "__main__":
    simular_mlfq("cenario1.csv", "Cenário 1: 2 Interativos + 1 Batch")
    simular_mlfq("cenario2.csv", "Cenário 2: Comportamento Dinâmico (Batch -> Interativo -> Batch)")
