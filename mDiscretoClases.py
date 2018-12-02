__author__ = 'Pancho'
from mDiscretoFunciones import*
import copy

class nodoAcceso(object):

    def __init__(self, id, vertice, distancia):
        self.id = id
        self.vertice = vertice
        self.distanciaAcceso = distancia

class nodo(object):

    def __init__(self, id):
        self.id = id
        self.nodoOD = False
        self.nodosAcceso = []
        self.acceso = 0 #Este valor debe venir obtenido de la base de datos.
        self.arcosIn=[]
        self.arcosOut=[]
        self.distanciaAcceso = 0
        self.lineas = []

class arco(object):

    def __init__(self, id, nombre, origen, destino, largo, velocidad, tipo):
        self.id = id
        self.nombre = nombre
        self.origen = origen
        self.destino = destino
        self.largo = largo
        self.velocidad = velocidad
        self.lineas = []
        self.tipo = tipo
        self.demandaSubio = 0 #Considera a los que partes y transfieren.
        self.demandaBajo = 0 #Considera a los que partes y transfieren.
        self.demandaEnRuta = 0 #Esto corresponde a la demanda que venia desde antes.
        self.demandaEnArco = 0 #Esta demanda corresponde al neto entre los que venian, subieron y bajaron.
        self.spacing = 0

class od(object):

    def __init__(self, origen, destino):
        self.origen = origen#Objeto nodo
        self.destino = destino#Objeto nodo
        self.id = str(origen.id) + "/" + str(destino.id)
        self.rutaArcos = [] #En su momento se le agregaran los arcos de la ruta en orden de principio a fin.
        self.rutaNodos = [] #En su momento se le agregaran los nodos de la ruta en orden de principio a fin.
        self.directo = False
        self.nodosTransferencia = [None, None]
        self.lineas = [None, None, None] #Lista con el conjunto de lineas que sirve para el primer tramo y el segundo y tercero en caso de par indirecto
        self.demanda = 0
        self.distancia = 0#Distancia entre ambos nodos.

        self.tEspera = [0, 0, 0]
        self.tEsperaSinDelta = [0, 0, 0] #Lo mismo que la lista anterior pero sin sumar a [1] y [2] la penalidad por transferencia.
        self.tViajeMovimiento = 0
        self.tViajeParadas = 0
        self.tViajeTotal = 0
        self.nTransferencias = 0 #Numero de transferencias que deben realizarse en el od
        self.tAccesoSpacing = 0
        self.tParadaFijo = 0
        self.tParadaVariable = 0

        self.TotaltMovimiento = 0
        self.TotaltParada = 0
        self.TotaltViaje = 0
        self.TotaltAccesoPerpendicular = 0
        self.TotaltAcceso = 0
        self.TotaltEspera = 0
        self.TotaltTransferencia = 0
        self.TotaltTransferenciaSinDelta = 0
        self.TotalNTransferencias = 0
        self.TotaltParadaFijo = 0
        self.TotaltParadaVariable = 0


        #self.k = k
        #self.tpp = tpp
        #self.tpc = tpc
        #self.tipo = tipo
        #self.deltaTT = delta
        #self.demandaDirecta = 0
        #self.demandaIndirecta = 0
        #self.demandaTotalRed = demandaTotalRed

        #self.distanciaPeriferia = self.dist[0]
        #self.distanciaCorredor = self.dist[1]
        #self.tParadas = None
        #self.tParadaPeriferia = 0
        #self.tParadaCorredor = 0
        #self.tMovimientoPeriferia = self.distanciaPeriferia/self.Vp
        #self.tMovimientoCorredor = self.distanciaCorredor/self.Vc
        #self.tViaje = self.tMovimientoPeriferia + self.tMovimientoCorredor + self.tParadaCorredor + self.tParadaCorredor


class linea(object):

    def __init__(self, nombre, linea, largo,  arcosIda, arcosVuelta, nodos, frecuencia):
        self.nombre = nombre
        self.linea = linea
        self.largoTotal = largo
        self.arcos = {}
        self.nodos = {}
        self.arcos['ida'] = arcosIda#Estos arcos son los que contienen el orden de la ruta de la linea. Info carga al ser un diccionario no o tiene.
        self.arcos['vuelta'] = arcosVuelta
        self.nodos['ida'] = [] #Estos nodos estan en orden tambien, como los arcos
        self.nodos['vuelta'] = []
        self.diccionarioNodos = {} #Diccionario que ocupa como key el id de un nodo y devuelve el lugar que ocupa en la lista ordenada
        self.diccionarioNodos['ida'] = {}
        self.diccionarioNodos['vuelta'] = {}
        self.f = frecuencia
        self.cargaInicial = 0 #Parametro a ocuparse para ver que usuarios comienzan arriba del bus al iniciar su recorrido. Se setea en asignarCargaf
        self.cargaMaxima = 0
        self.cargaPromedio = 0
        self.spacing = 0
        self.tiempoParadasTotal = 0
        self.tiempoMovimientoTotal = 0
        self.tiempoCiclo = 0
        self.velocidadComercial = 0
        self.ASK = 0
        self.RPK = 0
        self.FOPromedio = 0
        self.flota = 0
        #La info de carga debe estar separada segun direccion del servicio.
        #Esta tupla contiene cuatro diccionarios con la informacion de carga de pasajeros(0),
        # los que suben(1) y bajan(2) y el factor de ocupacion en ese arco(3) dentro del bus para la microzona dada por la llave.
        #El punto en que se calculan los indicadores de carga es en cada nodo
        self.infoCarga = {}
        self.infoCarga["ida"] = ({}, {}, {}, {})
        self.infoCarga["vuelta"] = ({}, {}, {}, {})
        self.tparadaVariable = {} #Se calcula a nivel de nodos. Se asigna mediante funcion hecha para aquello.
        self.tparadaVariable['ida'] = {}
        self.tparadaVariable['vuelta'] = {}
        self.tparadaFijo = {}#Este tiempo de parada se contabliza en cada arco.
        self.tparadaFijo['ida'] = {}
        self.tparadaFijo['vuelta'] = {}
        self.tiempoMovimiento = {}#Tiempo en movimiento para cada arco
        self.tiempoMovimiento['ida'] = {}
        self.tiempoMovimiento['vuelta'] = {}
        for a in self.arcos['ida']:
            self.tiempoMovimiento['ida'][a] = a.largo/a.velocidad
            self.tiempoMovimientoTotal += a.largo/a.velocidad
            self.infoCarga["ida"][0][a.origen] = 0
            self.infoCarga["ida"][1][a.origen] = 0
            self.infoCarga["ida"][2][a.origen] = 0
            self.infoCarga["ida"][3][a.origen] = 0
            self.nodos['ida'].append(nodos[a.origen])
            self.diccionarioNodos['ida'][a.origen] = len(self.nodos['ida']) - 1
            nodos[a.origen].lineas.append((self, 'ida'))
        for a in self.arcos['vuelta']:
            self.tiempoMovimiento['vuelta'][a] = a.largo/a.velocidad
            self.tiempoMovimientoTotal += a.largo/a.velocidad
            self.infoCarga["vuelta"][0][a.origen] = 0
            self.infoCarga["vuelta"][1][a.origen] = 0
            self.infoCarga["vuelta"][2][a.origen] = 0
            self.infoCarga["vuelta"][3][a.origen] = 0
            self.nodos['vuelta'].append(nodos[a.origen])
            self.diccionarioNodos['vuelta'][a.origen] = len(self.nodos['vuelta']) - 1
            nodos[a.origen].lineas.append((self, 'vuelta'))

        #Finalmente inicializamos el ultimo nodo de la linea
        self.infoCarga["ida"][0][self.arcos['ida'][-1].destino] = 0
        self.infoCarga["ida"][1][self.arcos['ida'][-1].destino] = 0
        self.infoCarga["ida"][2][self.arcos['ida'][-1].destino] = 0
        self.infoCarga["ida"][3][self.arcos['ida'][-1].destino] = 0
        self.nodos['ida'].append(nodos[self.arcos['ida'][-1].destino])
        self.diccionarioNodos['ida'][self.arcos['ida'][-1].destino] = len(self.nodos['ida']) - 1
        nodos[self.arcos['ida'][-1].destino].lineas.append((self, 'ida'))

        self.infoCarga["vuelta"][0][self.arcos['vuelta'][-1].destino] = 0
        self.infoCarga["vuelta"][1][self.arcos['vuelta'][-1].destino] = 0
        self.infoCarga["vuelta"][2][self.arcos['vuelta'][-1].destino] = 0
        self.infoCarga["vuelta"][3][self.arcos['vuelta'][-1].destino] = 0
        self.nodos['vuelta'].append(nodos[self.arcos['vuelta'][-1].destino])
        self.diccionarioNodos['vuelta'][self.arcos['vuelta'][-1].destino] = len(self.nodos['vuelta']) - 1
        nodos[self.arcos['vuelta'][-1].destino].lineas.append((self, 'vuelta'))

    def calcularLargoTotal(self):
        '''
        Asume que ya estan asignados los arcos. Simplemente suma los largos de los arcos de ida y de vuelta.
        :return:
        '''
        for a in self.arcos['ida']:
            self.largoTotal += a.largo
        for a in self.arcos['vuelta']:
            self.largoTotal += a.largo


class red(object):

    def __init__(self, parametros, cursor, tipored):

        nodos = {}
        arcos = {}
        ods = {}#Las key de este diccionario seran tuplas con el id del origen y del destino.
        nodosAcceso = {}#Este diccionario recopila la informacion de las zonas a nivel de nodos de acceso.
        lineas = {}

        #Primero toda la parte de la carga de datos
        #####--------NODOS-------#######
        #Primero creamos los vertices pgrouting
        cursor.execute("SELECT id FROM red_"+tipored+"_pgrouting_vertices_pgr")
        records = cursor.fetchall()
        print records[1].keys()
        for r in records:
            nodos[r['id']] = nodo(r['id'])

        #Luego creamos los centroides de acceso, que ocupan de id el de sus zonas eod respectivas.
        cursor.execute("SELECT * FROM nodos_acceso_red_"+tipored)
        records = cursor.fetchall()
        print records[1].keys()
        for r in records:
            nodosAcceso[r['ogc_fid']] = nodoAcceso(r['ogc_fid'], r['vertice_acceso'], r['distancia_acceso']/1000)
            #Aprovechamos de agregar el nodo a su vertice de acceso y setearlo como nodoOD
            nodos[r['vertice_acceso']].nodosAcceso.append(nodosAcceso[r['ogc_fid']])
            nodos[r['vertice_acceso']].nodoOD = True


        #####--------O/D-------#######
        #Primero se crean los pares od
        for n in nodos.values():
            if n.nodoOD:
                for m in nodos.values():
                    if m.nodoOD: #and (not n == m):
                        ods[(n.id, m.id)] = od(n, m)
        #Luego recorremos la tabla de la matriz de la base de datos y vamos asignando segun corresponda.
        #Al mismo tiempo vamos sumando al par el tiempo de acceso total. Lo hacemos ahora ya que luego tendremos mas de una
        #distancia de acceso por nodo, y no se sabra cuanta demanda asignarle a cada uno.
        cursor.execute('select * from eod2013')#eodbusycolectivo; eod2013
        records = cursor.fetchall()
        for r in records:
            ods[(nodosAcceso[r['zonaorigen']].vertice, nodosAcceso[r['zonadestino']].vertice)].demanda += r['viajes']
            ods[(nodosAcceso[r['zonaorigen']].vertice, nodosAcceso[r['zonadestino']].vertice)].TotaltAccesoPerpendicular += r['viajes']*(nodosAcceso[r['zonaorigen']].distanciaAcceso + nodosAcceso[r['zonadestino']].distanciaAcceso)/parametros['Va']
        #Por consideracion de simplicidad hecha mas adelante, se eliminan los od intrazonales
        odsCopy = ods.copy()
        for par in odsCopy:
            if odsCopy[par].origen == odsCopy[par].destino:
                del ods[par]
        sumaODUni = 0
        for OD in ods:
            if ods[OD].destino.id == 10:
                sumaODUni += ods[OD].demanda
        del odsCopy


        #####--------ARCOS-------#######
        cursor.execute("SELECT * FROM red_"+tipored+"_pgrouting")
        records = cursor.fetchall()
        for r in records:
            arcos[r['ogc_fid']] = arco(r['ogc_fid'], r['name'], r['source'], r['target'], r['largo']/1000, r['velocidad'], r['tipo'])
        #Con nodos y arcos listos procedemos a asignar aracos a nodos
        asignarArcosNodos(arcos, nodos)

        #####--------LINEAS-------#######
        ##Vamos a tener que sacar primero toda la info en un diccionario y luego crear las lineas
        dict = {}
        cursor.execute("select * from red_"+tipored)
        records = cursor.fetchall()
        arcosIda = None
        arcosVuelta = None
        lineaAnterior = None
        for r in records:
            #Creamos una nueva linea solo en el caso de que la fila sea de ida.
            if not dict.has_key(r['linea']):
                dict[r['linea']]={}
                dict[r['linea']]['nombre']=r['name']
                dict[r['linea']]['linea']=r['linea']
                dict[r['linea']]['largo']=0
                dict[r['linea']]['frecuencia'] = r['frecuencia']
            #Luego nos preocupamos de los arcos
            arcosx = asignarArcosLineas(r, arcos)
            if r['sentido'] == 'ida':
                dict[r['linea']]['arcosIda']=arcosx
            else:
                dict[r['linea']]['arcosVuelta']=arcosx
        #Luego de que estamos seguros de que tenemos toda la info de las lineas, las creamos
        for l in dict:
            lineas[l] = linea(dict[l]['nombre'], dict[l]['linea'], dict[l]['largo'],  dict[l]['arcosIda'], dict[l]['arcosVuelta'], nodos, dict[l]['frecuencia'])
            lineas[l].calcularLargoTotal()
        #Justo despues de crear todas las lineas, asignamos ahora a ellas a los arcos.
        asignarLineasArcos(arcos, lineas)


        #####--------RUTAS_MINIMAS-------#######
        #Tal como en las lineas, tendremos que sacar primero toda la info, para luego poder crear las rutas en orden.
        #Es necesario hacer esto, ya que el record no saca las filas en orden.
        #Indicar en el informe que los viajes intrazona se despreciarian. Son 86 de un total de 11362.
        #Preguntar ese detalle a Juanca.
        cursor.execute("SELECT * FROM resultados_red_"+tipored)
        records = cursor.fetchall()
        rutasArco = {}#La clave es el orgien y el destino. Luego contiene un diccionario con el arco y la secuencia.
        rutasNodo = {}#La clave es el orgien, el destino. Luego contiene un diccionario con el nodo y la secuencia.
        for r in records:
            #Solo nos preocuoamos por las rutas minimas entre los nodosOD
            if nodos[r['source']].nodoOD and nodos[r['target']].nodoOD:
                #Si no se encuentra la llave del od, le agregamos un diccionario.
                if not (r['source'], r['target']) in rutasArco:
                    rutasArco[(r['source'], r['target'])] = {}
                    rutasNodo[(r['source'], r['target'])] = {}
                #Luego agregamos el contenido
                rutasArco[(r['source'], r['target'])][r['seq']] = arcos[r['edge']]
                rutasNodo[(r['source'], r['target'])][r['seq']] = nodos[r['node']]
        #Una vez que tenemos toda la info, creamos una lista ordenada por la secuencia y agregamos para cada od
        for par in ods:
            if ods[par].origen.nodoOD and ods[par].destino.nodoOD and (not ods[par].origen == ods[par].destino):
                #if ods[par].origen.id == 75 and ods[par].destino.id == 36:
                #    print "este es"

                arcosOrdenados = []
                nodosOrdenados = []
                for a in range(len(rutasArco[(ods[par].origen.id, ods[par].destino.id)])):
                    arcosOrdenados.append(rutasArco[(ods[par].origen.id, ods[par].destino.id)][a])
                    ods[par].distancia += rutasArco[(ods[par].origen.id, ods[par].destino.id)][a].largo
                for a in range(len(rutasNodo[(ods[par].origen.id, ods[par].destino.id)])):
                    nodosOrdenados.append(rutasNodo[(ods[par].origen.id, ods[par].destino.id)][a])
                ods[par].rutaArcos = arcosOrdenados
                ods[par].rutaNodos = nodosOrdenados

        self.tipoRed = tipored
        self.lineas = lineas
        self.ods = ods
        self.arcos = arcos
        self.nodos = nodos
        self.parametros = parametros
        self.demandaTotal = calcularDemandaTotal(self)
        self.demandaDirecta = 0
        self.demandaIndirecta = 0
        self.Transferencias = 0
        self.spacingCarretera = 0
        self.spacingCorredor = 0
        self.spacingPeriferia = 0

        #Tiempos Totales
        self.TiemposPersonas = 0
        self.TotaltViaje = 0
        self.TotaltEspera = 0
        self.TotaltAcceso = 0
        self.TotaltTransferencia = 0
        self.TotaltTransferenciaSinDelta = 0
        self.TotaltMovimiento = 0
        self.TotaltParada = 0
        self.TotaltParadaFijo = 0
        self.TotaltParadaVariable = 0

        #Costos Totales
        self.CostoTotaltMovimiento = 0
        self.CostoTotaltParada = 0
        self.CostoTotaltParadaFijo = 0
        self.CostoTotaltParadaVariable = 0
        self.CostoTotaltViaje = 0
        self.CostoTotaltEspera = 0
        self.CostoTotaltAcceso = 0
        self.CostoTotaltTransferencia = 0
        self.CostoTotaltTransferenciaSinDelta = 0
        self.Costos = 0
        self.CostoOperacionLineas = None
        self.CostoOperacionTotal = 0
        self.CostoTotal = self.CostoOperacionTotal + self.CostoTotaltViaje + self.CostoTotaltEspera + self.CostoTotaltAcceso + self.CostoTotaltTransferencia

        #Promedios
        self.tMovimientoPromedio = self.TotaltMovimiento/self.demandaTotal
        self.tParadaPromedio = self.TotaltParada/self.demandaTotal
        self.tParadaFijoPromedio = self.TotaltParadaFijo/self.demandaTotal
        self.tParadaVariablePromedio = self.TotaltParadaVariable/self.demandaTotal
        self.tViajePromedio = self.TotaltViaje/self.demandaTotal
        self.tEsperaPromedio = self.TotaltEspera/self.demandaTotal
        self.tAccesoPromedio = self.TotaltAcceso/self.demandaTotal
        self.tTransferenciaSinDeltaPromedio = self.TotaltTransferenciaSinDelta/self.demandaTotal
        self.tTransferenciaPromedio = self.TotaltTransferencia/self.demandaTotal
        self.CostoTotaltViajePromedio = self.CostoTotaltViaje/self.demandaTotal
        self.CostoTotaltMovimientoPromedio = self.CostoTotaltMovimiento/self.demandaTotal
        self.CostoTotaltParadaPromedio = self.CostoTotaltParada/self.demandaTotal
        self.CostoTotaltEsperaPromedio = self.CostoTotaltEspera/self.demandaTotal
        self.CostoTotaltAccesoPromedio = self.CostoTotaltAcceso/self.demandaTotal
        self.CostoTotaltTransferenciaPromedio = self.CostoTotaltTransferencia/self.demandaTotal
        self.CostoTotaltTransferenciaSinDeltaPromedio = self.CostoTotaltTransferenciaSinDelta/self.demandaTotal
        self.CostoOperacionPromedio = self.CostoOperacionTotal/self.demandaTotal
        self.CostoTotalPromedio = self.CostoTotal/self.demandaTotal

        #Otros Indicadores Agregados
        self.transferenciasPromedio = self.Transferencias/self.demandaTotal
        self.ASKTotal = 0
        self.RPKTotal = 0
        self.FOPromedio = 0 #Factor de ocupacion promedio de los buses de la red.
        self.FlotaTotal = 0
        self.CapacidadPromedio = 0
        self.CapacidadOciosaTotal = 0
        self.frecuenciaPromedio = 0
        self.vComercialPromedio = 0
        self.largoViajePromedio = 0
        self.largoViajeTotal = 0 #Suma los viajes de toda la red

        #Crearemos un diccionario que ira guardando los indicadores de la red para cada valor de F que se tome. De esta manera podremos graficar cambios respecto a F.
        #Quizas simplemente podemos hacer un clon de la red(aunque eso puede tardar mucho).
        self.resultadosPorFrecuencia = {}#La llave corresponde a un id dado por la iteracion
        self.iteracion = 1#Contador de iteraciones del optimizador
        self.frecPorDistancia = 0

    def actualizarFrecuencias(self, f, dicLineas):
        '''

        :param f: corresponde a una lista con los nuevos valores de la frecuencia
        :param dicLineas: diccionario que relaciona los id de las lineas con la numeracion ocupada en SciPy
        :return:
        '''

        #Primero imprimimos en que iteracion vamos
        print "Iteracion "+ str(self.iteracion)

        #Antes de comenzar a actualizar, clonamos la red actual y la guardamos en el diccionario de esta.
        red = copy.copy(self)
        self.resultadosPorFrecuencia[self.iteracion] = red
        self.iteracion += 1

        for l in self.lineas:
            i = dicLineas[self.lineas[l].linea]
            self.lineas[l].f = f[i]
            self.lineas[l].cargaInicial = 0 #Aprovechamos el for para resetear cargas iniciales de las lineas.

        #Primero reseteamos los costos de la red
        resetearCostosRed(self)

        #Luego ejecutamos los metodos que dependen de la frecuencia
        asignarCarga(self)
        calcularSpacing(self)
        tiempoParadaLineas(self)
        calcularCostoOperacion(self)
        calcularCostosPersonas(self)

        #Ya con los indicadores agregados, sumamos el costo total
        self.CostoTotal = self.CostoOperacionTotal + self.CostoTotaltViaje + self.CostoTotaltEspera + self.CostoTotaltAcceso + self.CostoTotaltTransferencia
        self.CostoTotalPromedio = self.CostoTotal/self.demandaTotal


        #Tambien se actualizan algunos indicadores promedio
        #Con la carga reasignada, podemos recalcular los indicadores que dependen de ella.
        sumaFO = 0
        sumaCapacidadPromedio = 0
        sumaFrecuencia = 0
        sumavComercial = 0
        for l in self.lineas:
            sumaFO += self.lineas[l].FOPromedio*self.lineas[l].f*self.lineas[l].largoTotal
            sumaCapacidadPromedio += self.lineas[l].cargaMaxima*self.lineas[l].f*self.lineas[l].largoTotal
            sumaFrecuencia += self.lineas[l].f*self.lineas[l].f*self.lineas[l].largoTotal
            sumavComercial += self.lineas[l].velocidadComercial*self.lineas[l].f*self.lineas[l].largoTotal
            self.frecPorDistancia += self.lineas[l].f*self.lineas[l].largoTotal
            self.ASKTotal += self.lineas[l].ASK
            self.RPKTotal += self.lineas[l].RPK
            self.CapacidadOciosaTotal += self.lineas[l].ASK-self.lineas[l].RPK
            self.lineas[l].flota = self.lineas[l].tiempoCiclo*self.lineas[l].f
            self.FlotaTotal += self.lineas[l].flota
        self.FOPromedio = sumaFO/self.frecPorDistancia
        self.CapacidadPromedio = sumaCapacidadPromedio/self.frecPorDistancia
        self.frecuenciaPromedio = sumaFrecuencia/self.frecPorDistancia
        self.vComercialPromedio = sumavComercial/self.frecPorDistancia
        self.largoViajePromedio = self.largoViajeTotal/self.demandaTotal

    def calcularIndicadoresIniciales(self):
        '''

        :return:
        '''
        #Ya con los indicadores agregados, sumamos el costo total
        self.CostoTotal = self.CostoOperacionTotal + self.CostoTotaltViaje + self.CostoTotaltEspera + self.CostoTotaltAcceso + self.CostoTotaltTransferencia
        self.CostoTotalPromedio = self.CostoTotal/self.demandaTotal


        #Tambien se actualizan algunos indicadores promedio
        #Con la carga reasignada, podemos recalcular los indicadores que dependen de ella.
        sumaFO = 0
        sumaCapacidadPromedio = 0
        sumaFrecuencia = 0
        sumavComercial = 0
        for l in self.lineas:
            sumaFO += self.lineas[l].FOPromedio*self.lineas[l].f*self.lineas[l].largoTotal
            sumaCapacidadPromedio += self.lineas[l].cargaMaxima*self.lineas[l].f*self.lineas[l].largoTotal
            sumaFrecuencia += self.lineas[l].f*self.lineas[l].f*self.lineas[l].largoTotal
            sumavComercial += self.lineas[l].velocidadComercial*self.lineas[l].f*self.lineas[l].largoTotal
            self.frecPorDistancia += self.lineas[l].f*self.lineas[l].largoTotal
            self.ASKTotal += self.lineas[l].ASK
            self.RPKTotal += self.lineas[l].RPK
            self.CapacidadOciosaTotal += self.lineas[l].ASK-self.lineas[l].RPK
            self.lineas[l].flota = self.lineas[l].tiempoCiclo*self.lineas[l].f
            self.FlotaTotal += self.lineas[l].flota
        self.FOPromedio = sumaFO/self.frecPorDistancia
        self.CapacidadPromedio = sumaCapacidadPromedio/self.frecPorDistancia
        self.frecuenciaPromedio = sumaFrecuencia/self.frecPorDistancia
        self.vComercialPromedio = sumavComercial/self.frecPorDistancia
        self.largoViajePromedio = self.largoViajeTotal/self.demandaTotal