import tkinter as tk
from tkinter import font as tkfont
import threading
import queue
import time
import random
from threading import Barrier

# Fila para comunicação entre as threads dos filósofos e a GUI
update_queue = queue.Queue()


class ControllablePhilosopher(threading.Thread):
    """
    Uma classe de Filósofo que pode ser parada e pausada externamente.
    """
    def __init__(self, p_id, left_fork, right_fork, pause_event, **kwargs):
        super().__init__()
        self.p_id = p_id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.pause_event = pause_event
        self.running = True  # Flag para parar a thread de forma limpa
        self.status = "pensando"

        # Argumentos específicos de cada simulação
        self.waiter = kwargs.get('waiter')
        self.barrier = kwargs.get('barrier')
        self.sleep_between_forks = kwargs.get('sleep_between_forks', 0)

    def set_status(self, new_status):
        self.status = new_status
        # Envia uma tupla com o ID e o novo status para a GUI
        update_queue.put((self.p_id, self.status))

    def run(self):
        while self.running:
            # Ponto de pausa: a thread irá bloquear aqui se o evento não estiver "setado"
            self.pause_event.wait() 

            # Lógica do Filósofo (pensa, fica com fome, come)
            if self.status == "pensando":
                self.set_status("pensando")
                time.sleep(random.uniform(1, 3))
                self.set_status("com fome")

            elif self.status == "com fome":
                # Lógica de aquisição de garfos varia com o modo
                if self.waiter: # Modo Garçom
                    self.waiter.acquire()
                    self.left_fork.acquire()
                    self.right_fork.acquire()
                    self.waiter.release()
                    self.set_status("comendo")
                else: # Modos de Deadlock ou Hierarquia
                    if self.barrier:
                        try: self.barrier.wait(1)
                        except threading.BrokenBarrierError: break
                    
                    self.left_fork.acquire()
                    time.sleep(self.sleep_between_forks)
                    if not self.running: # Checa de novo antes de pegar o segundo garfo
                        self.left_fork.release()
                        break
                    self.right_fork.acquire()
                    self.set_status("comendo")

            elif self.status == "comendo":
                time.sleep(random.uniform(2, 4))
                self.right_fork.release()
                self.left_fork.release()
                self.set_status("pensando")


class App(tk.Tk):
    """
    Controlador Principal da Aplicação.
    Gerencia a troca de telas e o ciclo de vida da simulação.
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Jantar dos Filósofos - Simulação")
        self.geometry("600x600")

        self.active_threads = []
        self.simulation_type = None
        self.pause_event = threading.Event()
        self.pause_event.set() # Começa despausado

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MenuFrame, SimulationFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "SimulationFrame":
            frame.update_title()

    def start_simulation(self, sim_type):
        self.stop_simulation() # Garante que qualquer simulação anterior pare
        self.simulation_type = sim_type
        
        forks = [threading.Lock() for _ in range(5)]
        kwargs = {'pause_event': self.pause_event}

        if sim_type == "deadlock_rapido":
            kwargs['barrier'] = Barrier(5)
            kwargs['sleep_between_forks'] = 0.1
        elif sim_type == "solucao_garcom":
            kwargs['waiter'] = threading.Lock()
        
        for i in range(5):
            left_fork = forks[i]
            right_fork = forks[(i + 1) % 5]

            if sim_type == "solucao_hierarquia":
                if i < 4:
                    p = ControllablePhilosopher(i, left_fork, right_fork, **kwargs)
                else: # Último filósofo pega os garfos em ordem invertida
                    p = ControllablePhilosopher(i, right_fork, left_fork, **kwargs)
            else:
                 p = ControllablePhilosopher(i, left_fork, right_fork, **kwargs)
            
            self.active_threads.append(p)
            p.start()

        self.show_frame("SimulationFrame")

    def stop_simulation(self):
        # Manda todas as threads pararem
        for t in self.active_threads:
            t.running = False
        
        # Libera locks que podem estar bloqueando a saída das threads
        # (Isso é um truque para destravar o deadlock e permitir que as threads terminem)
        if self.simulation_type and "deadlock" in self.simulation_type:
             for t in self.active_threads:
                if t.left_fork.locked():
                    t.left_fork.release()

        # Espera um pouco para as threads terminarem
        for t in self.active_threads:
            t.join(timeout=0.1)

        self.active_threads = []
        # Limpa a fila para a próxima simulação
        while not update_queue.empty():
            update_queue.get()

    def return_to_menu(self):
        self.stop_simulation()
        self.show_frame("MenuFrame")

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear() # Pausa
            self.frames["SimulationFrame"].pause_btn.config(text="Continuar")
        else:
            self.pause_event.set() # Continua
            self.frames["SimulationFrame"].pause_btn.config(text="Pausar")

    def restart_simulation(self):
        sim_type = self.simulation_type
        self.stop_simulation()
        self.start_simulation(sim_type)
        if not self.pause_event.is_set(): # Garante que reinicie despausado
             self.toggle_pause()


class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Escolha uma Simulação", font=tkfont.Font(family='Helvetica', size=18, weight="bold"))
        label.pack(side="top", fill="x", pady=20)

        simulations = {
            "Deadlock (Lento)": "deadlock_lento",
            "Deadlock (Rápido/Garantido)": "deadlock_rapido",
            "Solução com Hierarquia": "solucao_hierarquia",
            "Solução com Garçom": "solucao_garcom"
        }

        for text, sim_type in simulations.items():
            btn = tk.Button(self, text=text, command=lambda st=sim_type: controller.start_simulation(st))
            btn.pack(pady=10, padx=50, fill="x")


class SimulationFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.title_label = tk.Label(self, text="", font=tkfont.Font(family='Helvetica', size=14, weight="bold"))
        self.title_label.pack(pady=10)

        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack()
        
        self.philosopher_shapes = {}
        self.philosopher_labels = {}
        positions = [(200, 50), (350, 150), (300, 300), (100, 300), (50, 150)]
        for i in range(5):
            x, y = positions[i]
            shape = self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="yellow", tags=f"p{i}")
            label = self.canvas.create_text(x, y, text=f"Filósofo {i}")
            self.philosopher_shapes[i] = shape
            self.philosopher_labels[i] = label
        
        controls_frame = tk.Frame(self)
        controls_frame.pack(pady=20)

        self.pause_btn = tk.Button(controls_frame, text="Pausar", command=controller.toggle_pause)
        self.pause_btn.pack(side="left", padx=10)
        restart_btn = tk.Button(controls_frame, text="Reiniciar", command=controller.restart_simulation)
        restart_btn.pack(side="left", padx=10)
        menu_btn = tk.Button(controls_frame, text="Voltar ao Menu", command=controller.return_to_menu)
        menu_btn.pack(side="left", padx=10)

        self.update_canvas()

    def update_title(self):
        title = self.controller.simulation_type.replace("_", " ").title()
        self.title_label.config(text=title)

    def update_canvas(self):
        try:
            while not update_queue.empty():
                p_id, status = update_queue.get_nowait()
                colors = {"pensando": "yellow", "com fome": "orange", "comendo": "green"}
                self.canvas.itemconfig(self.philosopher_shapes[p_id], fill=colors.get(status, "gray"))
        finally:
            self.controller.after(100, self.update_canvas)


if __name__ == "__main__":
    app = App()
    app.mainloop()