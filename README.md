# Simulação: O Jantar dos Filósofos

Uma implementação em Python do clássico problema de sincronização de processos, demonstrando a ocorrência de *deadlock* e uma solução eficaz usando o método de hierarquia de recursos.

## O Problema: Jantar dos Filósofos

O "Jantar dos Filósofos" é um problema clássico da ciência da computação usado para ilustrar questões de sincronização em sistemas concorrentes. A configuração é a seguinte:

- **Cinco filósofos** estão sentados em uma mesa redonda.
- Entre cada par de filósofos adjacentes, há exatamente **um garfo**. Portanto, há cinco garfos no total.
- No centro da mesa, há um grande prato de espaguete.
- Um filósofo pode estar em um de dois estados: **pensando** ou **comendo**.

Para comer, um filósofo precisa de **dois garfos**: o que está à sua esquerda e o que está à sua direita. O dilema central, ou o *deadlock*, ocorre se todos os cinco filósofos decidirem comer ao mesmo tempo, e cada um pegar o garfo à sua esquerda. Nesse momento, todos os filósofos estarão segurando um garfo e esperando eternamente pelo segundo garfo (que está na mão de seu vizinho), e ninguém consegue comer. O sistema para.

## Implementações

Este repositório contém duas simulações distintas:

1.  `deadlock_simulation.py`: Uma implementação ingênua onde cada filósofo tenta pegar o garfo da esquerda e depois o da direita. Este código **resultará em deadlock**.
2.  `solution_simulation.py`: Uma implementação que resolve o deadlock aplicando uma **hierarquia de recursos**. Cada filósofo é instruído a pegar sempre o garfo de menor índice primeiro. Isso quebra a condição de espera circular, garantindo que o sistema continue a funcionar.

## Pré-requisitos

- Python 3.8 ou superior

## Como Executar

Clone o repositório e navegue até a pasta do projeto. Execute os scripts usando o interpretador Python 3.

### 1. Simulação com Deadlock

Para observar a condição de deadlock, onde o programa irá travar após alguns segundos:

```bash
python3 deadlock_simulation.py