import socket
import threading
import sys

# Server Setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))
server.listen(2)

clients = []
choices = {}
names = {}
lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        name = conn.recv(1024).decode()

        with lock:
            is_first_player = len(names) == 0  # First to join is starter
            names[conn] = name

        # Send starter flag
        conn.send(b"STARTER" if is_first_player else b"NOT_STARTER")

        while True:
            choice = conn.recv(1024).decode()
            if not choice:
                break

            with lock:
                choices[conn] = choice
                if len(choices) == 2:
                    process_game()
    except:
        print(f"[DISCONNECTED] {addr}")
        sys.exit()
    finally:
        with lock:
            if conn in clients:
                clients.remove(conn)
            if conn in choices:
                del choices[conn]
            if conn in names:
                del names[conn]
        conn.close()

def process_game():
    players = list(choices.keys())
    c1, c2 = choices[players[0]], choices[players[1]]
    n1, n2 = names[players[0]], names[players[1]]

    if c1 == c2:
        msg = f"Both chose {c1}. It's a Draw!"
        players[0].send(msg.encode())
        players[1].send(msg.encode())
    else:
        wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if wins[c1] == c2:
            players[0].send(f"YOU win! {c1.capitalize()} beats {c2}.".encode())
            players[1].send(f"YOU lose! {c1.capitalize()} beats {c2}.".encode())
        else:
            players[1].send(f"YOU win! {c2.capitalize()} beats {c1}.".encode())
            players[0].send(f"YOU lose! {c2.capitalize()} beats {c1}.".encode())
    choices.clear()

print("[SERVER STARTED] Waiting for players...")

while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
    thread.start()
