# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 21:35:13 2019

@author: Carlos Rana
"""

import requests
import time
import urllib.parse

# =============================================================================
#         FUNCIONES
# =============================================================================

#definimos las funciones que editan la matriz de pesos
def ha_ganado(total,ident_gan,ident_per):
    #desde una id sacamos el nombre de jugador
    nombre_gan = diccionario_id[ident_gan]
    nombre_per = diccionario_id[ident_per]
    
    #desde el nombre de un jugador sacamos su numero (node id)
    numero_gan = diccionario_num[nombre_gan]
    numero_per = diccionario_num[nombre_per]
    
    encontrado = False
    
    if len(total) == 0:
        lista = [numero_gan,numero_per,1]
        total.append(lista)
    else:
        for entrada in total:
            if entrada[0] == ident_gan and entrada[1] == ident_per:
                encontrado = True
                entrada[2] += 1
                break
                
        if encontrado == False:
            lista = [numero_gan,numero_per,1]
            total.append(lista)
            
    return total

def ha_perdido(total,ident_gan,ident_per):
    #desde una id sacamos el nombre de jugador
    nombre_gan = diccionario_id[ident_gan]
    nombre_per = diccionario_id[ident_per]
    
    #desde el nombre de un jugador sacamos su numero (node id)
    numero_gan = diccionario_num[nombre_gan]
    numero_per = diccionario_num[nombre_per]
    
    encontrado = False
    
    if len(total) == 0:
        lista = [numero_gan,numero_per,-1]
        total.append(lista)
    else:
        for entrada in total:
            if entrada[0] == ident_gan and entrada[1] == ident_per:
                encontrado = True
                entrada[2] -= 1
                break
                
        if encontrado == False:
            lista = [numero_gan,numero_per,-1]
            total.append(lista)
            
    return total




# =============================================================================
#         MAIN
# =============================================================================
tiempo_inicial = time.time()
contador = 0

#declaramos la cabecera de las peticiones a la base de datos
cabecera = "https://euw1.api.riotgames.com/lol/"

#IMPORTANTE SI NO NO FUNCIONA
#CAMBIAR LA API KEY POR LA DE LA PAGINA DE LA API DE RIOT
api_key = "?api_key=RGAPI-f4036588-109a-4078-94ee-b1ba3d58e2cc"


#sacamos los challengers de europa
#cambiar cabecera para cambiar de region
#cambiar URL para cambiar de liga
URL = cabecera+"league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"+api_key
response = requests.get(URL)
contador += 1
dicc = response.json()

total = []
jugadores = []
nombres = []
matchs_id = []
diccionario_id = {}

M = len(dicc['entries'])
j = 0

#por cada nombre sacamos su accountId y la almacenamos para iterar sobre ellas
for jugador in dicc['entries']:    
    j += 1
    #parseamos el nombre de usuario para quitar espacios y caracteres raros
    nombre = urllib.parse.quote(jugador['summonerName'])
    
    URL = cabecera+"summoner/v4/summoners/by-name/"+nombre+api_key
    response = requests.get(URL)
    contador += 1
    dicc3 = response.json()
    jugadores.append(dicc3['accountId'])
    nombres.append(nombre)
    diccionario_id[dicc3['accountId']] = nombre

    time.sleep(2)
 

    
print("Datos cargados.")
diccionario_num = {}

i = 1
for nombre in nombres:
    diccionario_num[nombre] = i
    i += 1
    

j = 0
#bucle principal
for jugador in jugadores:
    j += 1
    
    encryptedAccountId = jugador
    
    #sacamos la partida este jugador
    URL2 = cabecera+"match/v4/matchlists/by-account/"+encryptedAccountId+api_key
    response = requests.get(URL2)
    contador += 1
    partidas = response.json()
    
    partidas = partidas['matches']

    for partida in partidas:
        gameId = partida['gameId']
        
        #comprobamos que no se repiten partidas
        if gameId not in matchs_id:
            matchs_id.append(gameId)
            #esperamos para no sobrepasar las consultas posibles en x tiempo
            if contador >= 5:
                contador = 0
                time.sleep(5)
            URL = cabecera+"match/v4/matches/"+str(gameId)+api_key
            response = requests.get(URL)
            contador += 1
            respuesta = response.json() 
            
            participantes = respuesta['participantIdentities'] 
            lista = []

            arriba = False
            #vemos si el jugador a analizar esta en un equipo o en otro
            for jugador2 in participantes:
                if jugador2['player']['currentAccountId'] == encryptedAccountId and jugador2['participantId'] <= 5:
                    arriba = True
                    break
            
            #sacamos cada jugador y actualizamos la matriz de datos
            for jugador2 in participantes:
                if arriba:
                    if jugador2['participantId'] > 5 and jugador2['player']['currentAccountId'] in jugadores:
                        dentro = jugador2['player']
                        lista.append(dentro['currentAccountId'])
                else:
                    if jugador2['participantId'] <= 5 and jugador2['player']['currentAccountId'] in jugadores:
                        dentro = jugador2['player']
                        lista.append(dentro['currentAccountId'])
                        
            equipos = respuesta['teams']

            if equipos[1]['win'] == 'Win':
                for entrada in lista:
                    total = ha_ganado(total,encryptedAccountId,entrada)
            else:
                for entrada in lista:
                    total = ha_perdido(total,encryptedAccountId,entrada)
             
           
 
           

  
#Cambiar booleana si no se quieren escribir datos en un fichero de tipo red social
escribir = True

if escribir:          
    N = len(total)
    f = open("red.gml","w")
    f.write("Autor: Carlos.\n")
    for i in list(range(N)):
        f.write("node\n")
        f.write("[\n")
        f.write("  id "+str(i)+"\n")
        f.write("]\n")
    
    for elemento in total:
        if elemento[2] > 0:
            f.write("edge\n")
            f.write("[\n")
            f.write("  source "+str(elemento[0])+"\n")
            f.write("  target "+str(elemento[1])+"\n")
            f.write("  peso "+str(elemento[2])+"\n")
            f.write("]\n")
        elif elemento[2] < 0:
            f.write("edge\n")
            f.write("[\n")
            f.write("  source "+str(elemento[1])+"\n")
            f.write("  target "+str(elemento[0])+"\n")
            f.write("  peso "+str(-elemento[2])+"\n")
            f.write("]\n")
            
    f.close()
    
    print("Datos escritos en el fichero.")
    
print("Tiempo total de ejecucio:",time.time()-tiempo_inicial)