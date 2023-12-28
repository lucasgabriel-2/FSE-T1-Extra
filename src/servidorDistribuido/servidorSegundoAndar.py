from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
import sys
sys.path.append(d)

from comunicacaoTcpIp.cliente import Cliente
from comunicacaoTcpIp.servidor import Servidor

from comunicacaoGpio.atuador import Atuador
from comunicacaoGpio.sensor import Sensor
import threading
import socket
from time import sleep
import json
from datetime import datetime
import copy

class SegundoAndar:

    def __init__(self):
        # Configura os sensores
        self.instancia_sensor_de_vaga = Sensor(20)
        self.instancia_sensor_passagem_01 = Sensor(16)
        self.instancia_sensor_passagem_02 = Sensor(21)

        # Configura os atuadores
        self.instancia_atuador_endereco_01 = Atuador(13)
        self.instancia_atuador_endereco_02 = Atuador(6)
        self.instancia_atuador_endereco_03 = Atuador(5)
        self.instancia_atuador_sinal_de_lotado_fechado = Atuador(8)

        # Inicia o valor de todas vagas do segundo andar e a contagem de carros 
        self.ocupacao_vagas_segundo_andar = [0,0,0,0,0,0,0,0]
        self.quantidade_de_carros_segundo_andar = 0

        # Controla segundo andar
        self.fecha_estacionamento = False

        # Inicializo um Lock que nao sera usado na pratica (apenas para preecher o parametro da classe servidor)
        self.lock_segundo_andar = threading.Lock()

        # Configurar o servidor distribuido para comunicacao com o central
        arquivo_json = '../comunicacaoJson/jsonComandoSegundoAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
            
        host = conteudo_json["ip_servidor_distribuido_segundo_andar"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_distribuido_segundo_andar"]  # Porta do servidor

        self.instancia_servidor_segundo_andar = Servidor(host, porta, arquivo_json, self.lock_segundo_andar)

        # Configurar o cliente para comunicacao com o central
        arquivo_json = '../comunicacaoJson/jsonSegundoAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
        
        host = conteudo_json["ip_servidor_central"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_central"]  # Porta do servidor
        self.instancia_cliente_segundo_andar = Cliente(host, porta, arquivo_json, "vagas_segundo_andar")
        
        # Inicia o funcionamento do estacionamento
        self.iniciaEstacionamento()
        
    def verificaTodasVagas(self):
        # 00
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[0] = 1
        else:
            self.ocupacao_vagas_segundo_andar[0] = 0

        # 01
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[1] = 1
        else:
            self.ocupacao_vagas_segundo_andar[1] = 0

        # 02
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[2] = 1
        else:
            self.ocupacao_vagas_segundo_andar[2] = 0

        # 03
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[3] = 1
        else:
            self.ocupacao_vagas_segundo_andar[3] = 0

        # 04
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[4] = 1
        else:
            self.ocupacao_vagas_segundo_andar[4] = 0

        # 05
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[5] = 1
        else:
            self.ocupacao_vagas_segundo_andar[5] = 0

        # 06
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[6] = 1
        else:
            self.ocupacao_vagas_segundo_andar[6] = 0

        # 07
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_segundo_andar[7] = 1
        else:
            self.ocupacao_vagas_segundo_andar[7] = 0
        
        return  self.ocupacao_vagas_segundo_andar
    
    def trataEntrada(self):
                
            estado_anterior_vagas = copy.copy(self.ocupacao_vagas_segundo_andar)
                            
            sleep(5) # Aguarda o carro estacionar
            
            estado_atual_vagas = self.verificaTodasVagas()

            vaga_selecionada = -1
            indice = 0
            for vagas in estado_anterior_vagas:
                if ((estado_anterior_vagas[indice] == 0) and (estado_atual_vagas[indice] == 1)):
                    vaga_selecionada = indice
                    break
                indice += 1
            

            data_e_hora_atuais = datetime.now()
            formato = "%d/%m/%Y %H:%M:%S"
            data_e_hora_formatadas = data_e_hora_atuais.strftime(formato)
            self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(data_e_hora_formatadas,"data_hora_entrada", vaga_selecionada, False)

            self.quantidade_de_carros_segundo_andar+=1
            self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_segundo_andar,"quantidade_de_carros_segundo_andar", -1, True)

    def trataSaida(self):
        estado_anterior_vagas = copy.copy(self.ocupacao_vagas_segundo_andar)
        estado_atual_vagas = self.verificaTodasVagas()

        vaga_liberada = -1
        if estado_anterior_vagas != estado_atual_vagas:
            # Verifica qual a vaga que foi liberada
            indice = 0
            for vagas in self.ocupacao_vagas_segundo_andar:
                if ((estado_anterior_vagas[indice] == 1)  and (estado_atual_vagas[indice] == 0)):
                    vaga_liberada = indice
                    break
                indice+=1

        # Dados especificos do carro
        # Data e horario de saida
        data_e_hora_atuais = datetime.now()
        formato = "%d/%m/%Y %H:%M:%S"
        data_e_hora_formatadas = data_e_hora_atuais.strftime(formato)
        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(data_e_hora_formatadas,"data_hora_saida", vaga_liberada, False)

        # Dados gerais estacionamento
        self.quantidade_de_carros_segundo_andar-=1
        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_segundo_andar,"quantidade_de_carros_segundo_andar", -1, False)

        # Envia id vaga do carro que pagara
        vaga_liberada += 1
        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(vaga_liberada,"segundo_andar_id_vaga_carro_a_pagar", -1, True)

        # Reinicia dados relacionados ao carro pagante
        # ... so escreve e nao envia pois ja vai fazer isso la tambem ao contabilizar o pagamento

        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(0,"segundo_andar_id_vaga_carro_a_pagar", -1, False)
        vaga_liberada -= 1
        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem(0,"id_carro_ocupando_vaga", vaga_liberada, False)
        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem("","data_hora_entrada", vaga_liberada, False)
        self.instancia_cliente_segundo_andar.escreveNoJsonEnviaMensagem("","data_hora_saida", vaga_liberada, False)

    def controlaEntradaEsaida(self):

        contador = 0
        while(True):
                self.instancia_atuador_sinal_de_lotado_fechado.desativaAtuador()

                if self.instancia_sensor_passagem_01.detectaEvento():
                    contador+=1
                    if contador%2 != 0:
                        # print("01 aconteceu primeiro")
                        thread_trata_entrada = threading.Thread(target=self.trataEntrada)
                        thread_trata_entrada.start()
                
                if self.instancia_sensor_passagem_02.detectaEvento():
                    contador+=1
                    if contador%2 != 0:
                        # print("02 aconteceu primeiro")
                        thread_trata_saida = threading.Thread(target=self.trataSaida)
                        thread_trata_saida.start()

                if(self.quantidade_de_carros_segundo_andar == 8 or self.fecha_estacionamento):
                    self.instancia_atuador_sinal_de_lotado_fechado.ativaAtuador()
                    # print("Estacionamento fechado/lotado")
                    sleep(2)
                        
    def verificaComandoServidor(self):
        while True:
            with open('../comunicacaoJson/jsonComandoSegundoAndar.json', 'r') as arquivo:
                conteudo_json = json.load(arquivo)
            resposta_fecha_estacionamento = conteudo_json["fechamento_manual_segundo_andar"]
            if resposta_fecha_estacionamento == "False":
                self.fecha_estacionamento = False
            elif resposta_fecha_estacionamento == "True":
                self.fecha_estacionamento = True
            sleep(0.05)

    def iniciaEstacionamento(self):
        thread_controle_entrada_saida = threading.Thread(target=self.controlaEntradaEsaida)
        thread_verifica_comando_servidor = threading.Thread(target=self.verificaComandoServidor)

        thread_controle_entrada_saida.start()
        thread_verifica_comando_servidor.start()
    
SegundoAndar()
                   