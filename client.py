# Bibliotecas necessárias
import socket

# Constantes que indicam os ícones do mapa
WALL = " # "
EMPTY = "   "
TREASURE = " ♦ "
PLAYER_1 = " ♞ "
PLAYER_2 = " ♘ "

# Mapa principal do jogo
game_main_map = [
    [WALL] * 8,
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL] * 8,
]

# Função que inicia e trata a conexão socket do cliente
def start_client():
    
    host = '127.0.0.1'
    port = 5000
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("Conectado ao servidor")
       

# Função main 
if __name__ == "__main__":
    start_client()