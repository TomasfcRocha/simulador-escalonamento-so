import os

def simular():
    print("=== DEMONSTRAÇÃO PRÁTICA: FIFO vs SJF (OSSIM) ===")
    print("Estudante: Tomás Rocha (a22509631)\n" + "="*50)
    
    # Ler o ficheiro teste_sjf.csv
    if not os.path.exists("teste_sjf.csv"):
        print("Erro: Ficheiro teste_sjf.csv não encontrado.")
        return
        
    processos = []
    with open("teste_sjf.csv", "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = [p.strip() for p in linha.split(",")]
            if len(partes) >= 3:
                pid = int(partes[0])
                arrival = int(partes[1])
                burst = int(partes[2])
                processos.append({"pid": pid, "arrival": arrival, "burst": burst})

    print(f"Workload carregada ({len(processos)} processos):")
    for p in processos:
        print(f" - Processo {p['pid']}: Chegada = {p['arrival']}, Burst = {p['burst']}")
    print("="*50)

    # --- 1. Simulação FIFO (First-In, First-Out) ---
    print("\n[+] Algoritmo: FIFO (First-In, First-Out)")
    # Ordenados por ordem de chegada
    fila_fifo = sorted(processos, key=lambda x: x['arrival'])
    
    tempo_atual = 0
    esperas_fifo = []
    turnarounds_fifo = []
    
    for p in fila_fifo:
        if tempo_atual < p['arrival']:
        # Se o CPU estiver ocioso até o processo chegar
            tempo_atual = p['arrival']
        espera = tempo_atual - p['arrival']
        turnaround = espera + p['burst']
        esperas_fifo.append(espera)
        turnarounds_fifo.append(turnaround)
        print(f" -> Processo {p['pid']} executado no instante {tempo_atual} (Espera: {espera}, Turnaround: {turnaround})")
        tempo_atual += p['burst']
        
    med_espera_fifo = sum(esperas_fifo) / len(esperas_fifo)
    med_ta_fifo = sum(turnarounds_fifo) / len(turnarounds_fifo)
    print(f">> FIFO -> Tempo Médio de Espera: {med_espera_fifo:.2f} | Turnaround Médio: {med_ta_fifo:.2f}")

    # --- 2. Simulação SJF (Shortest Job First - Não preemptivo) ---
    print("\n[+] Algoritmo: SJF (Shortest Job First)")
    # Chegam e escolhe-se o de menor burst entre os disponíveis
    nao_chegados = sorted(processos, key=lambda x: x['arrival'])
    prontos = []
    tempo_atual = 0
    esperas_sjf = []
    turnarounds_sjf = []
    
    completed = 0
    n = len(processos)
    
    while completed < n:
        # Adicionar à fila de prontos os processos que já chegaram
        while nao_chegados and nao_chegados[0]['arrival'] <= tempo_atual:
            prontos.append(nao_chegados.pop(0))
            
        if not prontos:
            # Avança o tempo se o CPU estiver ocioso
            tempo_atual = nao_chegados[0]['arrival']
            continue
            
        # Ordenar por menor burst (SJF) e em caso de empate por ordem de chegada
        prontos.sort(key=lambda x: (x['burst'], x['arrival']))
        p = prontos.pop(0)
        
        espera = tempo_atual - p['arrival']
        turnaround = espera + p['burst']
        esperas_sjf.append(espera)
        turnarounds_sjf.append(turnaround)
        
        print(f" -> Processo {p['pid']} (Burst: {p['burst']}) executado no instante {tempo_atual} (Espera: {espera}, Turnaround: {turnaround})")
        tempo_atual += p['burst']
        completed += 1

    med_espera_sjf = sum(esperas_sjf) / len(esperas_sjf)
    med_ta_sjf = sum(turnarounds_sjf) / len(turnarounds_sjf)
    print(f">> SJF  -> Tempo Médio de Espera: {med_espera_sjf:.2f} | Turnaround Médio: {med_ta_sjf:.2f}")
    
    print("\n" + "="*50)
    print(f"CONCLUSÃO PARA O RELATÓRIO:")
    print(f" * O FIFO sofre de Efeito Convoy (espera média: {med_espera_fifo:.2f}). O processo longo bloqueia os curtos.")
    print(f" * O SJF prioriza os processos curtos (espera média: {med_espera_sjf:.2f}), provando ser significativamente mais rápido e eficiente!")
    print("="*50)

if __name__ == "__main__":
    simular()
