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

class PrimeiroAndar:

    def __init__(self):
        # Configura os sensores
        self.instancia_sensor_de_vaga = Sensor(18)
        self.instancia_sensor_abertura_cancela_entrada = Sensor(23)
        self.instancia_sensor_fechamento_cancela_entrada = Sensor(24)
        self.instancia_sensor_abertura_cancela_saida = Sensor(25)
        self.instancia_sensor_fechamento_cancela_saida = Sensor(12)

        # Configura os atuadores
        self.instancia_atuador_endereco_01 = Atuador(22)
        self.instancia_atuador_endereco_02 = Atuador(26)
        self.instancia_atuador_endereco_03 = Atuador(19)
        self.instancia_atuador_sinal_de_lotado_fechado = Atuador(27)
        self.instancia_atuador_motor_cancela_entrada = Atuador(10)
        self.instancia_atuador_motor_cancela_saida = Atuador(17)

        # Inicia o valor de todas vagas do primeiro andar e a contagem de carros 
        self.ocupacao_vagas_primeiro_andar = [0,0,0,0,0,0,0,0]
        self.quantidade_de_carros_primeiro_andar = 0
        self.quantidade_de_carros_estacionamento = 0

        # Controla primeiro andar
        self.fecha_estacionamento = False

        # Inicializo um Lock que nao sera usado na pratica (apenas para preecher o parametro da classe servidor)
        self.lock_primeiro_andar = threading.Lock()

        # Configurar o servidor distribuido para comunicacao com o central
        arquivo_json = '../comunicacaoJson/jsonComandoPrimeiroAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
        
        host = conteudo_json["ip_servidor_distribuido_primeiro_andar"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_distribuido_primeiro_andar"]  # Porta do servidor

        self.instancia_servidor_primeiro_andar = Servidor(host, porta, arquivo_json, self.lock_primeiro_andar)

        # Configurar o cliente para comunicacao com o central
        arquivo_json = '../comunicacaoJson/jsonPrimeiroAndar.json'
        with open(arquivo_json, 'r') as arquivo:
            conteudo_json = json.load(arquivo)
        
        host = conteudo_json["ip_servidor_central"]      # Endereço IP do servidor
        porta = conteudo_json["porta_servidor_central"]  # Porta do servidor
        self.instancia_cliente_primeiro_andar = Cliente(host, porta, arquivo_json, "vagas_primeiro_andar")

        # Inicia o funcionamento do estacionamento
        self.iniciaEstacionamento()
        
    def verificaTodasVagas(self):
        # 00
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[0] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[0] = 0

        # 01
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[1] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[1] = 0

        # 02
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[2] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[2] = 0

        # 03
        self.instancia_atuador_endereco_03.desativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[3] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[3] = 0

        # 04
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[4] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[4] = 0

        # 05
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.desativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[5] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[5] = 0

        # 06
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.desativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[6] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[6] = 0

        # 07
        self.instancia_atuador_endereco_03.ativaAtuador()
        self.instancia_atuador_endereco_02.ativaAtuador()
        self.instancia_atuador_endereco_01.ativaAtuador()
        sleep(0.3)
        
        if self.instancia_sensor_de_vaga.verificaEstado():
            self.ocupacao_vagas_primeiro_andar[7] = 1
        else:
            self.ocupacao_vagas_primeiro_andar[7] = 0
        
        return  self.ocupacao_vagas_primeiro_andar

    def controlaEntrada(self):

        contador_id = 0
        while(True):
            if(self.quantidade_de_carros_estacionamento == 16 or self.fecha_estacionamento):
                self.instancia_atuador_sinal_de_lotado_fechado.ativaAtuador()
                while(self.quantidade_de_carros_estacionamento == 16 or self.fecha_estacionamento):
                    # print("Estacionamento fechado/lotado")
                    sleep(2)
                self.instancia_atuador_sinal_de_lotado_fechado.desativaAtuador()                   

            if self.instancia_sensor_abertura_cancela_entrada.detectaEvento():
                self.instancia_atuador_motor_cancela_entrada.ativaAtuador()
                
                while(not(self.instancia_sensor_fechamento_cancela_entrada.detectaEvento())):
                    # print("aguardando passagem do carro pela cancela de entrada ...")
                    sleep(0.3)
                self.instancia_atuador_motor_cancela_entrada.desativaAtuador()
                
                estado_anterior_vagas = copy.copy(self.ocupacao_vagas_primeiro_andar)
                                
                sleep(5) # Aguarda o carro estacionar
                
                estado_atual_vagas = self.verificaTodasVagas()

                vaga_selecionada = -1
                indice = 0
                for vagas in estado_anterior_vagas:
                    if ((estado_anterior_vagas[indice] == 0) and (estado_atual_vagas[indice] == 1)):
                        vaga_selecionada = indice
                        break
                    indice += 1

                # contador_id da um id para o carro que entra no estacionamento comecando de 1
                contador_id+=1
                
                if vaga_selecionada != -1:
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(contador_id,"id_carro_ocupando_vaga", vaga_selecionada, False)

                    data_e_hora_atuais = datetime.now()
                    formato = "%d/%m/%Y %H:%M:%S"
                    data_e_hora_formatadas = data_e_hora_atuais.strftime(formato)
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(data_e_hora_formatadas,"data_hora_entrada", vaga_selecionada, False)

                    self.quantidade_de_carros_primeiro_andar+=1
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_primeiro_andar,"quantidade_de_carros_primeiro_andar", -1, False)

                # else: print("Carro subindo para o segundo andar ...") 

                self.quantidade_de_carros_estacionamento+=1
                self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_estacionamento,"quantidade_de_carros_estacionamento", -1, True)
    
    def controlaSaida(self):
        while(True):
            if self.instancia_sensor_abertura_cancela_saida.detectaEvento():

                self.instancia_atuador_motor_cancela_saida.ativaAtuador()
                while(not(self.instancia_sensor_fechamento_cancela_saida.detectaEvento())):
                    pass
                    # print("aguardando passagem do carro pela cancela de saida ...")

                sleep(0.5)
                self.instancia_atuador_motor_cancela_saida.desativaAtuador()

                estado_anterior_vagas = copy.copy(self.ocupacao_vagas_primeiro_andar)
                estado_atual_vagas = self.verificaTodasVagas()
                vaga_liberada = -1
                if estado_anterior_vagas != estado_atual_vagas:
                    # Verifica se a vaga que foi liberada
                    indice = 0
                    for vagas in self.ocupacao_vagas_primeiro_andar:
                        if ((estado_anterior_vagas[indice] == 1)  and (estado_atual_vagas[indice] == 0)):
                            vaga_liberada = indice
                            break
                        indice+=1

                if vaga_liberada != -1:

                    # Dados especificos do carro
                    # Data e horario de saida
                    data_e_hora_atuais = datetime.now()
                    formato = "%d/%m/%Y %H:%M:%S"
                    data_e_hora_formatadas = data_e_hora_atuais.strftime(formato)
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(data_e_hora_formatadas,"data_hora_saida", vaga_liberada, False)

                    # Dados gerais estacionamento
                    self.quantidade_de_carros_estacionamento-=1
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_estacionamento,"quantidade_de_carros_estacionamento", -1, False)

                    self.quantidade_de_carros_primeiro_andar-=1
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_primeiro_andar,"quantidade_de_carros_primeiro_andar", -1, False)

                    # Envia id vaga do carro que pagara
                    vaga_liberada += 1
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(vaga_liberada,"primeiro_andar_id_vaga_carro_a_pagar",  -1, True)

                    # Reinicia dados relacionados ao carro pagante
                    # ... so escreve e nao envia pois ja vai fazer isso la tambem ao contabilizar o pagamento

                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(0,"primeiro_andar_id_vaga_carro_a_pagar", -1, False)
                    vaga_liberada -= 1
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(0,"id_carro_ocupando_vaga", vaga_liberada, False)
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem("","data_hora_entrada", vaga_liberada, False)
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem("","data_hora_saida", vaga_liberada, False)                
                else: 
                    # print("O carro que está saindo veio do segundo andar")
                    self.quantidade_de_carros_estacionamento-=1
                    self.instancia_cliente_primeiro_andar.escreveNoJsonEnviaMensagem(self.quantidade_de_carros_estacionamento,"quantidade_de_carros_estacionamento", -1, True)

    def verificaComandoServidor(self):
        while True:
            with open('../comunicacaoJson/jsonComandoPrimeiroAndar.json', 'r') as arquivo:
                conteudo_json = json.load(arquivo)
            resposta_fecha_estacionamento = conteudo_json["fechamento_manual_primeiro_andar"]
            if resposta_fecha_estacionamento == "False":
                self.fecha_estacionamento = False
            elif resposta_fecha_estacionamento == "True":
                self.fecha_estacionamento = True
            sleep(0.05)

    def iniciaEstacionamento(self):
        thread_controle_entrada = threading.Thread(target=self.controlaEntrada)
        thread_controle_saida = threading.Thread(target=self.controlaSaida)
        thread_verifica_comando_servidor = threading.Thread(target=self.verificaComandoServidor)

        thread_controle_entrada.start()
        thread_controle_saida.start()
        thread_verifica_comando_servidor.start()
    
PrimeiroAndar()
                   