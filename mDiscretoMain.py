__author__ = 'Pancho'


#Primero se maneja la info de input, fijada aco u obtenida de las bases de datos.
#Para eso habra que importar la libreria que permite conectarse a PostgreSQL

import psycopg2
import psycopg2.extras
import sys
import pprint
from mDiscretoClases import*
from mDiscretoFunciones import*
from mDiscretoGraficos import*

nivelRiqueza = (0.5, 2)
nivelDelta = (0, 0.5, 1.5, 2, 3)

for g in range(0, 1):

    redes = {}#Diccinario que contiene a las tres redes. "abierta", "cerrada" y "actual".
    parametros = {}#Parametros guardados con key que indican su nombre con un string

    #####--------PARAMETROS-------#######
    parametros['ad'] = 182.4
    parametros['bd'] = 2.28
    parametros['at'] = 4189.115
    parametros['bt'] = 13
    parametros['k'] = 0.8 #Nueva constante incorporado en octubre
    parametros['tparadaFija'] = 0.00424 #Nuevo tiempo de parada fijo calculado en octubre 2018
    #tmuertop = 0.00166
    #tpp = tmuertop + (Vp)/2*(1/20736.0+1/20736.0)
    #tpc = tmuertop + (Vc)/2*(1/20736.0+1/20736.0)
    parametros['gammaV'] = 1498.0#*nivelRiqueza[g]#Valor obtenido de "Precios Sociales Vigentes 2015" del Ministerio de Desarrollo Social.
    parametros['gammaE'] = parametros['gammaV']*1.570
    parametros['gammaA'] = parametros['gammaV']*2.185
    parametros['lambdaCorredor'] = 750
    parametros['lambdaPeriferia'] = 400
    parametros['lambdaCarretera'] = 676/16.0 #Este valor viene de total de pax eod2013 relacionados a carretera dividido por largo carretera.
    #lambdap = 400.0 Se utilizan para calcular el spacing!!!!
    #lambdac = 750.0
    #lambdaCBD = 1900.0
    parametros['Va'] = 4.5
    parametros['tsp'] = 0.001123
    parametros['tbp'] = 0.0006555
    parametros['tsc'] = 0.0004861
    parametros['delta'] = 0.09766*nivelDelta[g]




    #####--------CONEXION-------#######
    #Define our connection string
    conn_string = "host='localhost' dbname='lineas' user='Pancho'"
    # print the connection string we will use to connect
    print "Connecting to database\n	->%s" % (conn_string)
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    ##Este es un cursor normal, pero mejor utilicemos una de diccionario cursor = conn.cursor()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print "Connected!\n"


    #Creamos las redes
    redes['cerrada'] = red(parametros, cursor, "cerrada")
    redes['abierta'] = red(parametros, cursor, "abierta")
    redes['actual'] = red(parametros, cursor, "actual")

    conn.close()

    for r in redes.values():
        #####--------ASIGNACION INICIAL-------#######
        asignarViajesLineas(r)
        asignarCarga(r)#Se actualiza con las frecuencias
        calcularSpacing(r)#Se actualiza con las frecuencias
        tiempoParadaLineas(r)#Se actualiza con las frecuencias
        calcularCostosPersonas(r)
        calcularCostoOperacion(r)#Se actualiza con las frecuencias
        r.calcularIndicadoresIniciales()#Setea los indicadores para obtener valores en la primera iteracion.

        #####--------OPTIMIZACION-------#######
        optimiScipy(r)
        crearExcelRed(r, r.tipoRed+"Base"+str(g))

print 'Fin'

#TODO arreglar perfiles de carga de la red actual y ver porque esta dando cargas negativas en algunos casos.
#TODO Imprimir largo de viaje promedio para cada iteracion