# Bibliotecas necessárias
import socket
import json
import time
import os
from pynput import keyboard

# Constantes que indicam os ícones do mapa
WALL = " # "
EMPTY = "   "
TREASURE = " ♦ "
PORTAL = " ▯ "
PLAYER_1 = " ♞ "
PLAYER_2 = " ♘ "

# Função que renderiza o mapa
def render_map(game_main_map):
    os.system("cls" if os.name == "nt" else "clear")
    
    for row in game_main_map:
            print("".join(row))
            
# Função que inicia e trata a conexão socket do cliente
def start_client():
    
    host = '127.0.0.1'
    port = 5000
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("Conectado ao servidor")
    
    # Função que trata o evento de pressionar uma tecla
    def on_press(key):
        try:
            if key.char == "w":
                request_move("UP")
            elif key.char == "s":
                request_move("DOWN")
            elif key.char == "a":
                request_move("LEFT")
            elif key.char == "d":
                request_move("RIGHT")
        except AttributeError:
            pass

    # Função que envia a requisição de movimento para o servidor
    def request_move(moviment):
        client_socket.send(moviment.encode())
    
    while True:
        message = client_socket.recv(1024).decode()
        if message == "START":
            print("Jogo iniciado pelo servidor")
            client_socket.send("READY".encode())
            break
        
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    time.sleep(2)
    
    while True:
        message = client_socket.recv(1024).decode()
        if message == "GAME_OVER":
            print("Jogo finalizado")
            break
        
        game_main_map = json.loads(message)

        render_map(game_main_map)
       
# Função main 
if __name__ == "__main__":
    start_client()