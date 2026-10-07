import subprocess
import time
import os

def testar_algoritmo(algoritmo):
    print(f"\n================ A TESTAR ALGORITMO: {algoritmo} ================")
    
    # Inicia o servidor com o output direcionado diretamente para o terminal (sem PIPE oculto)
    servidor = subprocess.Popen(["./build/ossim", "--sched", algoritmo])
    time.sleep(1) # Dá tempo ao servidor para abrir o socket
    
    try:
        if os.path.exists("teste_sjf.csv"):
            with open("teste_sjf.csv", "r") as f:
                linhas = f.readlines()
                
            for linha in linhas:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                if os.path.exists("./build/application"):
                    partes = [p.strip() for p in linha.split(",")]
                    if len(partes) >= 3:
                        pid, arrival, burst = partes[0], partes[1], partes[2]
                        subprocess.run(["./build/application", pid, arrival, burst], capture_output=True)
                        print(f"-> [Cliente] Enviado Processo PID={pid} (Chegada={arrival}, Burst={burst})")
                time.sleep(0.2)
                
        print("A aguardar conclusão dos processos...")
        time.sleep(8) # Tempo alargado para dar tempo aos 20 ticks do processo 1 + curtos
        
    finally:
        # Envia sinal de fecho limpo ao servidor
        servidor.terminate()
        servidor.wait()

if __name__ == "__main__":
    print("Iniciando simulação comparativa em direto...")
    testar_algoritmo("FIFO")
    print("\n" + "="*50 + "\n")
    testar_algoritmo("SJF")
