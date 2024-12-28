# Bibliotecas necessárias
import socket
import random
import json
import time
import threading

# Constantes que indicam os ícones do mapa
WALL = " # "
EMPTY = "   "
TREASURE = " ♦ "
PORTAL = " ▯ "
PLAYER_1 = " ♞ "
PLAYER_2 = " ♘ "

# Cria uma matriz 8x8 preenchida com EMPTY
game_main_map = [[EMPTY for _ in range(8)] for _ in range(8)]

# Adiciona as paredes ao redor da matriz
for i in range(8):
    game_main_map[0][i] = WALL
    game_main_map[7][i] = WALL
    game_main_map[i][0] = WALL
    game_main_map[i][7] = WALL

# Lista que armazena os clientes conectados
clients = []

# Variável que armazena a quantidade de tesouros restantes
remaining_treasures = 4

# Função que define a posição dos jogadores
def set_player_position():
    for client in clients:
        if client.get("id") == 1:
            game_main_map[1][1] = PLAYER_1
            client["position"] = [1, 1]
        else:
            game_main_map[6][6] = PLAYER_2
            client["position"] = [6, 6]

# Função que define a posição dos tesouros
def set_treasure_position():
    treasures = 0
    while treasures < 4:
        x = random.randint(1, 6)
        y = random.randint(1, 6)
        if game_main_map[x][y] == EMPTY:
            game_main_map[x][y] = TREASURE
            treasures += 1

# Função que define a posição dos portais          
def set_portal_position():
    portals = 0
    while portals < 2:
        x = random.randint(1, 6)
        y = random.randint(1, 6)
        if game_main_map[x][y] == EMPTY:
            game_main_map[x][y] = PORTAL
            portals += 1

def monitoring_requests(clients):
    while True:
        for client in clients:
            message = client.get("connection").recv(1024).decode()
            if message != "":
                evaluate_move_request(client, message)

# Função que avalia a requisição de movimento          
def evaluate_move_request(client, message):
    global remaining_treasures
    
    print(f"{client.get("name")} → {message}")
    
    if message == "UP":
        if game_main_map[client.get("position")[0] - 1][client.get("position")[1]] == EMPTY:
            move_player(client, -1, 0)
        elif game_main_map[client.get("position")[0] - 1][client.get("position")[1]] == TREASURE:
            move_player(client, -1, 0)
            remaining_treasures -= 1
            client["score"] += 1
            
    if message == "DOWN":
        if game_main_map[client.get("position")[0] + 1][client.get("position")[1]] == EMPTY:
            move_player(client, 1, 0)
        elif game_main_map[client.get("position")[0] + 1][client.get("position")[1]] == TREASURE:
            move_player(client, 1, 0)
            remaining_treasures -= 1
            client["score"] += 1
            
    if message == "LEFT":
        if game_main_map[client.get("position")[0]][client.get("position")[1] - 1] == EMPTY:
            move_player(client, 0, -1)
        elif game_main_map[client.get("position")[0]][client.get("position")[1] - 1] == TREASURE:
            move_player(client, 0, -1)
            remaining_treasures -= 1
            client["score"] += 1  
              
    if message == "RIGHT":
        if game_main_map[client.get("position")[0]][client.get("position")[1] + 1] == EMPTY:
            move_player(client, 0, 1)
        elif game_main_map[client.get("position")[0]][client.get("position")[1] + 1] == TREASURE:
            move_player(client, 0, 1)
            remaining_treasures -= 1
            client["score"] += 1

def move_player(client, x, y):
    game_main_map[client.get("position")[0]][client.get("position")[1]] = EMPTY
    client["position"][0] += x
    client["position"][1] += y
    game_main_map[client.get("position")[0]][client.get("position")[1]] = PLAYER_1 if client.get("id") == 1 else PLAYER_2
    
# Função que inicia o servidor
def start_server():
    host = '127.0.0.1'
    port = 5000
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    print("Servidor iniciado, aguardando conexões...")
    
    while len(clients) < 2:
        conn, addr = server_socket.accept()
        player = {"name": "Player " + str(len(clients) + 1), "id": len(clients) + 1, "connection": conn, "position": [0, 0], "score": 0}		
        clients.append(player)
        print("Conectado com:", addr,"\nPlayer:", player.get("name"))
    
    set_player_position()
    set_treasure_position()
    set_portal_position()
        
    print("Iniciando o jogo...")
    for client in clients:
        client.get("connection").send("START".encode())
    
    index = 0
    while index < len(clients):
        message = clients[index].get("connection").recv(1024).decode()
        if message == "READY":
            print(f"{clients[index].get("name")} → {message}")
            index += 1
    
    time.sleep(2)
    
    moviment_thread = threading.Thread(target=monitoring_requests, args=(clients,))
    moviment_thread.start()
    
    while remaining_treasures >= 0:
        game_map_str = json.dumps(game_main_map)
        for client in clients:
            client.get("connection").send(game_map_str.encode())
        time.sleep(0.5)
    
    # Fechar conexões após o uso
    for client in clients:
        client.get("connection").close()
        
    server_socket.close()

# Função main
if __name__ == "__main__":
    start_server()