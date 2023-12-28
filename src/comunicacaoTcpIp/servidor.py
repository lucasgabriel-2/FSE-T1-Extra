from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
import sys
sys.path.append(d)

import os
import json
import socket
import threading
from threading import Lock
from time import sleep

class Servidor:
    def __init__(self, host, porta, arquivo_json, lock_andar):
        
        self.host = host
        self.porta = porta
        self.arquivo_json = arquivo_json
        self.lock = lock_andar
        
        # Criar um socket TCP/IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Vincular o socket ao endereço e porta
        self.server_socket.bind((self.host, self.porta))

        # Aguardar conexoes
        self.server_socket.listen(5)  # Permitir ate 5 conexões pendentes

        # print(f"Aguardando conexões em {self.host}:{self.porta}")

        # Thread para inicar o servidor
        thread_inicia_servidor = threading.Thread(target=self.iniciaServidor)
        thread_inicia_servidor.start()

    def iniciaServidor(self):

        while True:
            # Aceitar a conexao do cliente
            cliente_socket, endereco = self.server_socket.accept()

            # Iniciar uma nova thread para lidar com a conexao do cliente
            thread_comunicao_cliente = threading.Thread(target=self.comunicaoCliente, args=(cliente_socket, endereco))
            thread_comunicao_cliente.start()

    # Funcao para lidar com a conexao de um cliente
    def comunicaoCliente(self, cliente_socket, endereco):
        # print(f"Conexão de {endereco}")

        while True:
            try:
                # Receber dados do cliente
                dados_recebidos = cliente_socket.recv(4096).decode()
                if not dados_recebidos:
                    break
                
                # print(f"Cliente {endereco}: {dados_recebidos}")

                # Enviar resposta para o cliente
                resposta = {"mensagem": "Recebido: " + dados_recebidos}
                resposta_json = json.dumps(resposta)
                cliente_socket.sendall(resposta_json.encode())
                
                self.salvarMensagem(self.arquivo_json, dados_recebidos)

            except Exception as e:
                # print(f"Erro na conexão com {endereco}: {e}")
                break

        # Fechar a conexao com o cliente
        cliente_socket.close()
        # print(f"Conexão com {endereco} fechada")

    def salvarMensagem(self, arquivo_json, mensagem):
        
        self.lock.acquire()
        with open(arquivo_json, 'w') as arquivo:
        # Apagar todo o conteúdo do arquivo
            arquivo.write('')

        # Salvar a nova mensagem no arquivo
            arquivo.write(mensagem)
        self.lock.release()
        sleep(0.05)
        
    def encerraServidor(self):
        # print("Encerrando o servidor...")
        self.server_socket.close()