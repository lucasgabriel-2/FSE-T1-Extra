from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
import sys
sys.path.append(d)

import socket
import json
from time import sleep

class Cliente:

    def __init__(self, host, porta, arquivo_json, andar):
        self.host = host
        self.porta = porta
        self.arquivo_json = arquivo_json
        self.andar = andar
        # andar = "vagas_primeiro_andar" or andar = "vagas_segundo_andar"
         
        self.cliente_socket =  None
        self.conectaAoServidor()

    def conectaAoServidor(self):
        try:
            # Criar um socket TCP/IP
            self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Conectar-se ao servidor
            self.cliente_socket.connect((self.host, self.porta))

        except Exception as e:
            sleep(1)
            # print("Erro:", e)
            # print("Tentando estabelecer conexão com o servidor...")
            self.cliente_socket.close()
            self.conectaAoServidor()

    def desconectarServidor(self):
        # Fechar a conexão com o servidor
        self.cliente_socket.close()

    def clienteEnviaMensagem(self, mensagem):
        try:
            # Enviar mensagem para o servidor
            self.cliente_socket.sendall(mensagem.encode())

            # Receber resposta do servidor
            received_data = self.cliente_socket.recv(4096).decode()
            # print("Servidor:", received_data)

            if received_data == '':
                # print('Erro ao enviar mensagem para o servidor, tentando novamente...')
                self.cliente_socket.close()
                self.conectaAoServidor()
                sleep(1)
                return self.clienteEnviaMensagem(mensagem)
            
        except Exception as e:
            sleep(1)
            # print("Erro:", e)
            # print("Tentando estabelecer conexão com o servidor...")
            self.cliente_socket.close()
            self.conectaAoServidor()

    def escreveNoJsonEnviaMensagem(self, novo_valor, strig_nome_da_variavel, id, envia):
        #le conteudo do arquivo JSON
        with open(self.arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
        
        if(id == -1):
            # Modifica o valor da variavel desejada
            conteudo_json[strig_nome_da_variavel] = novo_valor
        else:
            conteudo_json[self.andar][id][strig_nome_da_variavel] = novo_valor
        
        # Converte o objeto de volta para JSON
        json_modificado = json.dumps(conteudo_json, indent=2)
        
        # Escreve o JSON modificado de volta no arquivo
        with open(self.arquivo_json, 'w') as arquivo:
            arquivo.write(json_modificado)

        sleep(0.05)
        if envia == True:
            sleep(1)
            self.clienteEnviaMensagem(json_modificado)                   