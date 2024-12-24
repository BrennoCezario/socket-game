import socket

clients = []

def start_server():
    host = '127.0.0.1'
    port = 5000
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    print("Servidor iniciado, aguardando conexões...")
    
    while len(clients) < 2:
        conn, addr = server_socket.accept()
        clients.append(conn)
        print("Conectado com:", addr)
    
    print("Iniciando o jogo...")
    
    # Fechar conexões após o uso
    for client in clients:
        client.close()

if __name__ == "__main__":
    start_server()