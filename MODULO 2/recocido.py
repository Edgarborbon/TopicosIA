import random
import math
import time

def costo(estado, objetivo):

    costo = 0
    for i in range(len(estado)):
        if estado[i] != objetivo[i]:
            costo += 1
    return costo


def recocido():

    eleccion = ''

    while eleccion != '1' and eleccion != '2' and eleccion != '3':

        print("""            1 = Arreglo pequeño [5, 2, 8, 1, 3, 7, 4, 6, 0]
            2 = Arreglo mediano [15, 1, 13, 19, 8, 2, 24, 18, 17, 7, 6, 23, 11, 22, 12, 10, 4, 3, 20, 14, 5, 16, 0, 9, 21]
            3 = Arreglo grande  [33, 11, 28, 1, 30, 21, 17, 26, 2, 22, 16, 23, 18, 4, 13, 27, 20, 15, 6, 8, 24, 7, 31, 3, 9, 5, 14, 19, 12, 29, 10, 0, 32, 25, 34]""")
        eleccion = input("Tamaño del arreglo: ")

        if eleccion ==  '1':
            estadoActual =   [5, 2, 8, 1, 3, 7, 4, 6, 0]
        elif eleccion =='2':
            estadoActual =   [15, 1, 13, 19, 8, 2, 24, 18, 17, 7, 6, 23, 11, 22, 12, 10, 4, 3, 20, 14, 5, 16, 0, 9, 21]
        elif eleccion =='3':
            estadoActual =   [33, 11, 28, 1, 30, 21, 17, 26, 2, 22, 16, 23, 18, 4, 13, 27, 20, 15, 6, 8, 24, 7, 31, 3, 9, 5, 14, 19, 12, 29, 10, 0, 32, 25, 34]
        else:
            print("Numero invalido")
            print(sep='')

    mostrarInfo = ''
    while mostrarInfo not in ["y", "n"]:

        mostrarInfo = input("¿Desea ver información de cada iteración? (y/n)").lower()
        
        if mostrarInfo not in ["y", "n"]:
            print("Introducir solo [y] o [n]")


    

    estadoObjetivo = sorted(estadoActual)
    N = len(estadoActual)

    tempInicial = N * 100.0
    temp = tempInicial
    tempMin = 0.1
    tasaEnfriamiento = 0.9
    L = N * 4


    costoActual = costo(estadoActual, estadoObjetivo)
    mejorEstado = list(estadoActual)
    costoMejor = costoActual
    costoCandidato = costoActual
    
    tiempoInicio = time.perf_counter()
    numIteracion = 0
    
    while temp > tempMin:
        numIteracion += 1
        
        if costoCandidato == 0:
            break

        for i in range(L):
            estadoNuevo = list(estadoActual)
            
            if temp > N: 
                x, y = random.sample(range(N), 2)
                inicio, fin = min(x, y), max(x, y)
                if fin > inicio:
                    porcionInvertida = estadoNuevo[inicio:fin]
                    porcionInvertida.reverse()
                    estadoNuevo[inicio:fin] = porcionInvertida
            else:
                pos1, pos2 = random.sample(range(N), 2)
                estadoNuevo[pos1], estadoNuevo[pos2] = estadoNuevo[pos2], estadoNuevo[pos1]

            costoNuevo = costo(estadoNuevo, estadoObjetivo)
            costoDiff = costoNuevo - costoActual
            
            if costoDiff < 0 or random.random() < math.exp(-costoDiff / temp):
                estadoActual = estadoNuevo
                costoActual = costoNuevo

            if costoActual < costoCandidato:
                mejorEstado = list(estadoActual)
                costoCandidato = costoActual
                if costoCandidato == 0:
                    break
        

        if mostrarInfo == 'y':            
            print(f"""
                    Iteracion N: {numIteracion} 
                    Temperatura actual: {temp:.2f} C°
                    Vecino generado: {estadoNuevo}
                    Costo de vecino generado: {costoNuevo}""")
                    
        if numIteracion % 10 == 0:
            temp *= 1.1
        else:
            temp *= tasaEnfriamiento

        

    tiempoFinal = time.perf_counter()
    tiempo = tiempoFinal - tiempoInicio

    if costoCandidato == 0:
        print("   - Solución Encontrada")
        print(f"   - Tiempo total: {tiempo:.4f} segundos.")
        print(f"   - Iteraciones: {numIteracion}")
        print(f"   - Solución: {mejorEstado}")
    else:
        print("   - No se encontró la solución")
        print(f"   - Mejor solución: {mejorEstado}")
        print(f"   - Costo: {costoCandidato}")

if __name__ == "__main__":
    recocido()








