import threading
import time
import random

class Philosopher(threading.Thread):
    def __init__(self, name, left_fork, right_fork, waiter):
        super().__init__()
        self.name = name
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.waiter = waiter # O garçom (um Lock central)

    def run(self):
        while True:
            print(f'{self.name} está pensando.')
            time.sleep(random.uniform(1, 3))
            
            print(f'{self.name} está com fome e vai pedir permissão ao garçom.')
            
            # Pede permissão ao garçom antes de tocar nos garfos
            with self.waiter:
                print(f'{self.name} recebeu permissão. Vai pegar os garfos.')
                self.left_fork.acquire()
                self.right_fork.acquire()
                # Uma vez que ele tem os garfos, o garçom é liberado pelo 'with'
                # e outros podem pedir permissão.
            
            print(f'{self.name} está comendo.')
            time.sleep(random.uniform(2, 4))

            # Libera os garfos após comer
            self.left_fork.release()
            self.right_fork.release()
            print(f'{self.name} terminou de comer e largou os garfos.')

def main():
    num_philosophers = 5
    forks = [threading.Lock() for _ in range(num_philosophers)]
    
    # O garçom é um único Lock para toda a mesa
    waiter = threading.Lock() 
    
    philosophers = []
    for i in range(num_philosophers):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % num_philosophers]
        philosopher = Philosopher(f'Filósofo {i}', left_fork, right_fork, waiter)
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()