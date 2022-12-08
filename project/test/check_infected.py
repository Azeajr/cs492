import socket


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


print("Patient0:\t", check_infected("172.16.238.10"))
print("Target1:\t", check_infected("172.16.238.2"))
print("Target2:\t", check_infected("172.16.238.3"))
print("Target3:\t", check_infected("172.16.238.4"))
