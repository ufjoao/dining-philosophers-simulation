import threading
import time
import random

# A classe Philosopher permanece exatamente a mesma da versão com deadlock
class Philosopher(threading.Thread):
    def __init__(self, name, left_fork, right_fork):
        super().__init__()
        self.name = name
        self.left_fork = left_fork
        self.right_fork = right_fork

    def run(self):
        while True:
            print(f'{self.name} está pensando.')
            time.sleep(random.uniform(1, 3))

            print(f'{self.name} está com fome.')
            self.left_fork.acquire()
            print(f'{self.name} pegou o primeiro garfo.')
            
            self.right_fork.acquire()
            
            print(f'{self.name} pegou o segundo garfo e está comendo.')
            time.sleep(random.uniform(1, 3))

            self.right_fork.release()
            self.left_fork.release()
            print(f'{self.name} terminou de comer e largou os garfos.')

def main():
    num_philosophers = 5
    forks = [threading.Lock() for _ in range(num_philosophers)]
    
    philosophers = []
    for i in range(num_philosophers):
        left_fork_index = i
        right_fork_index = (i + 1) % num_philosophers

        # A LÓGICA DA SOLUÇÃO ESTÁ AQUI!
        # Impomos a hierarquia: sempre pegar o garfo de menor índice primeiro.
        if left_fork_index < right_fork_index:
            first_fork = forks[left_fork_index]
            second_fork = forks[right_fork_index]
        else:
            # O último filósofo (4) tenta pegar o garfo 0 e depois o 4.
            first_fork = forks[right_fork_index]
            second_fork = forks[left_fork_index]
            
        philosopher = Philosopher(f'Filósofo {i}', first_fork, second_fork)
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()