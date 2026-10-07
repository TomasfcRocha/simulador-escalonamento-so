import subprocess
import os

def main():
    print("=== COMPARAÇÃO EXPERIMENTAL DE ALGORITMOS (OSSIM) ===")
    print("Estudante: Tomás Rocha (a22509631)\n" + "="*60)
    
    binario = "./build/ossim"
    if not os.path.exists(binario):
        print("Erro: O executável do ossim não foi encontrado em ./build/ossim.")
        return

    cenario_teste = "custom_scenarios/sjf/c1.csv"
    if not os.path.exists(cenario_teste):
        cenario_teste = "scenarios/1/A.csv"

    algoritmos = ["FIFO", "SJF", "RR", "MLFQ"]

    print(f"Workload de teste utilizada: {cenario_teste}\n")
    print("=" * 60)

    # Ler o conteúdo do cenário para enviar via stdin com fecho de EOF
    if os.path.exists(cenario_teste):
        with open(cenario_teste, "r") as f:
            conteudo_input = f.read()
    else:
        conteudo_input = ""

    for alg in algoritmos:
        print(f"\n[+] Algoritmo: {alg}")
        print("-" * 60)
        
        cmd = [binario, "--sched", alg]
        
        try:
            # Popen com communicate envia os dados e fecha o stdin (evita timeout/bloqueio)
            processo = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            stdout, stderr = processo.communicate(input=conteudo_input, timeout=3)
            
            if stdout.strip():
                print(stdout)
            if stderr.strip():
                print("Erros/Avisos:", stderr)
            if not stdout.strip() and not stderr.strip():
                print("Simulação concluída (sem output textual gerado).")
                
        except subprocess.TimeoutExpired:
            processo.kill()
            print(f"Erro: Timeout ao executar {alg} (o escalonador demorou demasiado tempo).")
        except Exception as e:
            print(f"Erro ao executar {alg}: {e}")
        
        print("~" * 60)

if __name__ == "__main__":
    main()
