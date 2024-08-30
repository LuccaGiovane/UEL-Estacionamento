import tkinter as tk
from tkinter import ttk
import socket
import threading

class ParkScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Status das Estações de Estacionamento")

        self.tree = ttk.Treeview(root, columns=("Porta", "Status", "Vagas Totais", "Vagas Disponíveis"), show="headings")
        self.tree.heading("Porta", text="Porta da Estação")
        self.tree.heading("Status", text="Status da Estação")
        self.tree.heading("Vagas Totais", text="Vagas Totais")
        self.tree.heading("Vagas Disponíveis", text="Vagas Disponíveis")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.port_input_window()

    def port_input_window(self):
        input_window = tk.Toplevel(self.root)
        input_window.title("Configurar Monitor")

        tk.Label(input_window, text="Digite a porta para o monitor:").pack(pady=10)
        self.port_entry = tk.Entry(input_window)
        self.port_entry.pack(pady=10)

        tk.Button(input_window, text="Iniciar Monitor", command=self.start_monitor).pack(pady=10)

    def start_monitor(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", int(port)))
        self.server_socket.listen(5)
        print(f"Monitor ouvindo na porta {port}...")

        # Inicia uma thread para aceitar conexões
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def port_input_window(self):
        input_window = tk.Toplevel(self.root)
        input_window.title("Configurar Monitor")

        tk.Label(input_window, text="Digite a porta para o monitor:").pack(pady=10)
        self.port_entry = tk.Entry(input_window)
        self.port_entry.pack(pady=10)

        tk.Button(input_window, text="Iniciar Monitor", command=self.start_monitor_from_entry).pack(pady=10)

    def start_monitor_from_entry(self):
        port = self.port_entry.get()
        self.port_entry.master.destroy()
        self.start_monitor(port)

    def accept_connections(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        while True:
            try:
                mensagem = client_socket.recv(1024).decode()
                if not mensagem:
                    break
                self.update_station_status_from_message(mensagem)
            except (ConnectionResetError, socket.error):
                break
        client_socket.close()

    def update_station_status_from_message(self, mensagem):
        partes = mensagem.split(", ")
        if len(partes) == 4:
            port, status, vagas_totais, vagas_livres = partes
            self.update_station_status(port, status, vagas_totais, vagas_livres)

    def update_station_status(self, port, status, total_vagas, vagas_livres):
        for row in self.tree.get_children():
            if self.tree.item(row)["values"][0] == port:
                self.tree.item(row, values=(port, status, total_vagas, vagas_livres))
                return
        self.tree.insert("", "end", values=(port, status, total_vagas, vagas_livres))

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkScreen(root)
    root.mainloop()

