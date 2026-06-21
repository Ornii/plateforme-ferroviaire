import socket

# non-privileged ports are > 1023
PORT = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", PORT))
s.listen()
while True:
    conn, addr = s.accept()
    print(f"Connected with {conn}")

    while True:
        buf = conn.recv(64)
        if len(buf) > 0:
            m = buf.decode()
            led_state = int(m)
            print("----Couleur du feu----")
            if led_state == 0:
                print("Rouge")
            else:
                print("Vert")
