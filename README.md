# Simulação Interativa: O Jantar dos Filósofos

Este projeto oferece uma simulação gráfica e interativa do clássico problema de concorrência **"O Jantar dos Filósofos"**, implementado em Python com a biblioteca Tkinter.

A aplicação principal permite ao usuário visualizar e comparar em tempo real quatro cenários diferentes: dois que levam a um *deadlock* e duas soluções clássicas para o problema.

##  Funcionalidades

-   **Interface Gráfica Interativa:** Um menu principal para escolher qual simulação executar.
-   **Visualização de 4 Cenários:**
    1.  Deadlock (ocorrência não garantida).
    2.  Deadlock (ocorrência garantida para fins didáticos).
    3.  Solução com Hierarquia de Recursos.
    4.  Solução com Garçom (Árbitro).
-   **Display Dinâmico:** Os estados dos filósofos (*pensando*, *com fome*, *comendo*) e dos garfos (*livre*, *em uso*) são atualizados em tempo real com cores e textos.
-   **Informações Detalhadas:** Visualização da contagem de garfos de cada filósofo, do total de garfos disponíveis na mesa e da prioridade dos garfos na solução de hierarquia.
-   **Controles de Simulação:** Pause, reinicie a simulação atual ou retorne ao menu principal a qualquer momento sem fechar o programa.

##  O Problema: Jantar dos Filósofos

O "Jantar dos Filósofos" é um problema clássico da ciência da computação usado para ilustrar questões de sincronização em sistemas concorrentes. A configuração é a seguinte:

-   **Cinco filósofos** estão sentados em uma mesa redonda.
-   Entre cada par de filósofos adjacentes, há exatamente **um garfo**. Portanto, há cinco garfos no total.
-   No centro da mesa, há um grande prato de espaguete.
-   Um filósofo pode estar em um de dois estados: **pensando** ou **comendo**.

Para comer, um filósofo precisa de **dois garfos**: o que está à sua esquerda e o que está à sua direita. O dilema central, ou o *deadlock*, ocorre se todos os cinco filósofos decidirem comer ao mesmo tempo, e cada um pegar o garfo à sua esquerda. Nesse momento, todos os filósofos estarão segurando um garfo e esperando eternamente pelo segundo garfo (que está na mão de seu vizinho), e ninguém consegue comer. O sistema para.

## 🛠️ Dependências e Configuração

Antes de executar, garanta que você tenha os pré-requisitos instalados.

### Pré-requisitos
-   Python 3.8 ou superior
-   Git para clonar o repositório

### 1. Clone o Repositório

git clone https://github.com/ufjoao/dining-philosophers-simulation.git

##  Implementações

Este repositório contém dois tipos de simulações distintas:

1.  `aplicacao_jantar.py`: Uma implementação gráfica que deixa o usuário escolher e visualizar diferentes implementações que geram deadlocks e algumas que solucionam o problema.

2.  `solution_simulation.py` / `deadlock_garantido.py` / `deadlock_simulation.py` / `solution_waiter.py`: Implementações individuais que demonstram os métodos através de saídas de terminal e podem ser executadas uma por vez.

##  Como Executar

Navegue até a pasta do projeto clonado.

### Dependência do Tkinter (Linux)
Se você estiver no Linux, pode ser necessário instalar o pacote do Tkinter:

sudo apt update
sudo apt install python3-tk


### Execução da Aplicação Gráfica
Execute o comando abaixo para iniciar a janela principal da simulação:
python3 aplicacao_jantar.py


---

### Execuções Individuais (via Terminal)
A pasta clonada também contém execuções individuais com saída diretamente no terminal. Caso seja do seu interesse, execute os seguintes comandos:

**Simulação com Deadlock (Lento):**
python3 deadlock_simulation.py


**Simulação com Deadlock (Rápido/Garantido):**
python3 deadlock_garantido.py


**Solução com Hierarquia de Recursos:**
python3 solution_resource_hierarchy.py


**Solução com Garçom (Árbitro):**
python3 solution_waiter.py


---

> **Importante!**
> Os scripts de terminal rodam em um loop infinito. Para parar a execução de qualquer um deles, pressione `Ctrl+C` no terminal.