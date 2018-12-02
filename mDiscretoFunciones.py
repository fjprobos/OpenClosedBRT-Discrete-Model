__author__ = 'Pancho'

from scipy.optimize import minimize
from math import*

def calcularTiempoEspera(od, k, delta, red):
    '''
    Calcula los tiempos de espera iniciales y en transferencia para un od dado.
    :param od: od a intervenir
    :param k: constante de tiempo de espera
    :param delta: penalidad por transferencia
    :return:
    '''

    for nlineas in range(len(od.lineas)):
        if not od.lineas[nlineas] == None:
            frecuenciaTotal = 0
            for l in od.lineas[nlineas]:
                frecuenciaTotal += float(l[0].f)
            od.tEspera[nlineas] = float(k)/frecuenciaTotal
            od.tEsperaSinDelta[nlineas] = float(k)/frecuenciaTotal
            if nlineas > 0:
                od.tEspera[nlineas] += delta
    od.TotaltEspera = od.tEspera[0]*od.demanda
    od.TotaltTransferencia = (od.tEspera[1] + od.tEspera[2])*od.demanda
    od.TotaltTransferenciaSinDelta = (od.tEsperaSinDelta[1] + od.tEsperaSinDelta[2])*od.demanda
    od.TotalNTransferencias = od.nTransferencias*od.demanda

    #Finalmente agregamos los resultados a nivel de red
    red.TotaltEspera += od.TotaltEspera
    red.TotaltTransferencia += od.TotaltTransferencia
    red.TotaltTransferenciaSinDelta += od.TotaltTransferenciaSinDelta
    red.Transferencias += od.TotalNTransferencias

def calcularTiempoViaje(od, tparadaf, red):
    '''
    Calcula el tiempo de viaje que considera tiempo en movimiento y tiempo por paradas (IVT) para el od en cuestion.
    :param od:
    :return:
    '''

    #Primero definimos variables que guarden valores por porcion del viaje
    tViajeMovimiento = []
    tParadaFijo = []
    tParadaVariable = []
    distancia = [] #Indica la distancia promedio para el od

    #Luego variables que guarden el promedio para el od
    tvmPromedio = 0
    tvparadasPromedio = 0
    tpfPromedio = 0
    tpvPromedio = 0
    distanciaPromedio = 0

    #Obtenemos todos los arcos de todas las rutas por seccion
    rutaArcos = calcularArcosRutaAsignada(od)

    if od.origen.id == 75 and od.destino.id == 36:
        print "este es"

    #Sumamos tiempos fijos de la ruta, obteniendose un promedio por seccion
    for seccion in rutaArcos:
        if not seccion == None:
            sumaFrecuencias = 0
            tvmFrec = 0
            tpfFrec = 0
            distFrec = 0
            for ruta in seccion:
                sumaFrecuencias += ruta[1]
                tvm = 0
                tpf = 0
                dist = 0
                for a in ruta[0]:
                    tvm += (a.largo)/(a.velocidad)
                    tpf += a.largo/a.spacing*tparadaf
                    dist += a.largo
                tvmFrec += tvm*ruta[1]
                tpfFrec += tpf*ruta[1]
                distFrec += dist*ruta[1]
            tViajeMovimiento.append(tvmFrec/sumaFrecuencias)
            tParadaFijo.append(tpfFrec/sumaFrecuencias)
            distancia.append(distFrec/sumaFrecuencias)

            tvmPromedio += tvmFrec/sumaFrecuencias
            tvparadasPromedio += tpfFrec/sumaFrecuencias
            tpfPromedio += tpfFrec/sumaFrecuencias
            distanciaPromedio += distFrec/sumaFrecuencias

    #Ahora incluimos el tiempo de parada variable
    tpVariable = calcularTiempoParadaVariable(od)
    for i in tpVariable:
        if not i == None:

            tpvPromedio += i
            tvparadasPromedio += i


    #Ahora asignamos los tiempos calculados al od
    od.tViajeMovimiento = tvmPromedio
    od.tViajeParadas = tvparadasPromedio
    od.tViajeTotal = tvparadasPromedio + tvmPromedio
    od.tParadaFijo = tpfPromedio
    od.tParadaVariable = tpvPromedio
    od.distancia = distanciaPromedio

    od.TotaltMovimiento = od.tViajeMovimiento*od.demanda
    od.TotaltParada = od.tViajeParadas*od.demanda
    od.TotaltViaje = od.tViajeTotal*od.demanda
    od.TotaltParadaFijo = od.tParadaFijo*od.demanda
    od.TotaltParadaVariable = od.tParadaVariable*od.demanda
    od.TotalDistancia = od.distancia*od.demanda

    #Finalmente agregamos a nivel de red
    red.TotaltMovimiento += od.TotaltMovimiento
    red.TotaltParada += od.TotaltParada
    red.TotaltViaje += od.TotaltViaje
    red.TotaltParadaFijo += od.TotaltParadaFijo
    red.TotaltParadaVariable += od.TotaltParadaVariable
    red.largoViajeTotal += od.TotalDistancia

def calcularTiempoAcceso(od, Va, red):
    '''
    Como se tiene el acceso desde nodo de acceso de la BD, aca solo se agrega el del spacing. Luego los OD se suman para la red.
    :param od:
    :return:
    '''
    #Primero identificamos los arcos iniciales y finales del od para obtener sus respectivos spacing.
    arcoInicial = od.rutaArcos[0]
    arcoFinal = od.rutaArcos[-1]

    spacingAcceso = arcoInicial.spacing
    spacingEgreso = arcoFinal.spacing

    #Luego agregamos al tiempo de acceso que ya se tiene por acceso perpedicular, la porcion por spacing.
    od.tAccesoSpacing = (spacingAcceso + spacingEgreso)/(Va*4.0)
    od.TotaltAcceso = od.TotaltAccesoPerpendicular + od.tAccesoSpacing*od.demanda

    #Finalmente agregamos al nivel de red
    red.TotaltAcceso += od.TotaltAcceso

def calcularTiempoParadaVariable(od):
    '''
    Calcula el tiempo de viaje debido a las paradas para el od en cuestion.
    Asume que ya se calculo el tParadaVariable para las lineas.
    :return:
    '''
    #Lista con los tiempos promedios por porcion del viaje
    tPorcion = [None, None, None]
    for p in range(len(od.lineas)): #Este for recorre las porciones de viaje
        tPorcion.append(0)##Le agregamos un cero a la porcion del viaje
        sumaTiempos = 0
        sumaFrecuencias = 0
        #Buscamos las lineas de la porcion
        lineas = od.lineas[p]

        #En caso que la porcion no tenga lineas, no tiene sentido seguir.
        if lineas == None:
            break

        #Tambien buscamos los nodos de inicio y termino de la porcion en que estemos
        if p == 0:
            if od.lineas[1] == None:
                nodoInic = od.origen
                nodoFin = od.destino
            else:
                nodoInic = od.origen
                nodoFin = od.nodosTransferencia[p]
        elif p == 1:
            if od.lineas[2] == None:
                nodoInic = od.nodosTransferencia[0]
                nodoFin = od.destino
            else:
                nodoInic = od.nodosTransferencia[0]
                nodoFin = od.nodosTransferencia[p]
        elif p == 2:
            nodoInic = od.nodosTransferencia[1]
            nodoFin = od.destino

        #Ahora comenzamos a recorrer cada una de las lineas de la seccion para sumar sus tiempos de parada variable
        #ponderados por sus respectivas frecuencias

        for l in lineas:
            #Primero evaluamos el caso en que la porcion comience y termine en el mismo sentido de la linea
            if l[1] == l[2]:
                #En ese caso sumamos los tiempos variables con un for que recorre desde el origen hasta el fin
                #segun el orden que ellos tienen en la lista de nodos de la linea
                origen = l[0].diccionarioNodos[l[1]][nodoInic.id] #Lugar en la lista de la linea que ocupa el nodo de origen
                destino = l[0].diccionarioNodos[l[1]][nodoFin.id] #Lugar en la lista de la linea que ocupa el nodo de destino
                for n in range(origen, destino + 1):
                    sumaTiempos += l[0].tparadaVariable[l[1]][l[0].nodos[l[1]][n].id]*l[0].f
                #Luego de que se sumaron todos los tiempos ponderados por frec.
                #  es necesairo incluir la frec sola en la suma de frecuencias
                sumaFrecuencias += l[0].f
            else:
                #En el caso que el sentido de subida no sea el mismo al de bajada, tendremos que sumar un sentido hasta
                #el final, y luego el otro desde el inicio hasta el nodo final
                origen = l[0].diccionarioNodos[l[1]][nodoInic.id] #Lugar en la lista de la linea que ocupa el nodo de origen
                destino = l[0].diccionarioNodos[l[2]][nodoFin.id] #Lugar en la lista de la linea que ocupa el nodo de destino
                for n in range(origen, len(l[0].nodos[l[1]])):
                    sumaTiempos += l[0].tparadaVariable[l[1]][l[0].nodos[l[1]][n].id]*l[0].f
                for n in range(destino):
                    sumaTiempos += l[0].tparadaVariable[l[2]][l[0].nodos[l[2]][n].id]*l[0].f
                #Luego sumamos frecuencias
                sumaFrecuencias += l[0].f

        #Finalmente obtenemos el tiempo variable de parada promedio de la porcion
        tPorcion[p] = sumaTiempos/sumaFrecuencias

    return tPorcion

def calcularSpacing(red):
    '''
    Misma funcion que en el modelo continuo.
    Version en base a Modificacion Spacing del cuaderno amarillo.
    Se consideran algunos calculos distintos si es red cerrada o abierta (actual ocupa formulas de abierta).
    Tambien se consideran distintos spacing en periferia, corredor o carretera.
    :param tp:
    :param gammaV:
    :param gammaA:
    :param lambdaa:
    :param largo:
    :param at:
    :param bt:
    :param Va:
    :param lineas:
    :param esCorredor:
    :return:
    '''
    ###Partimos calculando los parametros necesarios para el calculo del spacing, segun formula del cuaderno.

    #Parametros comunes
    tparadaFijo = red.parametros['tparadaFija']
    gammaV = red.parametros['gammaV']
    gammaA = red.parametros['gammaA']
    at = red.parametros['at']
    bt = red.parametros['bt']
    Va = red.parametros['Va']
    lineas = red.lineas

    #Parametros comunes por red pero distintos por tipo de arco
    lambdaCorredor = red.parametros['lambdaCorredor']
    lambdaPeriferia = red.parametros['lambdaPeriferia']
    lambdaCarretera = red.parametros['lambdaCarretera']

    #Parametros disntintos por red  tipo de arco
    fCarretera = 0
    fCorredor = 0
    fPeriferia = 0
    KCorredor = 0
    KPeriferia = 0
    KCarretera = 0
    QCorredor = 0
    QCarretera = 0
    QPeriferia = 0

    if red.tipoRed == 'abierta' or red.tipoRed == 'actual':
        #Primero asignamos parametros de carretera, en este caso tenemos que encontral el numero de la linea para la red.
        if red.tipoRed == 'abierta':
            fCarretera = lineas[3].f
            KCarretera = lineas[3].cargaMaxima
            QCarretera = lineas[3].cargaPromedio
        else:
            fCarretera = lineas[20].f
            KCarretera = lineas[20].cargaMaxima
            QCarretera = lineas[20].cargaPromedio
        #Luego las del corredor
        sumaCapacidades = 0
        sumaFrecuencias = 0
        sumaCargasPromedio = 0
        for l in lineas:
            sumaFrecuencias += lineas[l].f
            sumaCapacidades += lineas[l].cargaMaxima*lineas[l].f
            sumaCargasPromedio += lineas[l].cargaPromedio*lineas[l].f
        f = sumaFrecuencias/len(lineas)
        #De una suma aritmetica del numero de lineas partido en el numero de lineas, se obtiene un promedio
        #de la frecuencia que se observa en un tramo cualquiera del corredor.
        fCorredor = f*(len(lineas)+1)/2.0
        KCorredor = sumaCapacidades/sumaFrecuencias
        QCorredor = sumaCargasPromedio/sumaFrecuencias

        #Finalmente las de periferia
        sumaCapacidades = 0
        sumaFrecuencias = 0
        sumaCargasPromedio = 0
        for l in lineas:
            sumaFrecuencias += lineas[l].f
            sumaCapacidades += lineas[l].cargaMaxima*lineas[l].f
            sumaCargasPromedio += lineas[l].cargaPromedio*lineas[l].f
        fPeriferia = sumaFrecuencias/len(lineas)
        KPeriferia = sumaCapacidades/sumaFrecuencias
        QPeriferia = sumaCargasPromedio/sumaFrecuencias

    elif red.tipoRed == 'cerrada':
        #Primero asignamos parametros de carretera
        fCarretera = lineas[8].f
        KCarretera = lineas[8].cargaMaxima
        QCarretera = lineas[8].cargaPromedio

        #Luego las del corredor, que eneste caso corresponde a los datos del troncal
        fCorredor = lineas[10].f
        KCorredor = lineas[10].cargaMaxima
        QCorredor = lineas[10].cargaPromedio

        #Finalmente las de periferia
        sumaCapacidades = 0
        sumaFrecuencias = 0
        sumaCargasPromedio = 0
        for l in lineas:
            if not l == 10:
                sumaFrecuencias += lineas[l].f
                sumaCapacidades += lineas[l].cargaMaxima*lineas[l].f
                sumaCargasPromedio += lineas[l].cargaPromedio*lineas[l].f
        fPeriferia = sumaFrecuencias/len(lineas)
        KPeriferia = sumaCapacidades/sumaFrecuencias
        QPeriferia = sumaCargasPromedio/sumaFrecuencias


    red.spacingCarretera = ((fCarretera*tparadaFijo*(at + bt*KCarretera + gammaV*QCarretera))/((gammaA*lambdaCarretera)/(4*Va)))**(0.5)
    red.spacingCorredor = ((fCorredor*tparadaFijo*(at + bt*KCorredor + gammaV*QCorredor))/((gammaA*lambdaCorredor)/(4*Va)))**(0.5)
    red.spacingPeriferia = ((fPeriferia*tparadaFijo*(at + bt*KPeriferia + gammaV*QPeriferia))/((gammaA*lambdaPeriferia)/(4*Va)))**(0.5)

    #Por ultimo asignamos spacing a cada arco segun su tipo de arco
    for a in red.arcos:
        if red.arcos[a].tipo == "urbano poco denso" or (red.arcos[a].tipo == "urbano denso" or red.arcos[a].tipo == "urbano medio"):
            red.arcos[a].spacing = red.spacingPeriferia
        elif red.arcos[a].tipo == "corredor":
            red.arcos[a].spacing = red.spacingCorredor
        elif red.arcos[a].tipo == "carretera":
            red.arcos[a].spacing = red.spacingCarretera

def calcularCostoOperacion(red):
    '''
    Calcula costos por lineas y agrega a nivel de red.
    :param red: objeto de la clase red.
    :return: retorna el costo total de operacion de un sistema definido por una red. Se van calculando los costos de operacion en cada
    una de las lineas y luego se suman.
    '''
    CostoLineas ={} #Diccionario con el costo de cada linea por id
    CostoTotal = 0
    lineas = red.lineas

    for l in lineas:
        #Se multiplica por dos ya que hay que considerar el ida y vuelta.
        costo = (lineas[l].largoTotal*(red.parametros['ad'] + red.parametros['bd']*lineas[l].cargaMaxima))*lineas[l].f + (red.parametros['at'] + red.parametros['bt']*lineas[l].cargaMaxima)*lineas[l].flota
        CostoLineas[lineas[l].linea] = costo
        CostoTotal += costo

    red.CostoOperacionTotal = CostoTotal
    red.CostoOperacionLineas = CostoLineas

    #Tambien recalculamos los costos de operacion promedio
    red.CostoOperacionPromedio = red.CostoOperacionTotal/red.demandaTotal

def calcularCostosPersonas(red):
    '''
    Calcula los costos para las personas a nivel de od y agrega a nivel de red.
    OJO-> Debe calcularse luego de: asignarViajesLineas, asignarCarga, calcularSpacing, tiempoParadaLineas
    :param red:
    :return:
    '''

    #Calculamos los valores para cada par od y luego agregamos a los valores agregados a nivel de red.
    for od in red.ods:
        calcularTiempoEspera(red.ods[od], red.parametros['k'], red.parametros['delta'], red)
        calcularTiempoViaje(red.ods[od], red.parametros['tparadaFija'], red)
        calcularTiempoAcceso(red.ods[od], red.parametros['Va'], red)

    #Lo que podemos actualizar a nivel de red lo hacemos.
    red.CostoTotaltMovimiento = red.TotaltMovimiento*red.parametros['gammaV']
    red.CostoTotaltParada = red.TotaltParada*red.parametros['gammaV']
    red.CostoTotaltParadaFijo = red.TotaltParadaFijo*red.parametros['gammaV']
    red.CostoTotaltParadaVariable = red.TotaltParadaVariable*red.parametros['gammaV']
    red.CostoTotaltViaje = red.TotaltViaje*red.parametros['gammaV']
    red.CostoTotaltEspera = red.TotaltEspera*red.parametros['gammaE']
    red.CostoTotaltAcceso = red.TotaltAcceso*red.parametros['gammaA']
    red.CostoTotaltTransferencia = red.TotaltTransferencia*red.parametros['gammaE']
    red.CostoTotaltTransferenciaSinDelta = red.TotaltTransferenciaSinDelta*red.parametros['gammaE']

    #Tambien los promedios a nivel de red
    red.tMovimientoPromedio = red.TotaltMovimiento/red.demandaTotal
    red.tParadaPromedio = red.TotaltParada/red.demandaTotal
    red.tParadaFijoPromedio = red.TotaltParadaFijo/red.demandaTotal
    red.tParadaVariablePromedio =red.TotaltParadaVariable/red.demandaTotal
    red.tViajePromedio = red.TotaltViaje/red.demandaTotal
    red.tEsperaPromedio = red.TotaltEspera/red.demandaTotal
    red.tAccesoPromedio = red.TotaltAcceso/red.demandaTotal
    red.tTransferenciaSinDeltaPromedio = red.TotaltTransferenciaSinDelta/red.demandaTotal
    red.tTransferenciaPromedio = red.TotaltTransferencia/red.demandaTotal
    red.CostoTotaltViajePromedio = red.CostoTotaltViaje/red.demandaTotal
    red.CostoTotaltMovimientoPromedio = red.CostoTotaltMovimiento/red.demandaTotal
    red.CostoTotaltParadaPromedio = red.CostoTotaltParada/red.demandaTotal
    red.CostoTotaltEsperaPromedio = red.CostoTotaltEspera/red.demandaTotal
    red.CostoTotaltAccesoPromedio = red.CostoTotaltAcceso/red.demandaTotal
    red.CostoTotaltTransferenciaPromedio = red.CostoTotaltTransferencia/red.demandaTotal
    red.CostoTotaltTransferenciaSinDeltaPromedio = red.CostoTotaltTransferenciaSinDelta/red.demandaTotal
    red.transferenciasPromedio = red.Transferencias/red.demandaTotal

def resetearCostosRed(red):
    '''
    Setea en 0 los costos de la red. Lo ocupamos antes de recalcular costos al actualizar la frecuencia.
    :param red:
    :return:
    '''

    red.TiemposPersonas = 0
    red.TotaltViaje = 0
    red.TotaltEspera = 0
    red.TotaltAcceso = 0
    red.TotaltTransferencia = 0
    red.TotaltTransferenciaSinDelta = 0
    red.TotaltMovimiento = 0
    red.TotaltParada = 0
    red.TotaltParadaFijo = 0
    red.TotaltParadaVariable = 0
    red.CostoTotaltMovimiento = 0
    red.CostoTotaltParada = 0
    red.CostoTotaltParadaFijo = 0
    red.CostoTotaltParadaVariable = 0
    red.CostoTotaltViaje = 0
    red.CostoTotaltEspera = 0
    red.CostoTotaltAcceso = 0
    red.CostoTotaltTransferencia = 0
    red.CostoTotaltTransferenciaSinDelta = 0
    red.Costos = 0
    red.CostoOperacionLineas = None
    red.CostoOperacionTotal = 0
    red.CostoTotal = 0
    red.tMovimientoPromedio = red.TotaltMovimiento/red.demandaTotal
    red.tParadaPromedio = red.TotaltParada/red.demandaTotal
    red.tParadaFijoPromedio = red.TotaltParadaFijo/red.demandaTotal
    red.tParadaVariablePromedio = red.TotaltParadaVariable/red.demandaTotal
    red.tViajePromedio = red.TotaltViaje/red.demandaTotal
    red.tEsperaPromedio = red.TotaltEspera/red.demandaTotal
    red.tAccesoPromedio = red.TotaltAcceso/red.demandaTotal
    red.tTransferenciaSinDeltaPromedio = red.TotaltTransferenciaSinDelta/red.demandaTotal
    red.tTransferenciaPromedio = red.TotaltTransferencia/red.demandaTotal
    red.CostoTotaltViajePromedio = red.CostoTotaltViaje/red.demandaTotal
    red.CostoTotaltMovimientoPromedio = red.CostoTotaltMovimiento/red.demandaTotal
    red.CostoTotaltParadaPromedio = red.CostoTotaltParada/red.demandaTotal
    red.CostoTotaltEsperaPromedio = red.CostoTotaltEspera/red.demandaTotal
    red.CostoTotaltAccesoPromedio = red.CostoTotaltAcceso/red.demandaTotal
    red.CostoTotaltTransferenciaPromedio = red.CostoTotaltTransferencia/red.demandaTotal
    red.CostoTotaltTransferenciaSinDeltaPromedio = red.CostoTotaltTransferenciaSinDelta/red.demandaTotal
    red.CostoOperacionPromedio = red.CostoOperacionTotal/red.demandaTotal
    red.CostoTotalPromedio = red.CostoTotal/red.demandaTotal
    red.Transferencias = 0


    red.transferenciasPromedio = red.Transferencias/red.demandaTotal
    red.ASKTotal = 0
    red.RPKTotal = 0
    red.FOPromedio = 0 #Factor de ocupacion promedio de los buses de la red.
    red.FlotaTotal = 0
    red.CapacidadPromedio = 0
    red.CapacidadOciosaTotal = 0
    red.frecuenciaPromedio = 0
    red.vComercialPromedio = 0
    red.largoViajePromedio = 0
    red.largoViajeTotal = 0

    #Crearemos un diccionario que ira guardando los indicadores de la red para cada valor de F que se tome. De esta manera podremos graficar cambios respecto a F.
    #Quizas simplemente podemos hacer un clon de la red(aunque eso puede tardar mucho).
    red.frecPorDistancia = 0

def calcularDemandaTotal(red):
    '''

    :param red:
    :return:
    '''
    demanda = 0
    for od in red.ods:
        demanda += red.ods[od].demanda

    return demanda

def asignarArcosLineas(record, arcos):
    '''
    Devuelve un arreglo de arcos a partir de un arreglo de indices que indican el id del arco.
    Se aprovecha de indicar en el arco que la linea pasa por ahi.
    :param record:  Ocupa el record de la fila de la consulta SQL en forma de diccionario.
    :param arcos: Diccionario con todos los arcos de la red.
    :return: Retorna el conjunto de arcos en vez del arreglo de indices. Estan en el orden de inicio a fin.
    '''

    indices = record['arcos']
    arcosSalida = []
    for a in indices:
        arcosSalida.append(arcos[a])
        arcos[a].lineas.append(record['linea'])

    return arcosSalida

def asignarLineasArcos(arcos, lineas):
    '''
    Asigna las lineas reales en vez de los indices a cada arco.
    :param arcos:
    :param lineas:
    :return:
    '''
    for a in arcos:
        lineasAsignar = []
        for l in arcos[a].lineas:
            lineasAsignar.append(lineas[l])
        arcos[a].lineas = lineasAsignar

def asignarArcosNodos(arcos, nodos):
    '''
    Asigna los arcos a las listas de arcos de entrada o salida de cada nodo.
    Ojo, los origenes de los arcos son los oute de los nodos y viceversa.
    :param arcos: conjunto de arcos de la red. Se ocupa el diccionario de arcos.
    :param nodos: conjunto de nodos de la red. Se ocupa el diccionario de nodos.
    :return:
    '''
    for arco in arcos:
        nodos[arcos[arco].origen].arcosOut.append(arcos[arco])
        nodos[arcos[arco].destino].arcosIn.append(arcos[arco])

def asignarViajesLineas(red):
    '''
    Una vez que estan cargados todos los ods, lineas, arcos y nodos, procedemos a asignar la demanda de los od
    a las distintas lineas, indicando en que nodo se realiza la transferencia.
    Criterios:
    1)Viaje directo-Que la linea salga del nodo origen y llegue al nodo destino.
    2)Viaje indirecto-Cualquier otro caso, debe encontrarse el conjunto de lineas que sirven para aquello y el lugar de
    transferencia.

    :param ods:
    :param lineas:
    :param arcos:
    :param nodos:
    :return:
    '''

    ods = red.ods
    lineas = red.lineas
    arcos = red.arcos
    nodos = red.nodos

    #Para cada par od
    for od in ods:

        if ods[od].id == '4/36':
            print 'hola'


        lineasTupla = [None, None, None]#La misma lista que en la clase od
        nodoTransferencia = [None, None]

        lineasOrigenCualquiera = ods[od].origen.lineas #Lineas que llegan por el path al nodo en cuestion
        lineasDestinoCualquiera = ods[od].destino.lineas #Lineas que salen por el path del nodo en cuestion
        lineasOrigenSP = []
        lineasDestinoSP = []
        #Buscamos las lineas que salen del origen y llegan al destino segun los arcos de ruta minima. Estas seran las lineasXXXSP.
        for linea in lineas:
            if (ods[od].rutaArcos[0] in lineas[linea].arcos['ida']) or (ods[od].rutaArcos[0] in lineas[linea].arcos['vuelta']):
                lineasOrigenSP.append(lineas[linea])
            if (ods[od].rutaArcos[-1] in lineas[linea].arcos['ida']) or (ods[od].rutaArcos[-1] in lineas[linea].arcos['vuelta']):
                lineasDestinoSP.append(lineas[linea])


        #######-----------CASO DIRECTO en Shortest Path-----------################
        if lineasTupla[0] == None:
            #Vemos si la linea esta en el arco de salida y llegada del shortest path, y lo incluimos si corresponde.

            lineas1 = []
            for lOrigen in lineasOrigenSP:
                for lDestino in lineasDestinoSP:
                    if lOrigen == lDestino:
                        if (ods[od].rutaArcos[0] in lOrigen.arcos['ida']):
                            sentidoSubida = 'ida'
                        else:
                            sentidoSubida = 'vuelta'
                        if (ods[od].rutaArcos[-1] in lOrigen.arcos['ida']):
                            sentidoBajada = 'ida'
                        else:
                            sentidoBajada = 'vuelta'
                        lineas1.append([lOrigen, sentidoSubida, sentidoBajada])

            #Luego vemos si aquel conjunto lineas1 tiene elementos o no.
            if  len(lineas1) > 0:
                lineasTupla[0] = lineas1
                ods[od].directo = True
                red.demandaDirecta += ods[od].demanda

            #En caso de que no hayan lineas directas dentro de la ruta minima, buscamos lineas directas fuera del shortest path.

        #######-----------CASO DIRECTO en Cualquier Parte-----------################

        if lineasTupla[0] == None:

            lineas1 = []

            #Asignamos esta vez lineas que tan solo pasen por nodos origen y destino
            #Ojo que ahora no se pide que pasen por los arcos iniciales, por lo que puede ir en un sentido distinto
            #al del shortest path.


            for lOrigen in lineasOrigenCualquiera:
                for lDestino in lineasDestinoCualquiera:
                    #Se considera aca solo viajes en un sentido!!!!Esto se hace porque sino pueden dar viajes esxtremadamente largos.
                    if lOrigen[0] == lDestino[0] and lOrigen[1] == lDestino[1]:
                        #Ademas hay que procurar que dentro del sentido, el nodo de destino este despues que el el de origen
                        if verificarSentido(ods[od].origen, ods[od].destino, lOrigen[0], lOrigen[1]):
                            #Si cumple todos los requisitos, se incluye en lineas1
                            sentidoSubida = lOrigen[1]
                            sentidoBajada = lOrigen[1]
                            lineas1.append([lOrigen[0], sentidoSubida, sentidoBajada])

            #Volvemos a verificar si aquel conjunto tiene elementos o no.
            if len(lineas1) > 0:
                lineasTupla[0] = lineas1
                ods[od].directo = True
                red.demandaDirecta += ods[od].demanda

        #En caso de no haber, deifnitivamente se recurre a una transferencia

        #######-----------CASO 1 TRANSFERENCIA en Shortest Path-----------################

        if lineasTupla[0] == None:
            #Primero vemos si es posible llegar al destino con tan solo una transferencia en el shortest path
            #Para ello nos movemos en el shortest path, analizando los posibles nodos de transferencia
            #El nodo de transferencia es el target del lineaIn o source del lineaOut.
            #Finalmente queda la ruta con el nodo de transbordo mas cercano al destino.
            #Ojo que las lineas origen y destino son las aplicadas para caso cualquiera. El shortest path queda metido en el transbordo.

            for arco in range(len(ods[od].rutaArcos)-1):
                lineasIn = ods[od].rutaArcos[arco].lineas #Lineas que llegan por el path al nodo en cuestion
                lineasOut = ods[od].rutaArcos[arco + 1].lineas #Lineas que salen por el path del nodo en cuestion
                lineas1=[] #lineas que conectan el nodo en cuestion con el inicio
                lineas2=[] #lineas que conectan el nodo en cuestion con el final
                conexionInicio = False
                conexionFin = False

                #Primero agregamos las lineas del primer tramo
                for l in lineasIn:
                    if l in lineasOrigenSP:
                        conexionInicio = True
                        if (ods[od].rutaArcos[0] in l.arcos['ida']):
                            sentidoSubida = 'ida'
                        else:
                            sentidoSubida = 'vuelta'
                        if (ods[od].rutaArcos[arco] in l.arcos['ida']):
                            sentidoBajada = 'ida'
                        else:
                            sentidoBajada = 'vuelta'
                        lineas1.append([l, sentidoSubida, sentidoBajada])

                #Luego el segundo tramo
                for l in lineasOut:
                    if l in lineasDestinoSP:
                        conexionFin = True
                        if (ods[od].rutaArcos[arco + 1] in l.arcos['ida']):
                            sentidoSubida = 'ida'
                        else:
                            sentidoSubida = 'vuelta'
                        if (ods[od].rutaArcos[-1] in l.arcos['ida']):
                            sentidoBajada = 'ida'
                        else:
                            sentidoBajada = 'vuelta'
                        lineas2.append([l, sentidoSubida, sentidoBajada])

                #Finalmente verificamos si encontramos una asignacion posible. De ser asi la agregamos.
                #Se vuelve a iterar ocn el siguiente nodo, quedando con el mas cercano al destino.
                if conexionInicio and conexionFin:
                    nodoTransferencia[0] = nodos[ods[od].rutaArcos[arco].destino]
                    lineasTupla[0] = lineas1
                    lineasTupla[1] = lineas2
                    ods[od].nTransferencias = 1

            #Si al iterar sobre todos los arcos del shortest path no hay lineas, buscamos una sola transferencia en cualquier lado

        #######-----------CASO 1 TRANSFERENCIA Cualquiera-----------################


        if lineasTupla[0] == None:

            lineas1=[] #lineas que conectan el nodo de transferencia con el inicio
            lineas2=[] #lineas que conectan el nodo de transferencia con el final
            conexion = False
            nodosTrans = []

            for lineaOrigen in lineasOrigenCualquiera:
                for lineaDestino in lineasDestinoCualquiera:

                    #Primero vemos si las lineas se cruzan y aquel nodo sirve para llegar de origen a destino
                    checkNodoTransferencia = nodoCruceLineas(lineaOrigen, lineaDestino, ods[od].origen, ods[od].destino)

                    if (not checkNodoTransferencia == False):
                        #Bingo! Agregamos lineas y nodo y nos salimos del for con el primer descubrimiento.(no vamos a hacer estrategia de hyperpaths)

                        #Como el check permitia solo subidas y bajadas en el mismo sentido, agregamos el mismo
                        sentidoSubida = lineaOrigen[1]
                        sentidoBajada = lineaOrigen[1]

                        #Agregamos el nodo de transferencia
                        nodosTrans.append(checkNodoTransferencia)

                        #Luego la primera linea con sus sentidos
                        lineas1.append((lineaOrigen[0], sentidoSubida, sentidoBajada))

                        #Hacemos lo mismo ahora para la linea de destino
                        sentidoSubida = lineaDestino[1]
                        sentidoBajada = lineaDestino[1]

                        #Se agrega la linea con sus sentidos
                        lineas2.append((lineaDestino[0], sentidoSubida, sentidoBajada))
                        conexion = True


            if conexion:
                #Buscamos ahora la ruta mas corta entre las posibilidades encontradas
                largoRutaMax = 10000000000000
                for l in range(len(lineas1)):
                    largoRuta = largoEntreNodos(lineas1[l][0], lineas1[l][1], lineas1[l][2], ods[od].origen, nodosTrans[l]) + largoEntreNodos(lineas2[l][0], lineas2[l][1], lineas2[l][2], nodosTrans[l], ods[od].destino)
                    if largoRuta < largoRutaMax:
                        nodoTransferencia[0] = nodosTrans[l]
                        lineasTupla[0] = [lineas1[l]]#Las lineas deben agregarse como lista, ya que en los otros casos de asignacion hay mas de una.
                        lineasTupla[1] = [lineas2[l]]
                        largoRutaMax = largoRuta
                ods[od].nTransferencias = 1

        #Si pese a eso no hay posibilidad de viaje con una conexion, buscamos dos transferencias.

        #######-----------CASO 2 TRANSFERENCIAS-----------################

        if lineasTupla[0] == None:
            #Aca dividimos las dos transferencias en dos casos:1) BRT Cerrado, 2)BRT Actual
            if red.tipoRed == 'cerrada':

                #En ese caso la primera transferencia se realiza al entrar al corredor y la segunda antes de salir
                lineas1 = [] #lineas que conectan la entrada al corredor con el inicio
                lineas2 = [None] #lineas que sirven como troncal. Normalmente es solo una.
                lineas3 = [] #Lineas que conectan la salida del corredor con el final

                for arco in range(1, len(ods[od].rutaArcos)):
                    #Hacemos algo parecido al de 1 transferencia en shortest path
                    lineasIn = ods[od].rutaArcos[arco - 1].lineas #Lineas que llegan por el path al nodo en cuestion
                    lineasOut = ods[od].rutaArcos[arco].lineas #Lineas que salen por el path del nodo en cuestion

                    #Se chequea si el arco anterior de la ruta esta fuera del corredor y el actual dentro.
                    if ((ods[od].rutaArcos[arco] in lineas[10].arcos['ida']) or (ods[od].rutaArcos[arco] in lineas[10].arcos['vuelta'])) and (not (ods[od].rutaArcos[arco-1] in lineas[10].arcos['ida'] or ods[od].rutaArcos[arco-1] in lineas[10].arcos['vuelta'])):
                        #En ese caso se agrega el nodo.
                        nodoTransferencia[0] = nodos[ods[od].rutaArcos[arco].origen]

                        #luego se busca el sentido de subida del troncal, luego este se agrega,
                        if (ods[od].rutaArcos[arco] in red.lineas[10].arcos['ida']):
                            sentidoSubida = 'ida'
                        else:
                            sentidoSubida = 'vuelta'
                        lineas2[0] = [red.lineas[10], sentidoSubida, None]#Falta agregar el sentido bajada

                        #Ahora buscamos las lineas que lleguen desde el origen al inicio del troncal(lineas1)
                        for l in lineasIn:
                            if l in lineasOrigenSP:

                                if (ods[od].rutaArcos[0] in l.arcos['ida']):
                                    sentidoSubida = 'ida'
                                else:
                                    sentidoSubida = 'vuelta'
                                if (ods[od].rutaArcos[arco - 1] in l.arcos['ida']):
                                    sentidoBajada = 'ida'
                                else:
                                    sentidoBajada = 'vuelta'
                                lineas1.append([l, sentidoSubida, sentidoBajada])

                    #Ahora buscamos el nodo de salida del troncal
                    if (not (ods[od].rutaArcos[arco] in lineas[10].arcos['ida'] or ods[od].rutaArcos[arco] in lineas[10].arcos['vuelta'])) and ((ods[od].rutaArcos[arco-1] in lineas[10].arcos['ida']) or (ods[od].rutaArcos[arco-1] in lineas[10].arcos['vuelta'])):
                        #Esta condicion nos hizo tener problemas para la red cerrada.
                        nodoTransferencia[1] = nodos[ods[od].rutaArcos[arco].origen]

                        for l in lineasOut:
                            if l in lineasDestinoSP:

                                #Buscamos la linea que conecta con el final desde el segundo nodo de transferencia
                                if (ods[od].rutaArcos[arco] in l.arcos['ida']):
                                    sentidoSubida = 'ida'
                                else:
                                    sentidoSubida = 'vuelta'
                                if (ods[od].rutaArcos[-1] in l.arcos['ida']):
                                    sentidoBajada = 'ida'
                                else:
                                    sentidoBajada = 'vuelta'
                                lineas3.append([l, sentidoSubida, sentidoBajada])
                                #Finalmente agregamos el sentido bajada del corredor
                                if (ods[od].rutaArcos[arco-1] in red.lineas[10].arcos['ida']):
                                    sentidoBajada = 'ida'
                                else:
                                    sentidoBajada = 'vuelta'
                                lineas2[0][2] = sentidoBajada
                lineasTupla[0] = lineas1
                lineasTupla[1] = lineas2
                lineasTupla[2] = lineas3
                ods[od].nTransferencias = 2

            elif red.tipoRed == 'actual':
                print ods[od].id

                #Vamos agregando manualmente las asignaciones que requieran dos transbordos en la red actual.
                if ods[od].id == "35/33":
                    nodoTransferencia[0] = nodos[79]
                    nodoTransferencia[1] = nodos[32]
                    lineasTupla[0] = [[red.lineas[9], 'vuelta', 'vuelta']]
                    lineasTupla[1] = [[red.lineas[9], 'ida', 'ida']]
                    lineasTupla[2] = [[red.lineas[9], 'vuelta', 'vuelta']]


        ods[od].lineas = lineasTupla
        ods[od].nodosTransferencia = nodoTransferencia
        ods[od].TotalNTransferencias = ods[od].nTransferencias*ods[od].demanda
        red.Transferencias += ods[od].TotalNTransferencias
        red.transferenciasPromedio = red.Transferencias/red.demandaTotal

        if ods[od].nTransferencias > 0 :
            red.demandaIndirecta += ods[od].demanda



def asignarCarga(red):
    '''
    A Partir de las demandasde ods, asigna las subidas, bajadas y cargas de cada linea segun sentido en cada uno de los nodos.
    1) Para cada od, se indica a cada linea donde suben y bajan pasajeros a las lineas utiles para ese path.
    2) En cada od, la demanda se reparte segun la proporcion de frecuencia.
    3) Ya con todos los ods procesados, se hacen calculos de carga sobre las lineas.
    :param ods:
    :param lineas:
    :return:
    '''
    ods = red.ods
    lineasGlobal = red.lineas

    #Primero reseteamos la carga y RPK
    for l in lineasGlobal:
        lineasGlobal[l].RPK = 0
        lineasGlobal[l].ASK = 0
        lineasGlobal[l].FOPromedio = 0
        for a in lineasGlobal[l].arcos['ida']:
            lineasGlobal[l].infoCarga['ida'][0][a.origen] = 0
            lineasGlobal[l].infoCarga['ida'][1][a.origen] = 0
            lineasGlobal[l].infoCarga['ida'][2][a.origen] = 0
            lineasGlobal[l].infoCarga['ida'][3][a.origen] = 0
        for a in lineasGlobal[l].arcos['vuelta']:
            lineasGlobal[l].infoCarga['vuelta'][0][a.origen] = 0
            lineasGlobal[l].infoCarga['vuelta'][1][a.origen] = 0
            lineasGlobal[l].infoCarga['vuelta'][2][a.origen] = 0
            lineasGlobal[l].infoCarga['vuelta'][3][a.origen] = 0

        for a in lineasGlobal[l].arcos['ida']:#TODO aca queda redundante sacar en origen y destino por la falta de una lista de nodos por linelineasGlobal[l].arcos['vuelta'][a].
            lineasGlobal[l].infoCarga['ida'][0][a.destino] = 0
            lineasGlobal[l].infoCarga['ida'][1][a.destino] = 0
            lineasGlobal[l].infoCarga['ida'][2][a.destino] = 0
            lineasGlobal[l].infoCarga['ida'][3][a.destino] = 0
        for a in lineasGlobal[l].arcos['vuelta']:
            lineasGlobal[l].infoCarga['vuelta'][0][a.destino] = 0
            lineasGlobal[l].infoCarga['vuelta'][1][a.destino] = 0
            lineasGlobal[l].infoCarga['vuelta'][2][a.destino] = 0
            lineasGlobal[l].infoCarga['vuelta'][3][a.destino] = 0
        lineasGlobal[l].cargaMaxima = 0


    #Luego hacemos los calculos
    for od in ods:
        lineas = ods[od].lineas
        nodos = ods[od].nodosTransferencia

        #Vamos a tratar el tema en tres casos, viajes, directos, 1 transferencia o 2 transferencias
        #######-----------CASO DIRECTO-----------################
        if nodos[0] == None and nodos[1] == None:
                    frecuenciaTotalTramo = 0
                    for l in range(len(lineas[0])):
                        frecuenciaTotalTramo += lineas[0][l][0].f
                    #Ahora dividimos la demanda
                    for l in range(len(lineas[0])):
                        sentidoSubida = lineas[0][l][1]
                        sentidoBajada = lineas[0][l][2]
                        #Agregamos primero las subidas
                        lineas[0][l][0].infoCarga[sentidoSubida][1][ods[od].origen.id] += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f
                        #Luego las bajadas
                        lineas[0][l][0].infoCarga[sentidoBajada][2][ods[od].destino.id] += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f

        #######-----------CASO 1 TRANSFERENCIA-----------################
        elif nodos[1] == None:

                    ####      PRIMER TRAMO
                    frecuenciaTotalTramo = 0
                    for l in range(len(lineas[0])):
                        frecuenciaTotalTramo += lineas[0][l][0].f
                    #Ahora dividimos la demanda
                    for l in range(len(lineas[0])):
                        sentidoSubida = lineas[0][l][1]
                        sentidoBajada = lineas[0][l][2]
                        #Agregamos primero las subidas al nodo de origen
                        lineas[0][l][0].infoCarga[sentidoSubida][1][ods[od].origen.id] += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f
                        #Luego las bajadas al nodo de la primera transferencia
                        lineas[0][l][0].infoCarga[sentidoBajada][2][nodos[0].id] += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f

                    ####      SEGUNDO TRAMO
                    frecuenciaTotalTramo = 0
                    for l in range(len(lineas[1])):
                        frecuenciaTotalTramo += lineas[1][l][0].f
                    #Ahora dividimos la demanda
                    for l in range(len(lineas[1])):
                        sentidoSubida = lineas[1][l][1]
                        sentidoBajada = lineas[1][l][2]
                        #Agregamos primero las subidas al primer nodo de transferencia
                        lineas[1][l][0].infoCarga[sentidoSubida][1][nodos[0].id] += (ods[od].demanda*lineas[1][l][0].f/frecuenciaTotalTramo)/lineas[1][l][0].f
                        #Luego las bajadas al destino
                        lineas[1][l][0].infoCarga[sentidoBajada][2][ods[od].destino.id] += (ods[od].demanda*lineas[1][l][0].f/frecuenciaTotalTramo)/lineas[1][l][0].f


        #######-----------CASO 2 TRANSFERENCIAS-----------################
        else:

                    ####      PRIMER TRAMO
                    frecuenciaTotalTramo = 0
                    for l in range(len(lineas[0])):
                        frecuenciaTotalTramo += lineas[0][l][0].f
                    #Ahora dividimos la demanda
                    for l in range(len(lineas[0])):
                        sentidoSubida = lineas[0][l][1]
                        sentidoBajada = lineas[0][l][2]
                        #Vemos si debe asignarse esta carga a la inicial de la linea
                        if sentidoSubida == "vuelta" and sentidoBajada == "ida":
                            lineas[0][l][0].cargaInicial += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f
                        #Agregamos primero las subidas al nodo de origen
                        lineas[0][l][0].infoCarga[sentidoSubida][1][ods[od].origen.id] += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f
                        #Luego las bajadas al nodo de la primera transferencia
                        lineas[0][l][0].infoCarga[sentidoBajada][2][nodos[0].id] += (ods[od].demanda*lineas[0][l][0].f/frecuenciaTotalTramo)/lineas[0][l][0].f

                    ####      SEGUNDO TRAMO
                    frecuenciaTotalTramo = 0
                    for l in range(len(lineas[1])):
                        frecuenciaTotalTramo += lineas[1][l][0].f
                    #Ahora dividimos la demanda
                    for l in range(len(lineas[1])):
                        sentidoSubida = lineas[1][l][1]
                        sentidoBajada = lineas[1][l][2]
                        #Vemos si debe asignarse esta carga a la inicial
                        if sentidoSubida == "vuelta" and sentidoBajada == "ida":
                            lineas[1][l][0].cargaInicial += (ods[od].demanda*lineas[1][l][0].f/frecuenciaTotalTramo)/lineas[1][l][0].f
                        #Agregamos primero las subidas al primer nodo de transferencia
                        lineas[1][l][0].infoCarga[sentidoSubida][1][nodos[0].id] += (ods[od].demanda*lineas[1][l][0].f/frecuenciaTotalTramo)/lineas[1][l][0].f
                        #Luego las bajadas al segundo nodo de transferencia
                        lineas[1][l][0].infoCarga[sentidoBajada][2][nodos[1].id] += (ods[od].demanda*lineas[1][l][0].f/frecuenciaTotalTramo)/lineas[1][l][0].f

                    ####      TERCER TRAMO
                    frecuenciaTotalTramo = 0
                    for l in range(len(lineas[2])):
                        frecuenciaTotalTramo += lineas[2][l][0].f
                    #Ahora dividimos la demanda
                    for l in range(len(lineas[2])):
                        sentidoSubida = lineas[2][l][1]
                        sentidoBajada = lineas[2][l][2]
                        #Agregamos carga inicial en caso de que sea el caso
                        if sentidoSubida == "vuelta" and sentidoBajada == "ida":
                            lineas[2][l][0].cargaInicial += (ods[od].demanda*lineas[2][l][0].f/frecuenciaTotalTramo)/lineas[2][l][0].f
                        #Agregamos primero las subidas al segundo nodo de transferencia
                        lineas[2][l][0].infoCarga[sentidoSubida][1][nodos[1].id] += (ods[od].demanda*lineas[2][l][0].f/frecuenciaTotalTramo)/lineas[2][l][0].f
                        #Luego las bajadas al destino
                        lineas[2][l][0].infoCarga[sentidoBajada][2][ods[od].destino.id] += (ods[od].demanda*lineas[2][l][0].f/frecuenciaTotalTramo)/lineas[2][l][0].f


    #Finalmente para cada linea, calculamos la carga en cada tramo y RPK
    #Primero para la ida, luego para la vuelta
    for l in lineasGlobal:
    #Ida
        arcos = lineasGlobal[l].arcos['ida']
        lineasGlobal[l].infoCarga['ida'][0][arcos[0].origen] = lineasGlobal[l].cargaInicial + lineasGlobal[l].infoCarga['ida'][1][arcos[0].origen]-lineasGlobal[l].infoCarga['ida'][2][arcos[0].origen]
        lineasGlobal[l].RPK += lineasGlobal[l].infoCarga['ida'][0][arcos[0].origen]*arcos[0].largo
        for c in range(1, len(arcos)):
            lineasGlobal[l].infoCarga['ida'][0][arcos[c].origen] = lineasGlobal[l].infoCarga['ida'][1][arcos[c].origen]-lineasGlobal[l].infoCarga['ida'][2][arcos[c].origen] + lineasGlobal[l].infoCarga['ida'][0][arcos[c-1].origen]
            lineasGlobal[l].RPK += lineasGlobal[l].infoCarga['ida'][0][arcos[c].origen]*arcos[c].largo
        lineasGlobal[l].infoCarga['ida'][0][arcos[-1].destino] = lineasGlobal[l].infoCarga['ida'][1][arcos[-1].destino]-lineasGlobal[l].infoCarga['ida'][2][arcos[-1].destino] + lineasGlobal[l].infoCarga['ida'][0][arcos[-1].origen]

    #Ahora lo mismo en la vuelta. Se incluye la carga residual que quedo al final del sentido ida
        arcos = lineasGlobal[l].arcos['vuelta']
        lineasGlobal[l].infoCarga['vuelta'][0][arcos[0].origen] = lineasGlobal[l].infoCarga['ida'][0][lineasGlobal[l].arcos['ida'][-1].destino] + lineasGlobal[l].infoCarga['vuelta'][1][arcos[0].origen]-lineasGlobal[l].infoCarga['vuelta'][2][arcos[0].origen]
        lineasGlobal[l].RPK += lineasGlobal[l].infoCarga['vuelta'][0][arcos[0].origen]*arcos[0].largo
        for c in range(1, len(arcos)):
            lineasGlobal[l].infoCarga['vuelta'][0][arcos[c].origen] = lineasGlobal[l].infoCarga['vuelta'][1][arcos[c].origen]-lineasGlobal[l].infoCarga['vuelta'][2][arcos[c].origen] + lineasGlobal[l].infoCarga['vuelta'][0][arcos[c-1].origen]
            lineasGlobal[l].RPK += lineasGlobal[l].infoCarga['vuelta'][0][arcos[c].origen]*arcos[c].largo
        lineasGlobal[l].infoCarga['vuelta'][0][arcos[-1].destino] = lineasGlobal[l].infoCarga['vuelta'][1][arcos[-1].destino]-lineasGlobal[l].infoCarga['vuelta'][2][arcos[-1].destino] + lineasGlobal[l].infoCarga['vuelta'][0][arcos[-1].origen]


    #Antes de terminar buscamos la carga maxima
        arcos = lineasGlobal[l].arcos['ida']
        for c in arcos:
            if lineasGlobal[l].infoCarga['ida'][0][c.origen] > lineasGlobal[l].cargaMaxima:
                lineasGlobal[l].cargaMaxima = lineasGlobal[l].infoCarga['ida'][0][c.origen]
            if lineasGlobal[l].infoCarga['ida'][0][c.destino] > lineasGlobal[l].cargaMaxima:
                lineasGlobal[l].cargaMaxima = lineasGlobal[l].infoCarga['ida'][0][c.destino]
        arcos = lineasGlobal[l].arcos['vuelta']
        for c in arcos:
            if lineasGlobal[l].infoCarga['vuelta'][0][c.origen] > lineasGlobal[l].cargaMaxima:
                lineasGlobal[l].cargaMaxima = lineasGlobal[l].infoCarga['vuelta'][0][c.origen]
            if lineasGlobal[l].infoCarga['vuelta'][0][c.destino] > lineasGlobal[l].cargaMaxima:
                lineasGlobal[l].cargaMaxima = lineasGlobal[l].infoCarga['vuelta'][0][c.destino]
        lineasGlobal[l].RPK = lineasGlobal[l].RPK*lineasGlobal[l].f
        lineasGlobal[l].ASK = lineasGlobal[l].cargaMaxima*lineasGlobal[l].largoTotal*lineasGlobal[l].f
        lineasGlobal[l].FOPromedio = lineasGlobal[l].RPK/lineasGlobal[l].ASK
        lineasGlobal[l].cargaPromedio = lineasGlobal[l].FOPromedio*lineasGlobal[l].cargaMaxima

def tiempoParadaLineas(red):
    '''
    Funcion que calcula los tiempos de parada variable de las lineas, en funcion de la informacion de infocarga.
    Asume que infocarga ya esta asignado.
    :param lineas:
    :return:
    '''

    lineas = red.lineas
    tsp = red.parametros['tsp']
    tbp = red.parametros['tbp']
    tsc = red.parametros['tsc']
    tparadafijo = red.parametros['tparadaFija']

    #Primero reseteamos los tiempos de las lineas
    for l in lineas:
        lineas[l].tiempoParadasTotal = 0

    #Luego hacemos los calculos
    for l in lineas:
        ####IDA####
        arcos = lineas[l].arcos['ida']

        #Primer nodo
        lineas[l].tparadaFijo['ida'][arcos[0].id] = arcos[0].largo/arcos[0].spacing*tparadafijo
        lineas[l].tiempoParadasTotal += arcos[0].largo/arcos[0].spacing*tparadafijo
        if arcos[0].tipo == 'corredor':
            lineas[l].tparadaVariable['ida'][arcos[0].origen] = (lineas[l].infoCarga['ida'][1][arcos[0].origen] + lineas[l].infoCarga['ida'][2][arcos[0].origen])*tsc
            lineas[l].tiempoParadasTotal += (lineas[l].infoCarga['ida'][1][arcos[0].origen] + lineas[l].infoCarga['ida'][2][arcos[0].origen])*tsc
        else:
            lineas[l].tparadaVariable['ida'][arcos[0].origen] = max(lineas[l].infoCarga['ida'][1][arcos[0].origen]*tsp, lineas[l].infoCarga['ida'][2][arcos[0].origen]*tbp)
            lineas[l].tiempoParadasTotal += max(lineas[l].infoCarga['ida'][1][arcos[0].origen]*tsp, lineas[l].infoCarga['ida'][2][arcos[0].origen]*tbp)

        #Nodos intermedios
        for c in range(1, len(arcos)):
            lineas[l].tparadaFijo['ida'][arcos[c].id] = arcos[c].largo/arcos[c].spacing*tparadafijo
            lineas[l].tiempoParadasTotal += arcos[c].largo/arcos[c].spacing*tparadafijo
            if arcos[c].tipo == 'corredor':
                lineas[l].tparadaVariable['ida'][arcos[c].origen] = (lineas[l].infoCarga['ida'][1][arcos[c].origen] + lineas[l].infoCarga['ida'][2][arcos[c].origen])*tsc
                lineas[l].tiempoParadasTotal += (lineas[l].infoCarga['ida'][1][arcos[c].origen] + lineas[l].infoCarga['ida'][2][arcos[c].origen])*tsc
            else:
                lineas[l].tparadaVariable['ida'][arcos[c].origen] = max(lineas[l].infoCarga['ida'][1][arcos[c].origen]*tsp, lineas[l].infoCarga['ida'][2][arcos[c].origen]*tbp)
                lineas[l].tiempoParadasTotal += max(lineas[l].infoCarga['ida'][1][arcos[c].origen]*tsp, lineas[l].infoCarga['ida'][2][arcos[c].origen]*tbp)

        #Ultimo nodo
        if arcos[-1].tipo == 'corredor':
            lineas[l].tparadaVariable['ida'][arcos[-1].destino] = (lineas[l].infoCarga['ida'][1][arcos[-1].destino] + lineas[l].infoCarga['ida'][2][arcos[-1].destino])*tsc
            lineas[l].tiempoParadasTotal += (lineas[l].infoCarga['ida'][1][arcos[-1].destino] + lineas[l].infoCarga['ida'][2][arcos[-1].destino])*tsc
        else:
            lineas[l].tparadaVariable['ida'][arcos[-1].destino] = max(lineas[l].infoCarga['ida'][1][arcos[-1].destino]*tsp, lineas[l].infoCarga['ida'][2][arcos[-1].destino]*tbp)
            lineas[l].tiempoParadasTotal += max(lineas[l].infoCarga['ida'][1][arcos[-1].destino]*tsp, lineas[l].infoCarga['ida'][2][arcos[-1].destino]*tbp)

        ####VUELTA###
        arcos = lineas[l].arcos['vuelta']

        #Primer nodo
        lineas[l].tparadaFijo['vuelta'][arcos[0].id] = arcos[0].largo/arcos[0].spacing*tparadafijo
        lineas[l].tiempoParadasTotal += arcos[0].largo/arcos[0].spacing*tparadafijo
        if arcos[0].tipo == 'corredor':
            lineas[l].tparadaVariable['vuelta'][arcos[0].origen] = (lineas[l].infoCarga['vuelta'][1][arcos[0].origen] + lineas[l].infoCarga['vuelta'][2][arcos[0].origen])*tsc
            lineas[l].tiempoParadasTotal += (lineas[l].infoCarga['vuelta'][1][arcos[0].origen] + lineas[l].infoCarga['vuelta'][2][arcos[0].origen])*tsc
        else:
            lineas[l].tparadaVariable['vuelta'][arcos[0].origen] = max(lineas[l].infoCarga['vuelta'][1][arcos[0].origen]*tsp, lineas[l].infoCarga['vuelta'][2][arcos[0].origen]*tbp)
            lineas[l].tiempoParadasTotal += max(lineas[l].infoCarga['vuelta'][1][arcos[0].origen]*tsp, lineas[l].infoCarga['vuelta'][2][arcos[0].origen]*tbp)

        #Nodos intermedios
        for c in range(1, len(arcos)):
            lineas[l].tparadaFijo['vuelta'][arcos[c].id] = arcos[c].largo/arcos[c].spacing*tparadafijo
            lineas[l].tiempoParadasTotal += arcos[c].largo/arcos[c].spacing*tparadafijo
            if arcos[c].tipo == 'corredor':
                lineas[l].tparadaVariable['vuelta'][arcos[c].origen] = (lineas[l].infoCarga['vuelta'][1][arcos[c].origen] + lineas[l].infoCarga['vuelta'][2][arcos[c].origen])*tsc
                lineas[l].tiempoParadasTotal += (lineas[l].infoCarga['vuelta'][1][arcos[c].origen] + lineas[l].infoCarga['vuelta'][2][arcos[c].origen])*tsc
            else:
                lineas[l].tparadaVariable['vuelta'][arcos[c].origen] = max(lineas[l].infoCarga['vuelta'][1][arcos[c].origen]*tsp, lineas[l].infoCarga['vuelta'][2][arcos[c].origen]*tbp)
                lineas[l].tiempoParadasTotal += max(lineas[l].infoCarga['vuelta'][1][arcos[c].origen]*tsp, lineas[l].infoCarga['vuelta'][2][arcos[c].origen]*tbp)

        #Ultimo nodo
        if arcos[-1].tipo == 'corredor':
            lineas[l].tparadaVariable['vuelta'][arcos[-1].destino] = (lineas[l].infoCarga['vuelta'][1][arcos[-1].destino] + lineas[l].infoCarga['vuelta'][2][arcos[-1].destino])*tsc
            lineas[l].tiempoParadasTotal += (lineas[l].infoCarga['vuelta'][1][arcos[-1].destino] + lineas[l].infoCarga['vuelta'][2][arcos[-1].destino])*tsc
        else:
            lineas[l].tparadaVariable['vuelta'][arcos[-1].destino] = max(lineas[l].infoCarga['vuelta'][1][arcos[-1].destino]*tsp, lineas[l].infoCarga['vuelta'][2][arcos[-1].destino]*tbp)
            lineas[l].tiempoParadasTotal += max(lineas[l].infoCarga['vuelta'][1][arcos[-1].destino]*tsp, lineas[l].infoCarga['vuelta'][2][arcos[-1].destino]*tbp)

        #Aprovechamos tambien de setear el tiempo de ciclo de la linea, el tiempo de la flota y su velocidad comercial.
        lineas[l].tiempoCiclo = lineas[l].tiempoParadasTotal + lineas[l].tiempoMovimientoTotal
        lineas[l].flota = lineas[l].tiempoCiclo*lineas[l].f
        lineas[l].velocidadComercial = lineas[l].largoTotal/lineas[l].tiempoCiclo


def fo(red):
    '''

    :param red:
    :return:se retorna una funcion callable que ocupara scipy para evaluar la funcion objetivo respecto a las distintas frecuencias
    '''

    #Hacemos un diccionario que pase el ID de las lineas a numeracion interna
    dicLineas = {}
    i=0
    for l in red.lineas:
        dicLineas[red.lineas[l].linea] = i
        i += 1


    #Luego definimos la funcion que se entregara a scipy para ir probando la relacion Input/Output a optimizar. Lo que necesitamos que cambie durante la optimizacion,
    #debe cambiarse dentro de esta funcion.
    def f(x):
        #Primero, actualizamos las frecuencias con el input.
        #Luego debe actualizarse lo que este relacionado con la frecuencia de modo de obtenerse un nuevo costo total.
        red.actualizarFrecuencias(x, dicLineas)

        #Finalmente retornamos el costo total de la red
        return red.CostoTotal

    return (f, dicLineas)

def optimiScipy(red):

    #obtenemos el diccionario con las variables con valores iniciales a ocupar y la fo
    func = fo(red)
    f = func[0]
    dicLineas = func[1]
    x0 = ()
    for i in range(len(dicLineas)):
        x0 = x0 + (100.0,)

    res = minimize(f, x0, method='COBYLA')

    #print res.x
    #for l in red.lineas:
    #    print str(l.microZonas[0].ID)+"-"+str(l.microZonas[-1].ID)+", ",

    return (res.x, dicLineas)

def nodoCruceLineas(linea1, linea2, origen, destino):
    '''
    chequea si hay alguna posible conexion entre ambas lineas y si ella sirve para llegar desde el origen al destino
    retorna el nodo de transferencia si existe, sino false
    :param linea1: tupla que contiene (linea, sentido) del origen normalmente
    :param linea2: tupla que ocntiene (linea, sentido) del destino normalmente
    :param origen: nodo de origen del od
    :param destino: nodo destino del od
    :return:
    '''

    for nodo in linea1[0].nodos[linea1[1]]:
        if nodo in linea2[0].nodos[linea2[1]]:
            if (verificarSentido(nodo, destino, linea2[0], linea2[1]) and verificarSentido(origen, nodo, linea1[0], linea1[1])):
                return nodo
    return False

def largoEntreNodos(linea, sentidoSubida, sentidoBajada, origen, destino):
    '''
    calcula la distancia
    :param linea:
    :param sentidoSubida:
    :param sentidoBajada:
    :param origen:
    :param destino:
    :return:
    '''
    largo = 0
    posicionOrigen = None
    posicionDestino = None
    if sentidoBajada == sentidoSubida:
        for nodo in range(len(linea.nodos[sentidoSubida])):
            if linea.nodos[sentidoSubida][nodo] == origen:
                posicionOrigen = nodo
            if linea.nodos[sentidoSubida][nodo] == destino:
                posicionDestino = nodo

        for n in range(posicionOrigen, posicionDestino):
            largo += linea.arcos[sentidoSubida][n].largo
    else:
        for nodo in range(len(linea.nodos[sentidoSubida])):
            if linea.nodos[sentidoSubida][nodo] == origen:
                posicionOrigen = nodo
        for nodo in range(len(linea.nodos[sentidoBajada])):
            if linea.nodos[sentidoBajada][nodo] == destino:
                posicionDestino = nodo
        for n in range(posicionOrigen, len(linea.nodos[sentidoSubida])-1):
            largo += linea.arcos[sentidoSubida][n].largo
        for n in range(0, posicionDestino):
            largo += linea.arcos[sentidoBajada][n].largo
    return largo

def calcularArcosRutaAsignada(od):
    '''

    :param od: Se asume que el od ya tiene asignada la forma en que viajan sus pasajeros.
    :return:
    '''
    #arcosSalida contiene para cada tramo del viaje, una lista con tuplas que contienen los arcos de cada ruta/linea y la frecuencia de la linea
    arcosSalida = [None, None, None]

    #Tenemos que controlar el caso en que se baja en un sentido distinto

    #Caso directo
    if od.nodosTransferencia[0] == None:

        arcosSalida[0]=[]
        for l in range(len(od.lineas[0])):
            lin = (rutaEnLinea(od.origen, od.destino, od.lineas[0][l][0], od.lineas[0][l][1], od.lineas[0][l][2]), od.lineas[0][l][0].f)
            arcosSalida[0].append(lin)

    #Caso 1 Transferencia
    elif od.nodosTransferencia[1] == None:

        arcosSalida[0] = []
        arcosSalida[1] = []

        #Primero la primera seccion
        for l in range(len(od.lineas[0])):
            lin = (rutaEnLinea(od.origen, od.nodosTransferencia[0], od.lineas[0][l][0], od.lineas[0][l][1], od.lineas[0][l][2]), od.lineas[0][l][0].f)
            arcosSalida[0].append(lin)

        #Luego concatenamos el segundo tramo
        for l in range(len(od.lineas[1])):
            lin = (rutaEnLinea(od.nodosTransferencia[0], od.destino, od.lineas[1][l][0], od.lineas[1][l][1], od.lineas[1][l][2]), od.lineas[1][l][0].f)
            arcosSalida[1].append(lin)

    #Caso 2 Transferencias
    else:

        arcosSalida[0]=[]
        arcosSalida[1]=[]
        arcosSalida[2]=[]

        #Primero la primera seccion
        for l in range(len(od.lineas[0])):
            lin = (rutaEnLinea(od.origen, od.nodosTransferencia[0], od.lineas[0][l][0], od.lineas[0][l][1], od.lineas[0][l][2]), od.lineas[0][l][0].f)
            arcosSalida[0].append(lin)

        #Luego concatenamos el segundo tramo
        for l in range(len(od.lineas[1])):
            lin = (rutaEnLinea(od.nodosTransferencia[0], od.nodosTransferencia[1], od.lineas[1][l][0], od.lineas[1][l][1], od.lineas[1][l][2]), od.lineas[1][l][0].f)
            arcosSalida[1].append(lin)

        #Finalmente el tercer tramo
        for l in range(len(od.lineas[2])):
            lin = (rutaEnLinea(od.nodosTransferencia[1], od.destino, od.lineas[2][l][0], od.lineas[2][l][1], od.lineas[2][l][2]), od.lineas[2][l][0].f)
            arcosSalida[2].append(lin)

    return arcosSalida

def verificarSentido(origen, destino, linea, sentido):
    '''

    :param origen: nodo origen
    :param destino: nodo destino
    :param linea: linea a verificar
    :param sentido: sentido de la linea
    :return: Verifica si el origen esta antes que el sentido en el sentido de la linea. Retorna bool.
    '''

    if linea.diccionarioNodos[sentido][origen.id] < linea.diccionarioNodos[sentido][destino.id]:
        return True
    else:
        return False

def rutaEnLinea(origen, destino, linea, sentidoSubida, sentidoBajada):
    '''

    :param origen:
    :param destino:
    :param linea:
    :param sentidoSubida:
    :param sentidoBajada:
    :return:retorna un arreglo de arcos en orden con la ruta que realiza un usuario dentro de una linea para un cierto od
    '''

    arcosSalida = []
    if sentidoSubida == sentidoBajada:
        posicionOrigen = linea.diccionarioNodos[sentidoSubida][origen.id]
        posicionDestino = linea.diccionarioNodos[sentidoSubida][destino.id]

        for a in range(posicionOrigen, posicionDestino):
            arcosSalida.append(linea.arcos[sentidoSubida][a])

    else:
        posicionOrigen = linea.diccionarioNodos[sentidoSubida][origen.id]
        for a in range(posicionOrigen, len(linea.arcos[sentidoSubida])):
            arcosSalida.append(linea.arcos[sentidoSubida][a])
        posicionDestino = linea.diccionarioNodos[sentidoBajada][destino.id]
        for a in range(0, posicionDestino):
            arcosSalida.append(linea.arcos[sentidoBajada][a])

    #Finalmente se retornan los arcos
    return arcosSalida

def arreglaNodosoRepetidos(od):
    '''

    :param od: od con ruta y subidas/bajadas ya asignadas
    :return: retorna el od con bajadas en primera instancia del nodo y subidas en la segunda.
    '''
    #TODO implementar esta funcion. Hay casos en que si hay que dejar subidas en la primera instancia del nodo.