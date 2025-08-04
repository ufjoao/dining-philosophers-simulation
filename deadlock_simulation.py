import threading
import time
import random

class Philosopher(threading.Thread):
    def __init__(self, name, left_fork, right_fork):
        super().__init__()
        self.name = name
        self.left_fork = left_fork
        self.right_fork = right_fork

    def run(self):
        while True:
            # Pensa
            print(f'{self.name} está pensando.')
            time.sleep(random.uniform(1, 3))

            # Pega os garfos (aqui está o problema)
            print(f'{self.name} está com fome e vai pegar o garfo esquerdo.')
            self.left_fork.acquire()
            print(f'{self.name} pegou o garfo esquerdo. Vai tentar pegar o direito.')
            # Um pequeno delay aqui aumenta a chance de deadlock
            time.sleep(0.5) 
            
            self.right_fork.acquire()
            
            # Come
            print(f'{self.name} pegou os dois garfos e está comendo.')
            time.sleep(random.uniform(1, 3))

            # Larga os garfos
            self.right_fork.release()
            self.left_fork.release()
            print(f'{self.name} terminou de comer e largou os garfos.')

def main():
    num_philosophers = 5
    forks = [threading.Lock() for _ in range(num_philosophers)]
    
    # Cria os filósofos
    philosophers = []
    for i in range(num_philosophers):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % num_philosophers] # O vizinho à direita
        
        philosopher = Philosopher(f'Filósofo {i}', left_fork, right_fork)
        philosophers.append(philosopher)

    # Inicia as threads
    for p in philosophers:
        p.start()

    # Mantém a thread principal viva
    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()