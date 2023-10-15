import socket
import threading

def handle_client(client_socket):
    request = client_socket.recv(8)
    version, nmethods, *methods = request
    client_socket.sendall(b'\x05\x00')  # Мы не поддерживаем аутентификацию

    request = client_socket.recv(4)
    version, cmd, _, addr_type = request

    if cmd == 1 and addr_type == 1:  # Запрос на подключение к серверу
        target_address = client_socket.recv(4)  # IPv4 адрес
        target_port = client_socket.recv(2)  # Порт

        target_host = socket.inet_ntoa(target_address)
        target_port = int.from_bytes(target_port, byteorder='big')

        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((target_host, target_port))

        client_socket.sendall(b'\x05\x00\x00\x01' + target_address + target_port.to_bytes(2, byteorder='big'))

        def forward(src, dst):
            while True:
                data = src.recv(4096)
                if len(data) == 0:
                    break
                dst.send(data)

        client_to_remote = threading.Thread(target=forward, args=(client_socket, remote_socket))
        remote_to_client = threading.Thread(target=forward, args=(remote_socket, client_socket))

        client_to_remote.start()
        remote_to_client.start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 8888))
    server.listen(5)

    print("SOCKS5 прокси-сервер слушает на порту 8888...")

    while True:
        client_socket, addr = server.accept()
        print(f"Принято подключение от {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()