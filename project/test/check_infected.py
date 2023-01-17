import socket
import time
import signal
from rich.live import Live
from rich.table import Table


def check_infected(ip_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip_address, 50000))
        client_socket.send("knock knock".encode())
        infected_status = client_socket.recv(8).decode() == "infected"
        client_socket.close
        return infected_status
    except:
        return False


def generate_table() -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="dim", width=12)
    table.add_column("Infected")
    table.add_row("Patient0\t", str(check_infected("172.16.238.10")))
    table.add_row("Target1\t", str(check_infected("172.16.238.2")))
    table.add_row("Target2\t", str(check_infected("172.16.238.3")))
    table.add_row("Target3\t", str(check_infected("172.16.238.4")))

    return table


signal.signal(signal.SIGINT, lambda signal_number, frame: exit(1))
print("Ctrl-C to exit")

with Live(generate_table(), refresh_per_second=2) as live:
    while True:
        time.sleep(0.5)
        live.update(generate_table())
