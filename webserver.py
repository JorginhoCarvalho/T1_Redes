#!/usr/bin/env python

import cgi
import cgitb
import socket
import math
import string

cgitb.enable()

TCP_IP = "127.0.0.1"
BUFFER_SIZE = 4000

def Recebe_Parametros(Parametros_lista):
  num_maq = 9 * [0]
  comando = 10 * [0]
  i = 0
  for parametros in Parametros_lista:
         if(parametros[:3] == "maq"):
                  num_maq[i] = parametros[3]
                  comando[i] = parametros[5:]

                  i = i+1
  return num_maq, comando, len(Parametros_lista) -1

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
  data_aux = Pacote[160:]
  data = int(len(data_aux)/8) * [0]

  for i in range(int(len(data_aux)/8)):
    data[i] = data_aux [:8]
    data_aux = data_aux [8:]

  for i in range(len(data)):
    data[i] = chr(int(data[i], 2))


  data = ''.join(data)

  return data, Flags

def Monta_Pacote(Comando):
  Version = '0010'
  IHL = '0000'
  Total_Length = '0000000000000000'
  TOS = '00000000'
  ID = '0000000000000000'
  Flags = '000'
  Fragment_Offset = '0000000000000'
  TTL = '00001000'
  Protocol = ''.join(bin(int(Comando)) [2:]).rjust(8, '0')
  Header_Checksum = '0000000000000000'

  aux = TCP_IP.split(".")

  for i in range(len(aux)):
    aux[i] = (bin(int(aux[i]))) [2:].rjust(8, '0')

  Source_Address = ''.join(aux)
  Destination_Address = ''.join(aux)
  Option = '00000000000000000000000000000000'

  tamanho = len(Version + IHL + TOS + Total_Length + ID + Flags + Fragment_Offset + TTL + Protocol + Header_Checksum \
    + Source_Address + Destination_Address + Option)

  number = int(math.ceil(float(tamanho) / 32.0))
  Total_Length = ''.join(bin(number * 32)) [2:].rjust(16, '0')

  IHL = ''.join(bin(number)) [2:].rjust(4, '0')

  Pacote = (Version + IHL + TOS + Total_Length + ID  + Flags + Fragment_Offset + TTL + Protocol + Header_Checksum \
    + Source_Address + Destination_Address + Option).ljust(number * 32, '0')

  return Pacote

def Executa_comando(Comando):
  if(Comando == 'ps'):
    return '1'
  elif(Comando == 'df'):
    return '2'
  elif(Comando == 'finger'):
    return '3'
  else:
    return '4'

def Seleciona_Porta(N_maq):
  return 8000 + int(N_maq)

print ("Content-Type: text/html;charset=utf-8\r\n\r\n")
print "<pre>"
parametros_lista = cgi.FieldStorage()
N_maquina, Comando, N_Comandos= Recebe_Parametros(parametros_lista)


for i in range(0, N_Comandos):

  TCP_PORT = Seleciona_Porta(N_maquina[i])
  if(N_maquina[i] == '1'):
    print "Maquina 1"
  elif(N_maquina[i] == '2'):
    print "Maquina 2"
  else:
    print "Maquina 3"
  Comando[i] = Executa_comando(Comando[i])
  Pacote = Monta_Pacote(Comando[i])
  try:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(Pacote)

    while True:
      Pacote = s.recv(BUFFER_SIZE)

      if not Pacote:
        break
      else:
        data, flags = Desmonta_Pacote(Pacote)
        print data
  finally:
    s.close()

print "</pre>"
                                                                                    
