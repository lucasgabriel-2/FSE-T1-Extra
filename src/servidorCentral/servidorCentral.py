from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
import sys
sys.path.append(d)

from comunicacaoTcpIp.servidor import Servidor
from comunicacaoTcpIp.cliente import Cliente

from datetime import datetime
from time import sleep
import json
import socket
import threading
import os

class ServidorCentral:
    def __init__(self):

        # Inicializo os locks
        self.lock_primeiro_andar = threading.Lock()
        self.lock_segundo_andar = threading.Lock()

        # Configurar o servidor central de comunicação com o primeiro andar
        arquivo_json = '../comunicacaoJson/jsonCentralPrimeiroAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
        
        host = conteudo_json["ip_servidor_central"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_central"]  # Porta do servidor

        self.instancia_servidor_central_primeiro_andar = Servidor(host, porta, arquivo_json, self.lock_primeiro_andar)
               
        # Configurar o servidor central de comunicação com o segundo andar
        arquivo_json = '../comunicacaoJson/jsonCentralSegundoAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
        
        host = conteudo_json["ip_servidor_central"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_central"]  # Porta do servidor

        self.instancia_servidor_central_segundo_andar = Servidor(host, porta, arquivo_json, self.lock_segundo_andar)

        # Configura o cliente para comunicacao com o primeiro andar
        arquivo_json = '../comunicacaoJson/jsonComandoCentralPrimeiroAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)

        host = conteudo_json["ip_servidor_distribuido_primeiro_andar"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_distribuido_primeiro_andar"]  # Porta do servidor

        self.instancia_cliente_primeiro_andar = Cliente(host, porta, arquivo_json, "vagas_primeiro_andar")

        # Configura o cliente para comunicacao com o segundo andar
        arquivo_json = '../comunicacaoJson/jsonComandoCentralSegundoAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)

        host = conteudo_json["ip_servidor_distribuido_segundo_andar"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_distribuido_segundo_andar"]  # Porta do servidor

        self.instancia_cliente_segundo_andar = Cliente(host, porta, arquivo_json, "vagas_segundo_andar")

        # Variaveis do menu
        self.numero_total_de_carros_estacionamento = 0
        self.numero_carros_primeiro_andar = 0
        self.numero_vagas_disponiveis_primeiro_andar = 0

        self.fecha_estacionamento = False

        self.numero_carros_segundo_andar = 0
        self.numero_vagas_disponiveis_segundo_andar = 0

        self.bloqueia_segundo_andar = False

        self.valor_total_pago_em_centavos = 0
        self.taxa_por_minuto = 15

        # Thread para apresentar o menu
        thread_menu = threading.Thread(target=self.menu)

        # Thread para atualizar informacoes
        thread_atualiza_informacoes_primeiro_andar = threading.Thread(target=self.atualizaInformacoesPrimeiroAndar)

        # Thread para atualizar informacoes
        thread_atualiza_informacoes_segundo_andar = threading.Thread(target=self.atualizaInformacoesSegundoAndar)

        thread_menu.start()
        thread_atualiza_informacoes_primeiro_andar.start()
        thread_atualiza_informacoes_segundo_andar.start()

    def atualizaInformacoesPrimeiroAndar(self):
        while True:
            self.lock_primeiro_andar.acquire()
            with open('../comunicacaoJson/jsonCentralPrimeiroAndar.json', 'r') as arquivo:
                conteudo_json = json.load(arquivo)

            self.numero_total_de_carros_estacionamento = conteudo_json["quantidade_de_carros_estacionamento"]
            self.numero_carros_primeiro_andar = conteudo_json["quantidade_de_carros_primeiro_andar"]
            self.numero_vagas_disponiveis_primeiro_andar = (8 - self.numero_carros_primeiro_andar)
            
            # le informacoes do carro pagante e calcula nova receita
            primeiro_andar_pagante_id_vaga = conteudo_json["primeiro_andar_id_vaga_carro_a_pagar"]
            if primeiro_andar_pagante_id_vaga != 0:
                primeiro_andar_pagante_id_carro = conteudo_json["vagas_primeiro_andar"][primeiro_andar_pagante_id_vaga-1]["id_carro_ocupando_vaga"]
                primeiro_andar_pagante_hora_entrada = conteudo_json["vagas_primeiro_andar"][primeiro_andar_pagante_id_vaga-1]["data_hora_entrada"]
                primeiro_andar_pagante_hora_saida = conteudo_json["vagas_primeiro_andar"][primeiro_andar_pagante_id_vaga-1]["data_hora_saida"]
                
                formato = "%d/%m/%Y %H:%M:%S"
                data_e_hora_fim = datetime.strptime(primeiro_andar_pagante_hora_saida, formato)
                data_e_hora_inicio = datetime.strptime(primeiro_andar_pagante_hora_entrada, formato)

                diferenca_entrada_saida = data_e_hora_fim - data_e_hora_inicio
                diferenca_em_minutos = diferenca_entrada_saida.total_seconds() / 60
                self.valor_total_pago_em_centavos += diferenca_em_minutos*self.taxa_por_minuto

                # Reinicio o valor da vaga, pois o carro saiu e o estacionamento ja foi cobrado
                conteudo_json["primeiro_andar_id_vaga_carro_a_pagar"] = 0
                conteudo_json["vagas_primeiro_andar"][primeiro_andar_pagante_id_vaga-1]["id_carro_ocupando_vaga"] = 0
                conteudo_json["vagas_primeiro_andar"][primeiro_andar_pagante_id_vaga-1]["data_hora_entrada"] = ""
                conteudo_json["vagas_primeiro_andar"][primeiro_andar_pagante_id_vaga-1]["data_hora_saida"] = ""
                
                # Converte o objeto de volta para JSON
                json_modificado = json.dumps(conteudo_json, indent=2)
                
                # Escreve o JSON modificado de volta no arquivo
                with open('../comunicacaoJson/jsonCentralPrimeiroAndar.json', 'w') as arquivo:
                    arquivo.write(json_modificado)
            self.lock_primeiro_andar.release()
            sleep(0.05)

    def atualizaInformacoesSegundoAndar(self):
        while True:
            self.lock_segundo_andar.acquire()
            with open('../comunicacaoJson/jsonCentralSegundoAndar.json', 'r') as arquivo:
                conteudo_json = json.load(arquivo)
            
            self.numero_carros_segundo_andar = conteudo_json["quantidade_de_carros_segundo_andar"]
            self.numero_vagas_disponiveis_segundo_andar = (8 - self.numero_carros_segundo_andar)
            
            # le informacoes do carro pagante e calcula nova receita
            segundo_andar_pagante_id_vaga = conteudo_json["segundo_andar_id_vaga_carro_a_pagar"]
            if segundo_andar_pagante_id_vaga != 0:
                segundo_andar_pagante_id_carro = conteudo_json["vagas_segundo_andar"][segundo_andar_pagante_id_vaga-1]["id_carro_ocupando_vaga"]
                segundo_andar_pagante_hora_entrada = conteudo_json["vagas_segundo_andar"][segundo_andar_pagante_id_vaga-1]["data_hora_entrada"]
                segundo_andar_pagante_hora_saida = conteudo_json["vagas_segundo_andar"][segundo_andar_pagante_id_vaga-1]["data_hora_saida"]
                
                formato = "%d/%m/%Y %H:%M:%S"
                data_e_hora_fim = datetime.strptime(segundo_andar_pagante_hora_saida, formato)
                data_e_hora_inicio = datetime.strptime(segundo_andar_pagante_hora_entrada, formato)

                diferenca_entrada_saida = data_e_hora_fim - data_e_hora_inicio
                diferenca_em_minutos = diferenca_entrada_saida.total_seconds() / 60
                self.valor_total_pago_em_centavos += diferenca_em_minutos*self.taxa_por_minuto

                # Reinicio o valor da vaga, pois o carro saiu e o estacionamento ja foi cobrado
                conteudo_json["segundo_andar_id_vaga_carro_a_pagar"] = 0
                conteudo_json["vagas_segundo_andar"][segundo_andar_pagante_id_vaga-1]["id_carro_ocupando_vaga"] = 0
                conteudo_json["vagas_segundo_andar"][segundo_andar_pagante_id_vaga-1]["data_hora_entrada"] = ""
                conteudo_json["vagas_segundo_andar"][segundo_andar_pagante_id_vaga-1]["data_hora_saida"] = ""
                
                # Converte o objeto de volta para JSON
                json_modificado = json.dumps(conteudo_json, indent=2)
                
                # Escreve o JSON modificado de volta no arquivo
                with open('../comunicacaoJson/jsonCentralSegundoAndar.json', 'w') as arquivo:
                    arquivo.write(json_modificado)
            self.lock_segundo_andar.release()
            sleep(0.05)

    def limpar_terminal(self):
        os.system('clear')
        
    def menu(self):

        while(True):
            self.limpar_terminal()
            print("--------------------CONTROLE DO ESTACIONAMENTO-------------------")
            print("Selecione uma das opcoes:")
            print("1 - Ver informacoes do estacionamento")
            print("2 - Fechar o estacionamento")
            print("3 - Abrir o estacionamento")
            print("4 - Bloquear o segundo andar")
            print("5 - Desbloquear o segundo andar")
            print("-----------------------------------------------------------------")
            opcao = input()
            if(opcao == "1"):
                self.verInformaceosEstacionamento()
            if(opcao == "2"):
                self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem("True", "fechamento_manual_primeiro_andar", -1, True)
            if(opcao == "3"):
                self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem("False", "fechamento_manual_primeiro_andar", -1, True)
            if(opcao == "4"):
                self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem("True", "fechamento_manual_segundo_andar", -1, True)
            if(opcao == "5"):
                self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem("False", "fechamento_manual_segundo_andar", -1, True)
                

    def verInformaceosEstacionamento(self):
        opcao = "1"
        while opcao != "0":
            self.limpar_terminal()
            print("------------------INFORMACOES DO ESTACIONAMENTO------------------")
            print(f"Numero total de carros no estacionamento: {self.numero_total_de_carros_estacionamento}")
            print()

            print(f"Numero de carros no primeiro andar: {self.numero_carros_primeiro_andar}")
            print(f"Numero de vagas disponiveis no primeiro andar: {self.numero_vagas_disponiveis_primeiro_andar}")
            print()

            print(f"Numero de carros no segundo andar: {self.numero_carros_segundo_andar}")
            print(f"Numero de vagas disponiveis no segundo andar: {self.numero_vagas_disponiveis_segundo_andar}")
            print()
            print(f"Valor total pago: {(self.valor_total_pago_em_centavos/100.0)}")
            print("-----------------------------------------------------------------")
            print()
            print()
            print("Digite 0 para voltar ao menu principal ou digite 1 para atualizar os dados")
            opcao = input()

ServidorCentral()