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
GREAT_TREASURE = " $ "

MAIN_MAP_SIZE = 16
TREASURE_ROOM_SIZE = 8

# Cria uma matriz 8x8 preenchida com EMPTY
game_main_map = [[EMPTY for _ in range(MAIN_MAP_SIZE)] for _ in range(MAIN_MAP_SIZE)]

# Adiciona as paredes ao redor da matriz
for i in range(MAIN_MAP_SIZE):
    game_main_map[0][i] = WALL
    game_main_map[15][i] = WALL
    game_main_map[i][0] = WALL
    game_main_map[i][15] = WALL
    
treasure_rooms = []

id =1
for treasure_room in range(2):
    treasure_room = {"room_id" : id, "room": [[EMPTY for _ in range(TREASURE_ROOM_SIZE)] for _ in range(TREASURE_ROOM_SIZE)], "position": [0,0], "stopwatch":0}
    for i in range(TREASURE_ROOM_SIZE):
        treasure_room.get("room")[0][i] = WALL
        treasure_room.get("room")[7][i] = WALL
        treasure_room.get("room")[i][0] = WALL
        treasure_room.get("room")[i][7] = WALL
    treasure_rooms.append(treasure_room)
    id += 1

treasure_room_semaphores = [threading.Semaphore(1) for _ in range(len(treasure_rooms))]

clients = [] # Lista que armazena os clientes conectados

remaining_treasures = 90 # Variável que armazena a quantidade de tesouros restantes

# Função que define a posição dos jogadores
def set_player_position():
    for client in clients:
        if client.get("id") == 1:
            game_main_map[1][1] = PLAYER_1
            client["position"] = [1, 1]
        else:
            game_main_map[14][14] = PLAYER_2
            client["position"] = [14, 14]

# Função que define a posição dos tesouros
def set_treasure_position():
    treasures = 0
    while treasures < 20:
        x = random.randint(1, 14)
        y = random.randint(1, 14)
        if game_main_map[x][y] == EMPTY:
            game_main_map[x][y] = TREASURE
            treasures += 1

# Função que define a posição dos portais          
def set_portal_position():
    portals = 0
    while portals < 2:
        x = random.randint(1, 14)
        y = random.randint(1, 14)
        if game_main_map[x][y] == EMPTY:
            game_main_map[x][y] = PORTAL
            treasure_rooms[portals]["position"] = [x, y]
            portals += 1

# Função que define a posição do tesouros nas salas de tesouros
def set_treasure_room_treasures_position():
    for treasure_room in treasure_rooms:
        treasures = 0
        while treasures < 35:
            x = random.randint(1, 6)
            y = random.randint(1, 6)
            if treasure_room.get("room")[x][y] == EMPTY:
                if x == 1 and y == 1:
                    pass
                else:
                    if treasures == 10 or treasures == 24:
                        treasure_room.get("room")[x][y] = GREAT_TREASURE
                        treasures += 1
                    else:
                        treasure_room.get("room")[x][y] = TREASURE
                        treasures += 1
                    print("TREASURES", treasures, "→", x, y)
    
# Função que monitora as requisições de movimento
def monitoring_requests(clients):
    while remaining_treasures > 0:
        for client in clients:
            try:
                message = client.get("connection").recv(1024).decode()
                if message:
                    evaluate_move_request(client, message)
            except ConnectionAbortedError:
                print(f"Conexão com {client.get('name')} foi abortada.")
                clients.remove(client)
                break
            except ConnectionResetError:
                print(f"Conexão com {client.get('name')} foi resetada.")
                clients.remove(client)
                break

# Função que avalia a requisição de movimento          
def evaluate_move_request(client, message):
    global remaining_treasures
    
    print(f"{client.get("name")} → {message}")
    
    if "UP" in message:
        if client.get("current_map")[client.get("position")[0] - 1][client.get("position")[1]] == EMPTY:
            move_player(client, -1, 0)
        elif client.get("current_map")[client.get("position")[0] - 1][client.get("position")[1]] == TREASURE:
            move_player(client, -1, 0)
            remaining_treasures -= 1
            client["score"] += 100
            print(f"{client.get("name")} → {client.get("score")} pontos")
        elif client.get("current_map")[client.get("position")[0] - 1][client.get("position")[1]] == PORTAL:
            move_player_to_portal(client, -1, 0)
            print(f"{client.get("name")} → Entrou no Portal")
            goto_treasure_room(client, client.get("position")[0] - 1, client.get("position")[1])
        elif client.get("current_map")[client.get("position")[0] - 1][client.get("position")[1]] == GREAT_TREASURE:
            move_player(client, -1, 0)
            remaining_treasures -= 1
            client["score"] += 500
            print(f"{client.get("name")} → {client.get("score")} pontos")
            
    if "DOWN" in message:
        if client.get("current_map")[client.get("position")[0] + 1][client.get("position")[1]] == EMPTY:
            move_player(client, 1, 0)
        elif client.get("current_map")[client.get("position")[0] + 1][client.get("position")[1]] == TREASURE:
            move_player(client, 1, 0)
            remaining_treasures -= 1
            client["score"] += 100
            print(f"{client.get("name")} → {client.get("score")} pontos")
        elif client.get("current_map")[client.get("position")[0] + 1][client.get("position")[1]] == PORTAL:
            move_player_to_portal(client, 1, 0)
            print(f"{client.get("name")} → Entrou no Portal")
            goto_treasure_room(client, client.get("position")[0] + 1, client.get("position")[1])
        elif client.get("current_map")[client.get("position")[0] + 1][client.get("position")[1]] == GREAT_TREASURE:
            move_player(client, 1, 0)
            remaining_treasures -= 1
            client["score"] += 500
            print(f"{client.get("name")} → {client.get("score")} pontos")
            
    if "LEFT" in message:
        if client.get("current_map")[client.get("position")[0]][client.get("position")[1] - 1] == EMPTY:
            move_player(client, 0, -1)
        elif client.get("current_map")[client.get("position")[0]][client.get("position")[1] - 1] == TREASURE:
            move_player(client, 0, -1)
            remaining_treasures -= 1
            client["score"] += 100 
            print(f"{client.get("name")} → {client.get("score")} pontos")
        elif client.get("current_map")[client.get("position")[0]][client.get("position")[1] - 1] == PORTAL:
            move_player_to_portal(client, 0, -1)
            print(f"{client.get("name")} → Entrou no Portal")
            goto_treasure_room(client, client.get("position")[0], client.get("position")[1] - 1)
        elif client.get("current_map")[client.get("position")[0]][client.get("position")[1] - 1] == GREAT_TREASURE:
            move_player(client, 0, -1)
            remaining_treasures -= 1
            client["score"] += 500
            print(f"{client.get("name")} → {client.get("score")} pontos")
        
    if "RIGHT" in message:
        if client.get("current_map")[client.get("position")[0]][client.get("position")[1] + 1] == EMPTY:
            move_player(client, 0, 1)
        elif client.get("current_map")[client.get("position")[0]][client.get("position")[1] + 1] == TREASURE:
            move_player(client, 0, 1)
            remaining_treasures -= 1
            client["score"] += 100
            print(f"{client.get("name")} → {client.get("score")} pontos")
        elif client.get("current_map")[client.get("position")[0]][client.get("position")[1] + 1] == PORTAL:
            move_player_to_portal(client, 0, 1)
            print(f"{client.get("name")} → Entrou no Portal")
            goto_treasure_room(client, client.get("position")[0], client.get("position")[1] + 1)
        elif client.get("current_map")[client.get("position")[0]][client.get("position")[1] + 1] == GREAT_TREASURE:
            move_player(client, 0, 1)
            remaining_treasures -= 1
            client["score"] += 500
            print(f"{client.get("name")} → {client.get("score")} pontos")
        
# Função que move o jogador
def move_player(client, x, y):
    client.get("current_map")[client.get("position")[0]][client.get("position")[1]] = EMPTY
    client["position"][0] += x
    client["position"][1] += y
    client.get("current_map")[client.get("position")[0]][client.get("position")[1]] = PLAYER_1 if client.get("id") == 1 else PLAYER_2


def move_player_to_portal(client, x, y):
    game_main_map[client.get("position")[0]][client.get("position")[1]] = EMPTY
    

# Função que coloca jogador na fila da sala do tesouro
def goto_treasure_room(client, x, y):
    if x == treasure_rooms[0].get("position")[0] and y == treasure_rooms[0].get("position")[1]:
        acquired = treasure_room_semaphores[0].acquire(blocking=False)
        if acquired:
                print(f"{client.get('name')} entrou na sala do tesouro {i + 1}")
                client.update({"position": [1, 1], "current_map": treasure_rooms[0].get("room"), "map_state": "1"})
                treasure_rooms[0].get("room")[1][1] = PLAYER_1 if client.get("id") == 1 else PLAYER_2
                # Iniciar temporizador para expulsar o jogador após 10 segundos
                threading.Thread(target=treasure_room_timer, args=(client, 0)).start()
        else:
            print(f"{client.get('name')} tentou entrar na sala do tesouro {i + 1}, mas está ocupada.")     
    if x == treasure_rooms[1].get("position")[0] and y == treasure_rooms[1].get("position")[1]:
        acquired = treasure_room_semaphores[1].acquire(blocking=False)
        if acquired:
                print(f"{client.get('name')} entrou na sala do tesouro {i + 1}")
                client.update({"position": [1, 1], "current_map": treasure_rooms[1].get("room"), "map_state": "2"})
                treasure_rooms[1].get("room")[1][1] = PLAYER_1 if client.get("id") == 1 else PLAYER_2
                # Iniciar temporizador para expulsar o jogador após 10 segundos
                threading.Thread(target=treasure_room_timer, args=(client, 1)).start()
        else:
            print(f"{client.get('name')} tentou entrar em uma sala do tesouro, mas está ocupada.")    
    print("Client current map: ", client.get("map_state"))
    
# Função de temporizador para saída automática
def treasure_room_timer(client, room_index):
    # Dormir por 10 segundos
    time.sleep(10)
    # Remover jogador da sala do tesouro
    treasure_room_semaphores[room_index].release()  # Liberar a sala
    print(f"{client.get('name')} foi expulso da sala do tesouro {room_index + 1}")
    treasure_rooms[room_index].get("room")[client.get("position")[0]][client.get("position")[1]] = EMPTY
    # Retornar o jogador ao mapa principal
    return_to_main_map(client)

def return_to_main_map(client):
    if game_main_map[1][1] == EMPTY:
        client.update({"position": [1, 1], "current_map": game_main_map, "map_state": "main"})
        game_main_map[1][1] = PLAYER_1 if client.get("id") == 1 else PLAYER_2
    elif game_main_map[2][2] == EMPTY or game_main_map[2][2] == TREASURE:
        if game_main_map[2][2] == EMPTY:
            game_main_map[2][2] = PLAYER_1 if client.get("id") == 1 else PLAYER_2
        else:
            game_main_map[2][2] = PLAYER_1 if client.get("id") == 1 else PLAYER_2
            remaining_treasures -= 1
            client["score"] += 100 
            print(f"{client.get("name")} → {client.get("score")} pontos")
    print(f"{client.get('name')} voltou ao mapa principal.")

# Função que define o vencedor
def set_winner():
    winner = clients[0]
    loser = clients[0]
    
    print("Pontuação final:")
    
    for client in clients:
        print(f"{client.get("name")} → {client.get("score")} pontos")
        
        if client.get("score") > winner.get("score"):
            winner = client
        else:
            loser = client
    if winner.get("score") == loser.get("score"):
        print("Empate!")
        for client in clients:
            client.get("connection").send("DRAW".encode())
            
    print(f"O vencedor é: {winner.get("name")} com {winner.get("score")} pontos")
    winner.get("connection").send(f"WINNER: {str(winner.get("score"))}".encode())
    loser.get("connection").send(f"LOSER: {str(loser.get("score"))}".encode())

# Função que inicia o servidor e trata as conexões durante o jogo
def start_server():
    # Configurações do servidor
    host = '127.0.0.1'
    port = 5000
    
    # Inicializa o socket do servidor 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    print("Servidor iniciado, aguardando conexões...")
    
    # Aguarda a conexão de dois clientes
    while len(clients) < 2:
        conn, addr = server_socket.accept()
        player = {"name": "Player " + str(len(clients) + 1), "id": len(clients) + 1, "connection": conn, "position": [0, 0], "score": 0, "current_map": game_main_map, "map_state": "main"}		
        clients.append(player)
        print("Conectado com:", addr,"\nPlayer:", player.get("name"))
    
    # Inicializa as posições dos jogadores, tesouros e portais
    set_player_position()
    set_treasure_position()
    set_portal_position()
    set_treasure_room_treasures_position()
    
    # Inicia o jogo
    print("Iniciando o jogo...")
    for client in clients:
        client.get("connection").send(f"START:{client.get("id")}".encode())
    
    # Aguarda a confirmação de que o cliente está pronto
    index = 0
    while index < len(clients):
        message = clients[index].get("connection").recv(1024).decode()
        if message == "READY":
            print(f"{clients[index].get("name")} → {message}")
            index += 1
    
    # Espera 2 segundos antes de iniciar o jogo
    time.sleep(2)
    
    # Inicia a thread de monitoramento das requisições
    moviment_thread = threading.Thread(target=monitoring_requests, args=(clients,), daemon=True)
    moviment_thread.start()
    
    while remaining_treasures >= 0:
        game_map_str = json.dumps(game_main_map)
        game_room1_str = json.dumps(treasure_rooms[0].get("room"))
        game_room2_str = json.dumps(treasure_rooms[1].get("room"))
        for client in clients:
            if client.get("map_state") == "main":
                client.get("connection").send(game_map_str.encode())
            elif client.get("map_state") == "1":
                client.get("connection").send(game_room1_str.encode())
            elif client.get("map_state") == "2":
                client.get("connection").send(game_room2_str.encode())
        if remaining_treasures == 0:
            for client in clients:
                client.get("connection").send("GAME_OVER".encode())
            break
        time.sleep(0.5)
        
    # Envia a mensagem de fim de jogo
    print("Jogo finalizado")
        
    print("Processando a pontuação final...")
    
    index = 0
    while index < len(clients):
        message = clients[index].get("connection").recv(1024).decode()
        if message == "POINTS":
            index += 1
            print(index)
        

    # Verifica o vencedor
    print("Verificando o vencedor...")
    set_winner()
    
    while True:
        message = clients[0].get("connection").recv(1024).decode()
        if message == "CLOSE":
            break
    
    # Fechar conexões após o uso
    for client in clients:
        client.get("connection").close()
        
    server_socket.close() # Fecha o socket do servidor

# Função main
if __name__ == "__main__":
    start_server() # Inicia o servidor