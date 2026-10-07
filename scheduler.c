#include "scheduler.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

#include "msg.h"

static const char *SCHED_NAMES[] = { "FIFO", "SJF", "RR", "MLFQ", NULL };
static sched_algo_en sched_algo = SCHED_FIFO;

// 3 Filas físicas reais para o MLFQ
static queue_t mlfq_q0 = {0}; // Nível 0: Alta prioridade
static queue_t mlfq_q1 = {0}; // Nível 1: Média prioridade
static queue_t mlfq_q2 = {0}; // Nível 2: Baixa prioridade

#define AGING_THRESHOLD_MS 3000 // Tempo limite de espera antes de sofrer aging (promoção)

int set_sched_algo(const char *name) {
    for (int i = 0; SCHED_NAMES[i] != NULL; i++) {
        if (strcasecmp(SCHED_NAMES[i], name) == 0) {
            sched_algo = (sched_algo_en) i;
            // Limpar as filas do MLFQ ao alternar de algoritmo
            while (dequeue_pcb(&mlfq_q0) != NULL);
            while (dequeue_pcb(&mlfq_q1) != NULL);
            while (dequeue_pcb(&mlfq_q2) != NULL);
            return sched_algo;
        }
    }
    return -1;
}

const char *get_sched_algo_str(void) {
    return SCHED_NAMES[sched_algo];
}

/**
 * Envia DONE para a aplicação e coloca o processo terminado na command queue.
 */
static void finish_burst(uint32_t current_time_ms, queue_t *cq, pcb_t *task) {
    msg_t msg = {
        .pid = task->pid,
        .request = PROCESS_REQUEST_DONE,
        .time_ms = current_time_ms
    };
    if (write(task->sockfd, &msg, sizeof(msg_t)) != sizeof(msg_t)) {
        perror("write");
    }
    enqueue_pcb(cq, task);
}

/**
 * Função auxiliar para verificar o Aging nas filas q1 e q2 e promover processos se necessário.
 */
static void check_aging(uint32_t current_time_ms) {
    // Verificar Aging na fila q1
    queue_elem_t *curr = mlfq_q1.head;
    while (curr != NULL) {
        queue_elem_t *next_elem = curr->next;
        if ((current_time_ms - curr->pcb->wait_start_ms) >= AGING_THRESHOLD_MS) {
            printf("[Scheduler] AGING: PID=%d esteve muito tempo na fila 1. A promover para a fila 0.\n", curr->pcb->pid);
            queue_elem_t *removed = remove_queue_elem(&mlfq_q1, curr);
            if (removed) {
                pcb_t *task = removed->pcb;
                free(removed);
                task->mlfq_level = 0;
                task->wait_start_ms = current_time_ms;
                enqueue_pcb(&mlfq_q0, task);
            }
        }
        curr = next_elem;
    }

    // Verificar Aging na fila q2
    curr = mlfq_q2.head;
    while (curr != NULL) {
        queue_elem_t *next_elem = curr->next;
        if ((current_time_ms - curr->pcb->wait_start_ms) >= AGING_THRESHOLD_MS) {
            printf("[Scheduler] AGING: PID=%d esteve muito tempo na fila 2. A promover para a fila 1.\n", curr->pcb->pid);
            queue_elem_t *removed = remove_queue_elem(&mlfq_q2, curr);
            if (removed) {
                pcb_t *task = removed->pcb;
                free(removed);
                task->mlfq_level = 1;
                task->wait_start_ms = current_time_ms;
                enqueue_pcb(&mlfq_q1, task);
            }
        }
        curr = next_elem;
    }
}

int scheduler(uint32_t current_time_ms, queue_t *rq, queue_t *cq, pcb_t **cpu_task) {
    // Se estivermos em MLFQ, novos processos ou desbloqueados em 'rq' entram na fila 0
    if (sched_algo == SCHED_MLFQ) {
        while (rq->head != NULL) {
            pcb_t *task = dequeue_pcb(rq);
            task->mlfq_level = 0;
            task->wait_start_ms = current_time_ms;
            enqueue_pcb(&mlfq_q0, task);
        }
        // Aplicar o mecanismo de envelhecimento periodicamente
        check_aging(current_time_ms);
    }

    // 1. Gerir o processo atualmente no CPU
    if (*cpu_task) {
        (*cpu_task)->ellapsed_time_ms += TICKS_MS;

        // Verificar se o burst terminou
        if ((*cpu_task)->ellapsed_time_ms >= (*cpu_task)->time_ms) {
            printf("[Scheduler] Processo PID=%d terminou o burst.\n", (*cpu_task)->pid);
            finish_burst(current_time_ms, cq, *cpu_task);
            *cpu_task = NULL;
        }
        // Preempção para Round-Robin (RR)
        else if (sched_algo == SCHED_RR) {
            if ((current_time_ms - (*cpu_task)->slice_start_ms) >= TIME_SLICE_MS) {
                printf("[Scheduler] RR: Quantum esgotado para PID=%d. A preemtir...\n", (*cpu_task)->pid);
                enqueue_pcb(rq, *cpu_task);
                *cpu_task = NULL;
            }
        }
        // Preempção e Despromoção no MLFQ
        else if (sched_algo == SCHED_MLFQ) {
            uint32_t quantum = TIME_SLICE_MS * (1 << (*cpu_task)->mlfq_level);

            if ((current_time_ms - (*cpu_task)->slice_start_ms) >= quantum) {
                (*cpu_task)->wait_start_ms = current_time_ms; // Registar início da espera na nova fila
                if ((*cpu_task)->mlfq_level == 0) {
                    (*cpu_task)->mlfq_level = 1;
                    printf("[Scheduler] MLFQ: PID=%d despromovido da fila 0 para a fila 1.\n", (*cpu_task)->pid);
                    enqueue_pcb(&mlfq_q1, *cpu_task);
                } else {
                    (*cpu_task)->mlfq_level = 2;
                    printf("[Scheduler] MLFQ: PID=%d despromovido/mantido na fila 2.\n", (*cpu_task)->pid);
                    enqueue_pcb(&mlfq_q2, *cpu_task);
                }
                *cpu_task = NULL;
            }
        }
    }

    // 2. Se o CPU estiver livre, selecionar o próximo processo
    if (*cpu_task == NULL) {
        if (sched_algo == SCHED_FIFO || sched_algo == SCHED_RR) {
            *cpu_task = dequeue_pcb(rq);
        }
        else if (sched_algo == SCHED_SJF) {
            if (rq->head != NULL) {
                queue_elem_t *best_elem = rq->head;
                queue_elem_t *curr = rq->head->next;

                while (curr != NULL) {
                    if (curr->pcb->time_ms < best_elem->pcb->time_ms) {
                        best_elem = curr;
                    }
                    curr = curr->next;
                }

                queue_elem_t *removed = remove_queue_elem(rq, best_elem);
                if (removed) {
                    *cpu_task = removed->pcb;
                    free(removed);
                }
            }
        }
        else if (sched_algo == SCHED_MLFQ) {
            // Hierarquia estrita: q0 -> q1 -> q2
            if (mlfq_q0.head != NULL) {
                *cpu_task = dequeue_pcb(&mlfq_q0);
            } else if (mlfq_q1.head != NULL) {
                *cpu_task = dequeue_pcb(&mlfq_q1);
            } else if (mlfq_q2.head != NULL) {
                *cpu_task = dequeue_pcb(&mlfq_q2);
            }
        }

        // Se um novo processo entrou no CPU, registar o início da fatia
        if (*cpu_task) {
            (*cpu_task)->slice_start_ms = current_time_ms;
            printf("[Scheduler] Processo PID=%d atribuído ao CPU (%s%s).\n", 
                   (*cpu_task)->pid, 
                   get_sched_algo_str(), 
                   (sched_algo == SCHED_MLFQ) ? ( (*cpu_task)->mlfq_level == 0 ? " - Fila 0" : ((*cpu_task)->mlfq_level == 1 ? " - Fila 1" : " - Fila 2") ) : "");
            return 1;
        }
    }
    return 0;
}