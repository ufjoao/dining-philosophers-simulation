import threading
import time
import random

# NOVO: Importamos a classe Barrier
from threading import Barrier

class Philosopher(threading.Thread):
    # ALTERADO: Adicionamos o 'barrier' no construtor
    def __init__(self, name, left_fork, right_fork, barrier):
        super().__init__()
        self.name = name
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.barrier = barrier

    def run(self):
        while True:
            print(f'{self.name} está pensando.')
            time.sleep(random.uniform(1, 3))

            print(f'{self.name} está com fome e vai para a mesa.')
            
            # NOVO: Barreira de sincronização
            # Todas as threads vão parar aqui até que 5 delas chamem .wait()
            # Isso força todas a tentarem pegar o garfo ao mesmo tempo.
            try:
                self.barrier.wait()
            except threading.BrokenBarrierError:
                # Isso pode acontecer se o programa for interrompido
                pass

            # A corrida pelos garfos começa AGORA
            print(f'{self.name} vai pegar o garfo esquerdo.')
            self.left_fork.acquire()
            print(f'{self.name} PEGOU o garfo esquerdo.')
            
            # NOVO: Pequena pausa para garantir que os outros também peguem o primeiro garfo
            time.sleep(0.1) 
            
            print(f'{self.name} vai pegar o garfo direito.')
            self.right_fork.acquire() # <-- DEADLOCK ACONTECERÁ AQUI
            
            print(f'{self.name} pegou os dois garfos e está comendo.')
            time.sleep(random.uniform(1, 3))

            self.right_fork.release()
            self.left_fork.release()
            print(f'{self.name} terminou de comer e largou os garfos.')

def main():
    num_philosophers = 5
    forks = [threading.Lock() for _ in range(num_philosophers)]
    
    # NOVO: Cria uma barreira que espera por todas as 5 threads de filósofos
    barrier = Barrier(num_philosophers)
    
    philosophers = []
    for i in range(num_philosophers):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % num_philosophers]
        
        # ALTERADO: Passa a barreira para cada filósofo
        philosopher = Philosopher(f'Filósofo {i}', left_fork, right_fork, barrier)
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()