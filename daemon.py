#!/usr/bin/env python
import socket
import subprocess
import math
import sys
import thread

TCP_IP = "127.0.0.1"
if len(sys.argv) < 2:
  print "e necessario passar a porta"
else:
  TCP_PORT = int(sys.argv[1])

BUFFER_SIZE = 4000  # Normally 1024, but we want fast response

def Desmonta_Pacote(Pacote):
        Version = Pacote[0:4]
        IHL = Pacote[4:8]
        TOS = Pacote[8:16]
        Total_Length = Pacote[16:32]
        ID = Pacote[32:48]
        Flags = Pacote[48:51]
        Fragment_Offset = Pacote[51:64]

		TTL = Pacote[64:72]
        Protocol = Pacote[72:80]
        Header_Checksum = Pacote[80:96]
        Source_Address = Pacote[96:128]
        Destination_Address = Pacote[128:160]
        Options = Pacote[160:]
        return Protocol, TTL

def Montar_Pacote(Comando, aux):
        Version = '0010'
        IHL = '0101'
        TOS = '00000000'
        Total_Length = '0000000000000000'
        ID = '0000000000000000'
        Flags = '111'
        Fragment_Offset = '0000000000000'
        TTL = bin(int(aux, 2)-1) [2:].rjust(8, '0')
        Protocol = '00000000'
        Header_Checksum = '0000000000000000'

        aux = TCP_IP.split(".")

		for i in range(len(aux)):
                aux[i] = (bin(int(aux[i]))) [2:].rjust(8, '0')

        Source_Address = ''.join(aux)
        Destination_Address = ''.join(aux)

        Data = Converte_bin(Executa_comando(int(Comando,2)))

        tamanho = len(Version + IHL + TOS + Total_Length + ID + Flags + Fragment_Offset + TTL + Protocol + Header_Checksum \
            + Source_Address + Destination_Address + Data)

        numero_words_32_bits = int(math.ceil(float(tamanho) / 32.0))
        Total_Length = ''.join(bin(numero_words_32_bits * 32)) [2:].rjust(16, '0')

        Pacote = (Version + IHL + TOS + Total_Length + ID  + Flags + Fragment_Offset + TTL + Protocol + Header_Checksum \
            + Source_Address + Destination_Address + Data)

        return Pacote


def Executa_comando(Comando):
        if(Comando == 1):
                return subprocess.check_output(['ps'])
        elif(Comando == 2):
                return subprocess.check_output(['df'])
        elif(Comando == 3):
                return subprocess.check_output(['finger'])
        else:
                return subprocess.check_output(['uptime'])


def Converte_bin(Data):
        vetor = (map(bin, bytearray(Data)))

        for x in range(len(vetor)):
                vetor[x] = vetor[x] [2:].rjust(8, '0')

        vetor = ''.join(vetor)

        return vetor
        
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


def Thread_funcao(conn):
        data = conn.recv(BUFFER_SIZE)
        if data:
            comando, TTL_aux = Desmonta_Pacote(data)
            pacote = Montar_Pacote(comando, TTL_aux)
            print "received data"
            conn.send(pacote)  # echo

        conn.close()


while 1:
        conn, addr = s.accept()
        print 'Connection address:', addr

        thread.start_new_thread(Thread_funcao, (conn,))

