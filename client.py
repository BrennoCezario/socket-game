# Bibliotecas necessárias
import socket
import json
import time
import os
from pynput import keyboard

# Constante que armazena o total de pontos
TOTAL_POINTS = 11600

# Variável que armazena dados do jogador
player = ""

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
        if "START" in message:
            player = message.split(":")[1]
            print("Jogo iniciado pelo servidor")
            client_socket.send("READY".encode())
            break
        
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    time.sleep(2)
    
    while True:
        message = client_socket.recv(2048).decode()
        if "GAME_OVER" in message:
            print("Jogo finalizado")
            break
        elif message:
            game_main_map = json.loads(message)
            render_map(game_main_map)
            time.sleep(0.4)
        else:
            continue
    
    client_socket.send("POINTS".encode())
    
    listener.stop()
    
    while True:
        message = client_socket.recv(1024).decode()
        if "WINNER" in message:
            score = message.split(":")[1]
            print("Parabéns, você venceu o jogo!")
            print("Sua pontuação foi:", score)
            print(f"Placar:\n 1º Lugar: {"Player 1"} → {score} pontos\n 2º Lugar: {"Player 2"} → {TOTAL_POINTS - int(score)} pontos") if player == "1" else print(f"Placar:\n 1º Lugar: {"Player 2"} → {score} pontos\n 2º Lugar: {"Player 1"} → {TOTAL_POINTS-int(score)} pontos")
            break
        elif "LOSER" in message:
            score = message.split(":")[1]
            print("Sinto muito, você perdeu o jogo!")
            print("Sua pontuação foi:", score)
            print(f"Placar:\n 1º Lugar: {"Player 1"} → {TOTAL_POINTS - int(score)} pontos\n 2º Lugar: {"Player 2"} → {score} pontos") if player == "2" else print(f"Placar:\n 1º Lugar: {"Player 2"} → {TOTAL_POINTS - int(score)} pontos\n 2º Lugar: {"Player 1"} → {score} pontos")
            break
        elif "DRAW" in message:
            print(f"Empate!\n Player 1 → {TOTAL_POINTS/2} pontos\n Player 2 → {TOTAL_POINTS/2} pontos")
            break
    
    client_socket.send("CLOSE".encode())
       
# Função main 
if __name__ == "__main__":
    start_client()