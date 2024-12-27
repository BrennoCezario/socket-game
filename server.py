# Bibliotecas necessárias
import socket

# Lista que armazena os clientes conectados
clients = []

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
        player = {"name": "Player " + str(len(clients) + 1), "id": len(clients) + 1, "connection": conn}	
        clients.append(player)
        print("Conectado com:", addr,"\nPlayer:", player)
    
    print("Iniciando o jogo...")
    
    # Fechar conexões após o uso
    for client in clients:
        client.get("connection").close()

# Função main
if __name__ == "__main__":
    start_server()