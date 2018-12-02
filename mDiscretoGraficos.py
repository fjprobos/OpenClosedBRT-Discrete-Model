__author__ = 'Pancho'
import xlsxwriter


def crearExcelRed(red, nombre):
    '''
    Excel con la informacion de la red entregada. Se asume que esta la informacion respecto a distintos valores de f.
    Muestra:
    1) Costos Agregados (con porcentajes respecto a total)
    2) Costos por Macrozona
    3) Carga de los vehiculos
    4) Tamano de vehiculo
    5) Histograma de tiempos
    6) Costos por persona transportada
    7) Capacidad de buses
    8) Flota optima
    9) Espaciamiento paraderos optimo
    10) ASK, RPK y FO
    11) Transferencias totales y por persona
    Obs: Estos indicadores se muestran para distintos valores de f.

    :param red: Esta es la red a analizar y para la cual se creara el excel
    :return:no retorna nada, solo crea un archivo excel con toda la info de esta red.
    '''
    #Paramostrar los costos podemos ocupar el esquema que tenemos para el Excel respecto a distintas n, pero respecto a los distintos f.
    #Como no es un solo f, podemos ir mostrando los distintos valores que ocupa el solver para el vector f. Le asignamos un id a cada par f-red.

    #Partimos rescatando de la red de input, toda la informacion necesaria.
    varIndependiente = [[]]
    CostoTotal = [[]]
    CostoOperacion = [[]]
    TViaje = [[]]
    TAcceso = [[]]
    TEspera = [[]]
    TTransferencia = [[]]
    DTransferencia = [[]]
    QTransferencia = [[]]
    CTransSinDelta = [[]]
    CTransConDelta = [[]]
    fPromedio = [[]]
    fPorDist = [[]]
    FOPromedio = [[]]
    flota = [[]]
    KPromedio = [[]]
    KOciosaTotal = [[]]
    sCorredor =[[]]
    sCarretera =[[]]
    sPeriferia = [[]]
    vComercial = [[]]
    infoCargaL1 = [[]]
    mzL1 = [[]]
    mzL2 = [[]]
    TparadaFijo = [[]]
    TparadaVariable = [[]]
    TMovimiento = [[]]
    largoViajePromedio = [[]]
    ASKTotal = [[]]
    RPKTotal = [[]]

    for i in range(1, red.iteracion):
        varIndependiente[0].append(i)
        CostoTotal[0].append(red.resultadosPorFrecuencia[i].CostoTotal)
        CostoOperacion[0].append(red.resultadosPorFrecuencia[i].CostoOperacionTotal)
        TViaje[0].append(red.resultadosPorFrecuencia[i].CostoTotaltViaje)
        TAcceso[0].append(red.resultadosPorFrecuencia[i].CostoTotaltAcceso)
        TEspera[0].append(red.resultadosPorFrecuencia[i].CostoTotaltEspera)
        TTransferencia[0].append(red.resultadosPorFrecuencia[i].CostoTotaltTransferencia)
        DTransferencia[0].append(red.resultadosPorFrecuencia[i].demandaIndirecta)
        QTransferencia[0].append(red.resultadosPorFrecuencia[i].Transferencias)
        CTransSinDelta[0].append(red.resultadosPorFrecuencia[i].TotaltTransferencia)
        CTransConDelta[0].append(red.resultadosPorFrecuencia[i].TotaltTransferenciaSinDelta)
        fPromedio[0].append(red.resultadosPorFrecuencia[i].frecuenciaPromedio)
        fPorDist[0].append(red.resultadosPorFrecuencia[i].frecPorDistancia)
        FOPromedio[0].append(red.resultadosPorFrecuencia[i].FOPromedio)
        flota[0].append(red.resultadosPorFrecuencia[i].FlotaTotal)
        KPromedio[0].append(red.resultadosPorFrecuencia[i].CapacidadPromedio)
        KOciosaTotal[0].append(red.resultadosPorFrecuencia[i].CapacidadOciosaTotal)
        sCorredor[0].append(red.resultadosPorFrecuencia[i].spacingCorredor)
        sCarretera[0].append(red.resultadosPorFrecuencia[i].spacingCarretera)
        sPeriferia[0].append(red.resultadosPorFrecuencia[i].spacingPeriferia)
        vComercial[0].append(red.resultadosPorFrecuencia[i].vComercialPromedio)
        infoCargaL1[0].append(red.resultadosPorFrecuencia[i].lineas[1].infoCarga["ida"])
        mzL1[0].append(red.resultadosPorFrecuencia[i].lineas[1].arcos['ida'])
        mzL2[0].append(red.resultadosPorFrecuencia[i].lineas[1].arcos['vuelta'])
        TparadaFijo[0].append(red.resultadosPorFrecuencia[i].TotaltParadaFijo)
        TparadaVariable[0].append(red.resultadosPorFrecuencia[i].TotaltParadaVariable)
        TMovimiento[0].append(red.resultadosPorFrecuencia[i].TotaltMovimiento)
        largoViajePromedio[0].append(red.resultadosPorFrecuencia[i].largoViajePromedio)
        ASKTotal[0].append((red.resultadosPorFrecuencia[i].ASKTotal))
        RPKTotal[0].append((red.resultadosPorFrecuencia[i].RPKTotal))

    #Creamos un workbook para contener las salidas a graficar
    redtipo = red.tipoRed
    n = str(len(red.lineas))
    wb = xlsxwriter.Workbook("Red"+redtipo+'n'+n+nombre+'.xlsx')
    #Dentro de ese workbook, habra un worksheet para cada grafico o set de graficos.
    wsMain = wb.add_worksheet('Main')
    wsTE   = wb.add_worksheet('TE y TT')
    wsCT   = wb.add_worksheet('CT y CO')
    wsTV   = wb.add_worksheet('TV y TA')
    wsTrans = wb.add_worksheet('Trans')
    wsFKB = wb.add_worksheet('Frec y K')
    wsInfoC = wb.add_worksheet('InfoC')
    wsCLineas = wb.add_worksheet('CompLineas')

    #Creamos tambien los charts que se pegaran en sus respectivas hojas
    #Creamos los charts en el workbook
    chartMain = wb.add_chart({'type': 'line'})
    chartTE = wb.add_chart({'type': 'line'})
    chartCT = wb.add_chart({'type': 'line'})
    chartTV = wb.add_chart({'type': 'line'})
    charttrans1 = wb.add_chart({'type': 'line'})
    charttrans2 = wb.add_chart({'type': 'line'})
    chartfrecLineas = wb.add_chart({'type': 'column'})
    chartVelCom = wb.add_chart({'type': 'column'})
    chartK = wb.add_chart({'type': 'column'})
    chartFlota = wb.add_chart({'type': 'column'})
    chartFO = wb.add_chart({'type': 'column'})

    #En cada sheet crearemos una tabla con los resultados para cada una de las redes que se compararan

    nombresRedes = ('Abierta', 'Cerrada')
    tipoLineas = ('solid', 'dash_dot')
    nRedes = 1
    largo = red.iteracion
    for k in range(nRedes):
        #Partimos poniendo el nombre a cada una de las dos columnas
        wsMain.write(0 + k*(largo + 2), 0, "Iteracion")
        wsMain.write(0 + k*(largo + 2), 1, "Costo Total")
        wsMain.write(0 + k*(largo + 2), 2, "Costo Operacion")
        wsMain.write(0 + k*(largo + 2), 3, "Costo Tiempo de Viaje")
        wsMain.write(0 + k*(largo + 2), 4, "Costo Tiempo de Acceso")
        wsMain.write(0 + k*(largo + 2), 5, "Costo Tiempo de Espera")
        wsMain.write(0 + k*(largo + 2), 6, "Costo Tiempo de Transferencia")
        wsTE.write(0 + k*(largo + 2), 0, "Iteracion")
        wsTE.write(0 + k*(largo + 2), 1, "Costo Tiempo de Espera")
        wsTE.write(0 + k*(largo + 2), 2, "Costo Tiempo de Transferencia")
        wsCT.write(0 + k*(largo + 2), 0, "Iteracion")
        wsCT.write(0 + k*(largo + 2), 1, "Costo Total")
        wsCT.write(0 + k*(largo + 2), 2, "Costo de Operacion")
        wsTV.write(0 + k*(largo + 2), 0, "Iteracion")
        wsTV.write(0 + k*(largo + 2), 1, "Costo Tiempo de Viaje")
        wsTV.write(0 + k*(largo + 2), 2, "Costo Tiempo de Acceso")
        wsTrans.write(0 + k*(largo + 2), 0, "Iteracion")
        wsTrans.write(0 + k*(largo + 2), 1, "Demanda que transfiere")
        wsTrans.write(0 + k*(largo + 2), 2, "Cantidad de transferencias")
        wsTrans.write(0 + k*(largo + 2), 3, "Costo Trans sin penalizacion")
        wsTrans.write(0 + k*(largo + 2), 4, "Costo Trans con penalizacion")
        wsFKB.write(0 + k*(largo + 2), 0, "Iteracion")
        wsFKB.write(0 + k*(largo + 2), 1, "Frecuencia Promedio")
        wsFKB.write(0 + k*(largo + 2), 2, "Frecuencia por Distancia")
        wsFKB.write(0 + k*(largo + 2), 3, "FO Promedio")
        wsFKB.write(0 + k*(largo + 2), 4, "Flota Total")
        wsFKB.write(0 + k*(largo + 2), 5, "Capacidad Promedio")
        wsFKB.write(0 + k*(largo + 2), 6, "Capacidad Ociosa Total")
        wsFKB.write(0 + k*(largo + 2), 7, "Spacing Carretera")
        wsFKB.write(0 + k*(largo + 2), 8, "Spacing Corredor")
        wsFKB.write(0 + k*(largo + 2), 9, "Spacing Periferia")
        wsFKB.write(0 + k*(largo + 2), 10, "Velocidad Comercial Promedio")
        wsFKB.write(0 + k*(largo + 2), 11, "Total Tiempo de Parada Fijo")
        wsFKB.write(0 + k*(largo + 2), 12, "Total Tiempo de Parada Variable")
        wsFKB.write(0 + k*(largo + 2), 13, "Total Tiempo en Movimiento")
        wsFKB.write(0 + k*(largo + 2), 14, "Largo de Viaje Promedio")
        wsFKB.write(0 + k*(largo + 2), 15, "ASK Total")
        wsFKB.write(0 + k*(largo + 2), 16, "RPK Total")
        wsCLineas.write(0 + k*(largo + 2), 0, "Linea")
        wsCLineas.write(0 + k*(largo + 2), 1, "Frecuencia")
        wsCLineas.write(0 + k*(largo + 2), 2, "Velocidad Comercial")
        wsCLineas.write(0 + k*(largo + 2), 3, "Tamano Vehiculo")
        wsCLineas.write(0 + k*(largo + 2), 4, "Flota")
        wsCLineas.write(0 + k*(largo + 2), 5, "ASK")
        wsCLineas.write(0 + k*(largo + 2), 6, "RPK")
        wsCLineas.write(0 + k*(largo + 2), 7, "Factor de Ocupacion")

        #Ahora comenzamos a pegar los resultados en ambas columnas
        for i in range(largo - 1):
            wsMain.write(i + 1 + k*(largo + 2), 0, varIndependiente[k][i])
            wsMain.write(i + 1 + k*(largo + 2), 1, CostoTotal[k][i])
            wsMain.write(i + 1 + k*(largo + 2), 2, CostoOperacion[k][i])
            wsMain.write(i + 1 + k*(largo + 2), 3, TViaje[k][i])
            wsMain.write(i + 1 + k*(largo + 2), 4, TAcceso[k][i])
            wsMain.write(i + 1 + k*(largo + 2), 5, TEspera[k][i])
            wsMain.write(i + 1 + k*(largo + 2), 6, TTransferencia[k][i])
            wsTE.write(i + 1 + k*(largo + 2), 0, varIndependiente[k][i])
            wsTE.write(i + 1 + k*(largo + 2), 1, TEspera[k][i])
            wsTE.write(i + 1 + k*(largo + 2), 2, TTransferencia[k][i])
            wsCT.write(i + 1 + k*(largo + 2), 0, varIndependiente[k][i])
            wsCT.write(i + 1 + k*(largo + 2), 1, CostoTotal[k][i])
            wsCT.write(i + 1 + k*(largo + 2), 2, CostoOperacion[k][i])
            wsTV.write(i + 1 + k*(largo + 2), 0, varIndependiente[k][i])
            wsTV.write(i + 1 + k*(largo + 2), 1, TViaje[k][i])
            wsTV.write(i + 1 + k*(largo + 2), 2, TAcceso[k][i])
            wsTrans.write(i + 1 + k*(largo + 2), 0, varIndependiente[k][i])
            wsTrans.write(i + 1 + k*(largo + 2), 1, DTransferencia[k][i])
            wsTrans.write(i + 1 + k*(largo + 2), 2, QTransferencia[k][i])
            wsTrans.write(i + 1 + k*(largo + 2), 3, CTransSinDelta[k][i])
            wsTrans.write(i + 1 + k*(largo + 2), 4, CTransConDelta[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 0, varIndependiente[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 1, fPromedio[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 2, fPorDist[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 3, FOPromedio[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 4, flota[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 5, KPromedio[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 6, KOciosaTotal[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 7, sCarretera[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 8, sCorredor[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 9, sPeriferia[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 10, vComercial[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 11, TparadaFijo[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 12, TparadaVariable[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 13, TMovimiento[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 14, largoViajePromedio[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 15, ASKTotal[k][i])
            wsFKB.write(i + 1 + k*(largo + 2), 16, RPKTotal[k][i])

        #Y los resultados de Infocarga y lineas
        nlineas = len(red.resultadosPorFrecuencia[red.iteracion-1].lineas)#Numero de lineas de la ultima red de esta ciudad
        lineas = red.resultadosPorFrecuencia[red.iteracion-1].lineas
        largoCiclo = 0
        #Primero los encabezados
        for l in lineas:
            wsInfoC.write(0 + largoCiclo, 0, "Linea"+str(lineas[l].linea))
            wsInfoC.write(0 + largoCiclo, 1, "f"+str(lineas[l].linea))
            wsInfoC.write(1 + largoCiclo, 1, "vComercial"+str(lineas[l].linea))
            wsInfoC.write(2 + largoCiclo, 1, "K"+str(lineas[l].linea))
            wsInfoC.write(3 + largoCiclo, 1, "B"+str(lineas[l].linea))
            wsInfoC.write(4 + largoCiclo, 1, "ASK"+str(lineas[l].linea))
            wsInfoC.write(5 + largoCiclo, 1, "RPK"+str(lineas[l].linea))
            wsInfoC.write(6 + largoCiclo, 1, "FO"+str(lineas[l].linea))
            wsInfoC.write(7 + largoCiclo, 1, "Perfil IDA")
            wsInfoC.write(8 + largoCiclo, 1, "Carga")
            wsInfoC.write(9 + largoCiclo, 1, "Subidas")
            wsInfoC.write(10 + largoCiclo, 1, "Bajadas")
            wsInfoC.write(11 + largoCiclo, 1, "Ocupacion")
            wsInfoC.write(12 + largoCiclo, 1, "Perfil Vuelta")
            wsInfoC.write(13 + largoCiclo, 1, "Carga")
            wsInfoC.write(14 + largoCiclo, 1, "Subidas")
            wsInfoC.write(15 + largoCiclo, 1, "Bajadas")
            wsInfoC.write(16 + largoCiclo, 1, "Ocupacion")

            #Luego los datos
            wsInfoC.write(0 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].f)
            wsInfoC.write(1 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].velocidadComercial)
            wsInfoC.write(2 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].cargaMaxima)
            wsInfoC.write(3 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].flota)
            wsInfoC.write(4 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].ASK)
            wsInfoC.write(5 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].RPK)
            wsInfoC.write(6 + largoCiclo, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].FOPromedio)
            wsCLineas.write(1 + l, 0, 'Linea '+str(red.resultadosPorFrecuencia[largo-1].lineas[l].linea))
            wsCLineas.write(1 + l, 1, red.resultadosPorFrecuencia[largo - 1].lineas[l].f)
            wsCLineas.write(1 + l, 2, red.resultadosPorFrecuencia[largo - 1].lineas[l].velocidadComercial)
            wsCLineas.write(1 + l, 3, red.resultadosPorFrecuencia[largo - 1].lineas[l].cargaMaxima)
            wsCLineas.write(1 + l, 4, red.resultadosPorFrecuencia[largo - 1].lineas[l].flota)
            wsCLineas.write(1 + l, 5, red.resultadosPorFrecuencia[largo - 1].lineas[l].ASK)
            wsCLineas.write(1 + l, 6, red.resultadosPorFrecuencia[largo - 1].lineas[l].RPK)
            wsCLineas.write(1 + l, 7, red.resultadosPorFrecuencia[largo - 1].lineas[l].FOPromedio)


            #Se agrega la informacion de cada nodo de carga por sentido, desde el primero al ultimo.
            #Primero el sentido IDA
            #Seteamos el ancho de la linea en terminos de arcos
            anchoIda = len(red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].arcos['ida'])

            for j in range(anchoIda):
                id = red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].arcos['ida'][j].origen
                wsInfoC.write(7 + largoCiclo, 2 + j, id)
                wsInfoC.write(8 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][0][id])
                wsInfoC.write(9 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][1][id])
                wsInfoC.write(10 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][2][id])
                wsInfoC.write(11 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][3][id])
            #Por ultimo incluimos la informacion de carga del ultimo nodo del sentido
            id = red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].arcos['ida'][-1].destino
            wsInfoC.write(7 + largoCiclo, 2 + anchoIda, id)
            wsInfoC.write(8 + largoCiclo, 2 + anchoIda, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][0][id])
            wsInfoC.write(9 + largoCiclo, 2 + anchoIda, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][1][id])
            wsInfoC.write(10 + largoCiclo, 2 + anchoIda, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][2][id])
            wsInfoC.write(11 + largoCiclo, 2 + anchoIda, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['ida'][3][id])

            anchoVuelta = len(red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].arcos['vuelta'])
            for j in range(anchoVuelta):
                id = red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].arcos['vuelta'][j].origen
                wsInfoC.write(12 + largoCiclo, 2 + j, id)
                wsInfoC.write(13 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][0][id])
                wsInfoC.write(14 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][1][id])
                wsInfoC.write(15 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][2][id])
                wsInfoC.write(16 + largoCiclo, 2 + j, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][3][id])
            #Tambien incluimos aca el ultimo nodo del sentido
            id = red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].arcos['vuelta'][-1].destino
            wsInfoC.write(12 + largoCiclo, 2 + anchoVuelta, id)
            wsInfoC.write(13 + largoCiclo, 2 + anchoVuelta, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][0][id])
            wsInfoC.write(14 + largoCiclo, 2 + anchoVuelta, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][1][id])
            wsInfoC.write(15 + largoCiclo, 2 + anchoVuelta, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][2][id])
            wsInfoC.write(16 + largoCiclo, 2 + anchoVuelta, red.resultadosPorFrecuencia[red.iteracion-1].lineas[l].infoCarga['vuelta'][3][id])

            #Aumentamos en 1 los anchos para que graficos consideren los valores del ultimo nodo
            anchoIda +=1
            anchoVuelta +=1

            #Creamos un chart por sentido para ir viendo la carga de la linea

            chartCargaIda = wb.add_chart({'type': 'line'})
            chartCargaIda.add_series({
            'categories': ['InfoC', 7 + largoCiclo, 2, 7 + largoCiclo, 2 + anchoIda],
            'values':     ['InfoC', 8 + largoCiclo, 2, 8 + largoCiclo, 2 + anchoIda],
            'line':       {'color': 'red'},
            'name': 'Carga'
            })

            chartCargaIda.add_series({
            'categories': ['InfoC', 7 + largoCiclo, 2, 7 + largoCiclo, 2 + anchoIda],
            'values':     ['InfoC', 9 + largoCiclo, 2, 9 + largoCiclo, 2 + anchoIda],
            'line':       {'color': 'green'},
            'name': 'Subidas'
            })

            chartCargaIda.add_series({
            'categories': ['InfoC', 7 + largoCiclo, 2, 7 + largoCiclo, 2 + anchoIda],
            'values':     ['InfoC', 10 + largoCiclo, 2, 10 + largoCiclo, 2 + anchoIda],
            'line':       {'color': 'blue'},
            'name': 'Bajadas'
            })

            chartCargaVuelta = wb.add_chart({'type': 'line'})
            chartCargaVuelta.add_series({
            'categories': ['InfoC', 12 + largoCiclo, 2, 12 + largoCiclo, 2 + anchoVuelta],
            'values':     ['InfoC', 13 + largoCiclo, 2, 13 + largoCiclo, 2 + anchoVuelta],
            'line':       {'color': 'red'},
            'name': 'Carga'
            })

            chartCargaVuelta.add_series({
            'categories': ['InfoC', 12 + largoCiclo, 2, 12 + largoCiclo, 2 + anchoVuelta],
            'values':     ['InfoC', 14 + largoCiclo, 2, 14 + largoCiclo, 2 + anchoVuelta],
            'line':       {'color': 'green'},
            'name': 'Subidas'
            })

            chartCargaVuelta.add_series({
            'categories': ['InfoC', 12 + largoCiclo, 2, 12 + largoCiclo, 2 + anchoVuelta],
            'values':     ['InfoC', 15 + largoCiclo, 2, 15 + largoCiclo, 2 + anchoVuelta],
            'line':       {'color': 'blue'},
            'name': 'Bajadas'
            })

            wsInfoC.insert_chart(largoCiclo, 3 + max(anchoIda, anchoVuelta), chartCargaIda)
            wsInfoC.insert_chart(largoCiclo, 11 + max(anchoIda, anchoVuelta), chartCargaVuelta)

            largoCiclo += 19



        #Le agregamos los datos a los charts normales
        #                                [sheetname, first_row, first_col, last_row, last_col]
        chartMain.add_series({
            'categories':'=Main!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Main!$B$'+str(2+k*(largo+2))+':$B$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'red'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Costo Total '+nombresRedes[k]
        })
        chartMain.add_series({
            'categories':'=Main!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Main!$C$'+str(2+k*(largo+2))+':$C$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'lime'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Costo Operacion '+nombresRedes[k]
        })
        chartMain.add_series({
            'categories':'=Main!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Main!$D$'+str(2+k*(largo+2))+':$D$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'green'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Viaje '+nombresRedes[k]
        })
        chartMain.add_series({
            'categories':'=Main!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Main!$E$'+str(2+k*(largo+2))+':$E$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'purple'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Acceso '+nombresRedes[k]
        })
        chartMain.add_series({
            'categories':'=Main!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Main!$F$'+str(2+k*(largo+2))+':$F$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'orange'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Espera '+nombresRedes[k]
        })
        chartMain.add_series({
            'categories':'=Main!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Main!$G$'+str(2+k*(largo+2))+':$G$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'navy'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Transferencia '+nombresRedes[k]
        })
        chartTE.add_series({
            'categories':'=TE y TT!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=TE y TT!$B$'+str(2+k*(largo+2))+':$B$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'orange'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Espera '+nombresRedes[k]
        })
        chartTE.add_series({
            'categories':'=TE y TT!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=TE y TT!$C$'+str(2+k*(largo+2))+':$C$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'navy'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Transferencia '+nombresRedes[k]

        })
        chartCT.add_series({
            'categories':'=CT y CO!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=CT y CO!$B$'+str(2+k*(largo+2))+':$B$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'orange'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Costo Total '+nombresRedes[k]
        })
        chartCT.add_series({
            'categories':'=CT y CO!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=CT y CO!$C$'+str(2+k*(largo+2))+':$C$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'navy'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Costo de Operacion '+nombresRedes[k]
        })
        chartTV.add_series({
            'categories':'=TV y TA!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=TV y TA!$B$'+str(2+k*(largo+2))+':$B$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'orange'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Viaje '+nombresRedes[k]
        })
        chartTV.add_series({
            'categories':'=TV y TA!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=TV y TA!$C$'+str(2+k*(largo+2))+':$C$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'navy'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tiempo de Acceso '+nombresRedes[k]
        })
        charttrans1.add_series({
            'categories':'=Trans!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Trans!$B$'+str(2+k*(largo+2))+':$B$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'orange'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Demanda que transfiere '+nombresRedes[k]
        })
        charttrans1.add_series({
            'categories':'=Trans!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Trans!$C$'+str(2+k*(largo+2))+':$C$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'navy'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Cantidad de Transferencias '+nombresRedes[k]
        })
        charttrans2.add_series({
            'categories':'=Trans!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Trans!$D$'+str(2+k*(largo+2))+':$D$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'orange'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Transferencias sin Delta '+nombresRedes[k]
        })
        charttrans2.add_series({
            'categories':'=Trans!$A$'+str(2+k*(largo+2))+':$A$'+str(1+(k+1)*largo+2*k),
            'values':    '=Trans!$E$'+str(2+k*(largo+2))+':$E$'+str(1+(k+1)*largo+2*k),
            'line':       {'color': 'navy'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Transferencias con Delta '+nombresRedes[k]
        })
        chartfrecLineas.add_series({
            'categories':'=CompLineas!$A$2:$A$'+str(nlineas + 1),
            'values':    '=CompLineas!$B$2:$B$'+str(nlineas + 1),
            'line':       {'color': 'red'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Frecuencias'
        })
        chartVelCom.add_series({
            'categories':'=CompLineas!$A$2:$A$'+str(nlineas + 1),
            'values':    '=CompLineas!$C$2:$C$'+str(nlineas + 1),
            'line':       {'color': 'red'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Velocidad Comercial'
        })
        chartK.add_series({
            'categories':'=CompLineas!$A$2:$A$'+str(nlineas + 1),
            'values':    '=CompLineas!$D$2:$D$'+str(nlineas + 1),
            'line':       {'color': 'red'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Tamano Vehiculo'
        })
        chartFlota.add_series({
            'categories':'=CompLineas!$A$2:$A$'+str(nlineas + 1),
            'values':    '=CompLineas!$E$2:$E$'+str(nlineas + 1),
            'line':       {'color': 'red'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Flota'
        })
        chartFO.add_series({
            'categories':'=CompLineas!$A$2:$A$'+str(nlineas + 1),
            'values':    '=CompLineas!$H$2:$H$'+str(nlineas + 1),
            'line':       {'color': 'red'},
            'line':   {'dash_type': tipoLineas[k]},
            'name':'Factor de Ocupacion'
        })

    #Finalmente insertamos el chart en la sheet donde queremos
    wsMain.insert_chart('I5', chartMain)
    wsTE.insert_chart('F5', chartTE)
    wsCT.insert_chart('F5', chartCT)
    wsTV.insert_chart('F5', chartTV)
    wsTrans.insert_chart('H5', charttrans1)
    wsTrans.insert_chart('H12', charttrans2)
    wsCLineas.insert_chart('J2', chartfrecLineas)
    wsCLineas.insert_chart('J18', chartVelCom)
    wsCLineas.insert_chart('R2', chartK)
    wsCLineas.insert_chart('R18', chartFlota)
    wsCLineas.insert_chart('J33', chartFO)

    wb.close()
