import os

def simular():
    print("=== DEMONSTRAÇÃO COMPARATIVA DE ALGORITMOS DE ESCALONAMENTO ===")
    print("Estudante: Tomás Rocha (a22509631)\n" + "="*60)
    
    if not os.path.exists("teste_rr.csv"):
        print("Erro: Ficheiro teste_rr.csv não encontrado.")
        return
        
    processos = []
    with open("teste_rr.csv", "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = [p.strip() for p in linha.split(",")]
            if len(partes) >= 3:
                pid = int(partes[0])
                arrival = int(partes[1])
                burst = int(partes[2])
                processos.append({"pid": pid, "arrival": arrival, "burst": burst, "remaining": burst, "first_run": -1})

    print(f"Workload carregada ({len(processos)} processos):")
    for p in processos:
        print(f" - Processo {p['pid']}: Chegada = {p['arrival']}, Burst = {p['burst']}")
    print("="*60)

    # --- 1. FIFO ---
    procs = [dict(p) for p in processos]
    procs.sort(key=lambda x: x['arrival'])
    tempo = 0
    esperas, turnarounds, respostas = [], [], []
    for p in procs:
        if tempo < p['arrival']: tempo = p['arrival']
        espera = tempo - p['arrival']
        turnaround = espera + p['burst']
        resposta = espera
        esperas.append(espera); turnarounds.append(turnaround); respostas.append(resposta)
        tempo += p['burst']
    print(f"[FIFO] Espera Média: {sum(esperas)/len(esperas):.2f} | Turnaround Médio: {sum(turnarounds)/len(turnarounds):.2f} | Resposta Média: {sum(respostas)/len(respostas):.2f}")

    # --- 2. SJF (Não Preemptivo) ---
    procs = [dict(p) for p in processos]
    nao_chegados = sorted(procs, key=lambda x: x['arrival'])
    prontos = []
    tempo = 0
    esperas, turnarounds, respostas = [], [], []
    completed = 0
    while completed < len(procs):
        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            prontos.append(nao_chegados.pop(0))
        if not prontos:
            tempo = nao_chegados[0]['arrival']
            continue
        prontos.sort(key=lambda x: (x['burst'], x['arrival']))
        p = prontos.pop(0)
        espera = tempo - p['arrival']
        turnaround = espera + p['burst']
        resposta = espera
        esperas.append(espera); turnarounds.append(turnaround); respostas.append(resposta)
        tempo += p['burst']
        completed += 1
    print(f"[SJF]  Espera Média: {sum(esperas)/len(esperas):.2f} | Turnaround Médio: {sum(turnarounds)/len(turnarounds):.2f} | Resposta Média: {sum(respostas)/len(respostas):.2f}")

    # --- 3. Round Robin (Quantum = 2) ---
    quantum = 2
    procs = [dict(p) for p in processos]
    nao_chegados = sorted(procs, key=lambda x: x['arrival'])
    fila = []
    tempo = 0
    concluidos = 0
    n = len(procs)
    estats = {}

    while concluidos < n:
        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            fila.append(nao_chegados.pop(0))
        if not fila:
            tempo = nao_chegados[0]['arrival']
            continue
        p = fila.pop(0)
        if p['first_run'] == -1:
            p['first_run'] = tempo
        
        exec_time = min(quantum, p['remaining'])
        p['remaining'] -= exec_time
        tempo += exec_time

        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            fila.append(nao_chegados.pop(0))

        if p['remaining'] > 0:
            fila.append(p)
        else:
            turnaround = tempo - p['arrival']
            espera = turnaround - p['burst']
            resposta = p['first_run'] - p['arrival']
            estats[p['pid']] = (espera, turnaround, resposta)
            concluidos += 1

    e_rr = [v[0] for v in estats.values()]
    t_rr = [v[1] for v in estats.values()]
    r_rr = [v[2] for v in estats.values()]
    print(f"[RR]   Espera Média: {sum(e_rr)/len(e_rr):.2f} | Turnaround Médio: {sum(t_rr)/len(t_rr):.2f} | Resposta Média: {sum(r_rr)/len(r_rr):.2f}  <-- Ótimo Tempo de Resposta!")

    # --- 4. MLFQ (Multi-Level Feedback Queue) ---
    # 3 filas com prioridades e quanta crescentes (ex: Q0 q=1, Q1 q=2, Q2 q=4)
    procs = [dict(p) for p in processos]
    nao_chegados = sorted(procs, key=lambda x: x['arrival'])
    q0, q1, q2 = [], [], []
    tempo = 0
    concluidos = 0
    estats_mlfq = {}

    while concluidos < n:
        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            q0.append(nao_chegados.pop(0))
        
        fila_atual = None
        quantum_atual = 1
        if q0: fila_atual = q0; quantum_atual = 1
        elif q1: fila_atual = q1; quantum_atual = 2
        elif q2: fila_atual = q2; quantum_atual = 4
        else:
            tempo = nao_chegados[0]['arrival']
            continue

        p = fila_atual.pop(0)
        if p['first_run'] == -1:
            p['first_run'] = tempo

        exec_time = min(quantum_atual, p['remaining'])
        p['remaining'] -= exec_time
        tempo += exec_time

        while nao_chegados and nao_chegados[0]['arrival'] <= tempo:
            q0.append(nao_chegados.pop(0))

        if p['remaining'] > 0:
            # Despromove para a fila inferior se esgotou o quantum
            if fila_atual == q0: q1.append(p)
            elif fila_atual == q1: q2.append(p)
            else: q2.append(p)
        else:
            turnaround = tempo - p['arrival']
            espera = turnaround - p['burst']
            resposta = p['first_run'] - p['arrival']
            estats_mlfq[p['pid']] = (espera, turnaround, resposta)
            concluidos += 1

    e_m = [v[0] for v in estats_mlfq.values()]
    t_m = [v[1] for v in estats_mlfq.values()]
    r_m = [v[2] for v in estats_mlfq.values()]
    print(f"[MLFQ] Espera Média: {sum(e_m)/len(e_m):.2f} | Turnaround Médio: {sum(t_m)/len(t_m):.2f} | Resposta Média: {sum(r_m)/len(r_m):.2f}  <-- Adaptativo e Rápido!")

    print("="*60)
    print("CONCLUSÃO PARA A ALÍNEA:")
    print(" * O Round Robin e o MLFQ garantem um Tempo de Resposta drasticamente inferior")
    print("   ao FIFO e SJF, por impedirem que processos longos monopolizem o CPU (preempção).")
    print("="*60)

if __name__ == "__main__":
    simular()
