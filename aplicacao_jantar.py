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
    # (Esta classe não sofreu alterações nesta versão)
    def __init__(self, p_id, left_fork, right_fork, pause_event, **kwargs):
        super().__init__()
        self.p_id = p_id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.pause_event = pause_event
        self.running = True
        self.status = "pensando"
        self.fork_count = 0 

        self.waiter = kwargs.get('waiter')
        self.barrier = kwargs.get('barrier')
        self.sleep_between_forks = kwargs.get('sleep_between_forks', 0)
        
        self._send_update()

    def _send_update(self):
        update_queue.put(('status_update', self.p_id, self.status, self.fork_count))

    def set_status(self, new_status):
        self.status = new_status
        self._send_update()

    def pickup_forks(self):
        if self.waiter:
            update_queue.put(('call_waiter', self.p_id))
            self.waiter.acquire()
            update_queue.put(('end_call', self.p_id))
            
            self.left_fork.acquire(); self.fork_count = 1; self._send_update()
            self.right_fork.acquire(); self.fork_count = 2; self.set_status("comendo")
            self.waiter.release()
        else: 
            if self.barrier:
                try: self.barrier.wait(1)
                except (threading.BrokenBarrierError, RuntimeError): return

            self.left_fork.acquire(); self.fork_count = 1; self._send_update()
            time.sleep(self.sleep_between_forks)
            if not self.running: 
                self.left_fork.release(); self.fork_count = 0; self._send_update(); return

            self.right_fork.acquire(); self.fork_count = 2; self.set_status("comendo")

    def release_forks(self):
        self.right_fork.release(); self.fork_count = 1; self._send_update()
        self.left_fork.release(); self.fork_count = 0; self.set_status("pensando")

    def run(self):
        while self.running:
            self.pause_event.wait()
            
            if self.status == "pensando":
                time.sleep(random.uniform(1, 3)); self.set_status("com fome")
            elif self.status == "com fome":
                self.pickup_forks()
            elif self.status == "comendo":
                time.sleep(random.uniform(2, 4)); self.release_forks()
            
            if not self.running: break


class App(tk.Tk):
    # (Esta classe não sofreu alterações nesta versão)
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Jantar dos Filósofos - Simulação")
        self.geometry("700x600")

        self.active_threads = []
        self.simulation_type = None
        self.pause_event = threading.Event()
        self.pause_event.set()

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
        # O setup da simulação agora é chamado no start_simulation
        # para garantir que os garfos sejam passados corretamente.

    def start_simulation(self, sim_type):
        self.stop_simulation()
        self.simulation_type = sim_type
        
        forks = [threading.Lock() for _ in range(5)]
        kwargs = {'pause_event': self.pause_event}

        if sim_type == "deadlock_rapido":
            kwargs['barrier'] = Barrier(5)
            kwargs['sleep_between_forks'] = 0.1
        elif sim_type == "solucao_garcom":
            kwargs['waiter'] = threading.Lock()
        
        # ALTERADO: Prepara a tela de simulação e passa os garfos para ela
        self.frames["SimulationFrame"].prepare_for_simulation(sim_type, forks)
        self.show_frame("SimulationFrame")

        for i in range(5):
            left_fork_idx, right_fork_idx = i, (i + 1) % 5
            
            if sim_type == "solucao_hierarquia" and left_fork_idx > right_fork_idx:
                p = ControllablePhilosopher(i, forks[right_fork_idx], forks[left_fork_idx], **kwargs)
            else:
                p = ControllablePhilosopher(i, forks[left_fork_idx], forks[right_fork_idx], **kwargs)
            
            self.active_threads.append(p)
            p.start()

    def stop_simulation(self):
        # ... (sem alterações aqui)
        for t in self.active_threads: t.running = False
        if self.simulation_type and "deadlock" in self.simulation_type:
             for t in self.active_threads:
                if t.left_fork.locked(): t.left_fork.release()
                if t.right_fork.locked(): t.right_fork.release()
        for t in self.active_threads: t.join(timeout=0.1)
        self.active_threads = []
        while not update_queue.empty(): update_queue.get()

    def return_to_menu(self):
        self.stop_simulation()
        self.show_frame("MenuFrame")

    def toggle_pause(self):
        # ... (sem alterações aqui)
        if self.pause_event.is_set():
            self.pause_event.clear(); self.frames["SimulationFrame"].pause_btn.config(text="Continuar")
        else:
            self.pause_event.set(); self.frames["SimulationFrame"].pause_btn.config(text="Pausar")

    def restart_simulation(self):
        # ... (sem alterações aqui)
        sim_type = self.simulation_type
        self.stop_simulation()
        self.start_simulation(sim_type)
        if not self.pause_event.is_set(): self.toggle_pause()


class MenuFrame(tk.Frame):
    # (Esta classe não sofreu alterações)
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
        self.philosopher_coords = [(250, 50), (400, 150), (350, 300), (150, 300), (100, 150)]
        self.waiter_coords = (250, 225)
        self.waiter_lines = {}
        self.fork_objects = [] # NOVO: Guarda os objetos Lock dos garfos
        self.fork_shapes = {}  # NOVO: Guarda os IDs dos desenhos dos garfos

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        sim_canvas_frame = tk.Frame(main_frame)
        sim_canvas_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        self.title_label = tk.Label(sim_canvas_frame, text="", font=tkfont.Font(family='Helvetica', size=14, weight="bold"))
        self.title_label.pack(pady=10)
        self.canvas = tk.Canvas(sim_canvas_frame, width=500, height=400)
        self.canvas.pack()
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", padx=10, pady=20)

        # NOVO: Frame de informações da mesa
        table_info_frame = tk.LabelFrame(right_frame, text="Informações da Mesa", font=tkfont.Font(family='Helvetica', size=10, weight="bold"))
        table_info_frame.pack(pady=20, anchor="n", fill="x")
        self.available_forks_label = tk.Label(table_info_frame, text="Garfos Disponíveis: 5", font=tkfont.Font(size=10))
        self.available_forks_label.pack(anchor="w", padx=5, pady=2)
        
        legend_frame = tk.LabelFrame(right_frame, text="Legenda dos Filósofos", font=tkfont.Font(family='Helvetica', size=10, weight="bold"))
        legend_frame.pack(pady=20, anchor="n")
        states = {"pensando": "yellow", "com fome": "orange", "comendo": "green"}
        for state, color in states.items():
            f = tk.Frame(legend_frame); tk.Label(f, text=" ", bg=color, relief="solid", borderwidth=1).pack(side="left", ipadx=5); tk.Label(f, text=f" = {state.title()}").pack(side="left", anchor="w"); f.pack(anchor="w", padx=5, pady=2)
        
        controls_frame = tk.LabelFrame(right_frame, text="Controles", font=tkfont.Font(family='Helvetica', size=10, weight="bold"))
        controls_frame.pack(pady=20, anchor="n")
        self.pause_btn = tk.Button(controls_frame, text="Pausar", command=controller.toggle_pause); self.pause_btn.pack(fill="x", padx=5, pady=2)
        restart_btn = tk.Button(controls_frame, text="Reiniciar", command=controller.restart_simulation); restart_btn.pack(fill="x", padx=5, pady=2)
        menu_btn = tk.Button(controls_frame, text="Voltar ao Menu", command=controller.return_to_menu); menu_btn.pack(fill="x", padx=5, pady=2)

        self.update_canvas()

    # ALTERADO: Recebe a lista de garfos do controlador
    def prepare_for_simulation(self, sim_type, forks):
        self.title_label.config(text=sim_type.replace("_", " ").title())
        self.canvas.delete("all")
        self.fork_objects = forks # Guarda a referência aos Locks
        self.philosopher_shapes, self.fork_count_texts, self.fork_shapes = {}, {}, {}

        # Desenha os garfos e suas prioridades
        fork_positions = []
        for i in range(5):
            p1 = self.philosopher_coords[i]
            p2 = self.philosopher_coords[(i + 1) % 5]
            # Ponto médio entre dois filósofos
            fork_pos = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            fork_positions.append(fork_pos)
            
            shape = self.canvas.create_rectangle(fork_pos[0]-5, fork_pos[1]-15, fork_pos[0]+5, fork_pos[1]+15, fill="gray", tags=f"f_shape_{i}")
            self.fork_shapes[i] = shape
            
            # NOVO: Mostra a prioridade (índice) do garfo na solução de hierarquia
            if sim_type == "solucao_hierarquia":
                self.canvas.create_text(fork_pos[0], fork_pos[1], text=str(i), fill="white", font=tkfont.Font(size=10, weight="bold"))

        if sim_type == "solucao_garcom":
            x, y = self.waiter_coords; self.canvas.create_rectangle(x-15, y-15, x+15, y+15, fill="lightblue", outline="black", tags="waiter"); self.canvas.create_text(x, y, text="Garçom")

        for i in range(5):
            x, y = self.philosopher_coords[i]
            self.philosopher_shapes[i] = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="gray", tags=f"p_shape_{i}")
            self.canvas.create_text(x, y-30, text=f"Filósofo {i}")
            self.fork_count_texts[i] = self.canvas.create_text(x, y, text="0", font=tkfont.Font(size=12, weight="bold"))

    def update_canvas(self):
        try:
            # NOVO: Atualiza a cor dos garfos com base no estado .locked()
            available_forks = 0
            if self.fork_objects:
                for i, fork_lock in enumerate(self.fork_objects):
                    if fork_lock.locked():
                        self.canvas.itemconfig(self.fork_shapes[i], fill="red")
                    else:
                        self.canvas.itemconfig(self.fork_shapes[i], fill="gray")
                        available_forks += 1
                self.available_forks_label.config(text=f"Garfos Disponíveis: {available_forks}")

            # Processa a fila de mensagens da thread
            while not update_queue.empty():
                message = update_queue.get_nowait()
                msg_type, p_id = message[0], message[1]

                if msg_type == 'status_update':
                    status, fork_count = message[2], message[3]
                    colors = {"pensando": "yellow", "com fome": "orange", "comendo": "green"}
                    self.canvas.itemconfig(self.philosopher_shapes[p_id], fill=colors.get(status, "gray"))
                    self.canvas.itemconfig(self.fork_count_texts[p_id], text=str(fork_count))
                
                elif msg_type == 'call_waiter':
                    px, py = self.philosopher_coords[p_id]; wx, wy = self.waiter_coords
                    self.waiter_lines[p_id] = self.canvas.create_line(px, py, wx, wy, fill="blue", dash=(4, 2), tags=f"line_{p_id}")
                
                elif msg_type == 'end_call':
                    if p_id in self.waiter_lines: self.canvas.delete(self.waiter_lines[p_id]); del self.waiter_lines[p_id]
        finally:
            self.controller.after(100, self.update_canvas)

if __name__ == "__main__":
    app = App()
    app.mainloop()