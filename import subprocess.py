import subprocess
import os

# Definição dos cenários de teste e dos ficheiros de input correspondentes
cenarios = {
    "Alínea A: Efeito Convoy (FIFO vs SJF)": {
        "workload": "inputs/workload_convoy.txt",
        "algoritmos": ["FIFO", "SJF"]
    },
    "Alínea B: Interatividade e Resposta (FIFO vs RR)": {
        "workload": "inputs/workload_interativa.txt",
        "algoritmos": ["FIFO", "RR"]
    },
    "Alínea C: MLFQ (Separação Batch vs Interativo)": {
        "workload": "inputs/workload_mlfq.txt",
        "algoritmos": ["MLFQ"]
    }
}

def correr_simulador(algoritmo, workload_file):
    """Executa o ossim com o algoritmo e workload especificados e retorna o resultado."""
    comando = ["python3", "ossim.py", "--alg", algoritmo, "--input", workload_file]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar {algoritmo}: {e.stderr}"

def main():
    print("=== COMPARAÇÃO DE ALGORITMOS DE ESCALAMENTO (FICHEIRO A FICHEIRO) ===\n")
    print(f"Estudante: Tomás Rocha (a22509631)\n" + "="*70 + "\n")

    for nome_cenario, config in cenarios.items():
        print(f"\n[+] {nome_cenario}")
        print(f"    Workload: {config['workload']}")
        print("-" * 70)
        
        for alg in config['algoritmos']:
            print(f"-> A executar algoritmo: {alg}")
            saida = correr_simulador(alg, config['workload'])
            # Exibe as métricas detalhadas obtidas pelo simulador para cada processo
            print(saida)
            print("~" * 70)

if __name__ == "__main__":
    main()