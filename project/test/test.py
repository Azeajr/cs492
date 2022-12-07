#!/usr/bin/env python3

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import socket

with SSHClient() as ssh:
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh.connect(
            hostname="172.17.0.2",
            username="pi",
            password="sunshine",
            port=22,
            timeout=1,
        )
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(["test.py", "requirements.txt"])

        cmd = "python -m ensurepip --upgrade"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.readlines())


        cmd = "python -m pip install -r requirements.txt"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.readlines())


        # cmd = "chmod +x test.py"
        # stdin, stdout, stderr = ssh.exec_command(cmd)

        cmd = "nohup python test.py &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.readlines())

    except:
        pass


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 50000))
server_socket.listen(5)
while True:
    conn, addr = server_socket.accept()
    from_client = ""
    while True:
        data = conn.recv(11)
        if not data:
            break
        from_client += data.decode()
        if from_client == "knock knock":
            conn.send("infected".encode())
    conn.close()


# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# try:
#     client_socket.connect(("172.17.0.2", 50000))
#     client_socket.send("knock knock".encode())
#     response = client_socket.recv(8).decode()
#     print(response)
#     infected_status = response == "infected"
#     client_socket.close
#     print("True")
# except Exception as e:
#     print(e, "False")