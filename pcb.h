//
// Created by Martijn Kuipers on 20/10/2025.
//

#ifndef PCB_H
#define PCB_H
#include <stdint.h>

#include "msg.h"

typedef enum  {
    TASK_COMMAND = 0,   // Task has connected and is waiting for instructions
    TASK_BLOCKED,       // Task is blocked (waiting/IO wait)
    TASK_RUNNING,       // Task is in the ready queue or currently running
    TASK_STOPPED,       // Task has finished execution (sent DONE), waiting for more messages
    TASK_TERMINATED,    // Task has been terminated and will be removed
} task_status_en;

// Define the Process Control Block (PCB) structure
typedef struct pcb_st {
    int32_t pid;                      
    task_status_en status;            
    uint32_t time_ms;                 
    uint32_t ellapsed_time_ms;     
    uint32_t slice_start_ms;         
    uint32_t sockfd;                 
    uint32_t last_update_time_ms;  
    int mlfq_level;                   // 0 = Alta, 1 = Média, 2 = Baixa
    uint32_t wait_start_ms;           // Timestamp de quando entrou na fila de espera (para o Aging)
} pcb_t;
#endif //PCB_H
