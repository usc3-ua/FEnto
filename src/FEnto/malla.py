import numpy as np
import matplotlib.pyplot as plt

parametros_por_defecto = {
    "tipo": "uniforme",
    "xmax": 1.0,
    "ymax": 1.0,
    "xr": 10,
    "yd": 10,
    "R": 0.2
}

safe_env_2 = {"pi": np.pi, "e": np.e}

def leer_configuracion(archivo,defecto):
    config_leida = {}
    try:
        fichero = open(archivo, 'r')
        for linea in fichero:
            linea_original = linea
            linea = linea.strip() 
            if not linea or linea.startswith("#"): 
                continue

            if "=" not in linea:
                raise ValueError(f"La línea '{linea_original.strip()}' no contiene '='")

            linea = linea.replace("'", "").replace('"', "") 
            
            clave, valor = linea.split("=") 
            clave = clave.strip()
            valor = valor.strip()
            
            valores_validos_tipo = {"uniforme", "con agujero"}

            if clave == "tipo":
                es_numero = False
                try:
                    _ = float(valor)
                    es_numero = True
                except ValueError:
                    pass
                if es_numero:
                    raise ValueError(f"La clave '{clave}' no puede tener un valor numérico: '{valor}'")
                valor_minusculas = valor.lower()
                if valor_minusculas not in valores_validos_tipo:
                    raise ValueError(f"La clave '{clave}' no puede tener el valor '{valor}'. Debe ser uno de {valores_validos_tipo}")
                config_leida[clave] = valor_minusculas

            elif clave in ["xmax", "ymax"]:
                try:
                    valor_float = eval(valor, {"__builtins__": None}, safe_env_2)
                    if not isinstance(valor_float, (int, float)):
                        raise ValueError
                    if valor_float <= 0:
                        raise ValueError
                    config_leida[clave] = valor_float
                except Exception:
                    raise ValueError(f"La línea '{linea_original.strip()}' contiene un error, '{clave}' debe ser un número mayor que cero")

            elif clave in ["xr", "yd"]:
                try:
                    valor_entero = int(valor)
                    if valor_entero < 0:
                        raise ValueError
                    config_leida[clave] = valor_entero
                except Exception:
                    raise ValueError(f"La línea '{linea_original.strip()}' contiene un error, '{clave}' debe ser un entero mayor que 0")
            elif clave == "R":
                try:
                    valor_float = eval(valor, {"__builtins__": None}, safe_env_2)
                    if not isinstance(valor_float, (int, float)):
                        raise ValueError
                    if valor_float <= 0:
                        raise ValueError
                    
                    if "xmax" not in config_leida:
                        config_leida["xmax"] = defecto["xmax"]

                    if "ymax" not in config_leida:
                        config_leida["ymax"] = defecto["ymax"]
                    
                    if valor_float > min(config_leida["xmax"] / 2, config_leida["ymax"] / 2):
                        raise ValueError

                    config_leida["R"] = valor_float 

                except Exception:
                    raise ValueError(
                        f"La línea '{linea_original.strip()}' contiene un error: '{clave}' debe ser un número mayor que cero "
                        f"y menor que el mínimo entre {config_leida['xmax']/2} y {config_leida['ymax']/2}"
                    )


        fichero.close()


        config = defecto.copy()
        config.update(config_leida)
    except FileNotFoundError:
        config = defecto.copy()
        print(f"⚠️ Archivo '{archivo}' no encontrado. Usando valores por defecto.")
    
    return config

def crear_malla(xmax,ymax,xr,yd,R,tipo):
    if tipo == "uniforme":
        n_nodos = (xr+1)*(yd+1)

        n_elementos = 2*xr*yd
        
        NL = np.zeros([n_nodos, 2])

        deltax = xmax/xr

        deltay = ymax/yd

        n = 0 

        for i in range(yd+1):
            for j in range(0,xr+1):
                NL[n,0] = j*deltax 
                NL[n,1] = i*deltay 
                n+= 1

        EL = np.zeros([n_elementos, 3])

        e = 0

        for i in range(yd):
            for j in range(xr):
                n1 = i * (xr + 1) + j
                n2 = n1 + 1
                n3 = n1 + (xr + 1)
                n4 = n3 + 1

                EL[e, :] = [n1, n2, n4]
                e += 1

                EL[e, :] = [n1, n4, n3]
                e += 1

        EL = EL.astype(int)

    else:
        n_nodos = 2*(xr+1)*(yd+1) + 2*(xr-1)*(yd+1)

        n_elementos = 4*yd*xr 

        NL = np.zeros([n_nodos,2])

        deltax = xmax/xr

        deltay = ymax/xr

        region1 = np.zeros([(xr+1)*(yd+1), 2])

        for i in range(xr + 1):
            region1[i, 0] = i * deltax
            region1[i, 1] = 0
        for i in range(xr + 1):
            region1[yd * (xr + 1) + i, 0] = R * np.cos((5 * np.pi / 4) + i * ((np.pi / 2) / xr)) + xmax / 2
            region1[yd * (xr + 1) + i, 1] = R * np.sin((5 * np.pi / 4) + i * ((np.pi / 2) / xr)) + ymax / 2
        for i in range(yd-1):
            for j in range(xr + 1):
                dx = (region1[yd * (xr + 1) + j, 0] - region1[j, 0]) / yd
                dy = (region1[yd * (xr + 1) + j, 1] - region1[j, 1]) / yd
                region1[(i+1) * (xr + 1) + j, 0] = region1[i * (xr + 1) + j, 0] + dx
                region1[(i+1) * (xr + 1) + j, 1] = region1[i * (xr + 1) + j, 1] + dy

        region2 = np.zeros([(xr + 1) * (yd + 1), 2])
        for i in range(xr + 1):
            region2[i, 0] = i * deltax
            region2[i, 1] = ymax
        for i in range(xr + 1):
            region2[yd * (xr + 1) + i, 0] = R * np.cos((3 * np.pi / 4) - i * ((np.pi / 2) / xr)) + xmax / 2
            region2[yd * (xr + 1) + i, 1] = R * np.sin((3 * np.pi / 4) - i * ((np.pi / 2) / xr)) + ymax / 2
        for i in range(yd-1):
            for j in range(xr + 1):
                dx = (region2[yd * (xr + 1) + j, 0] - region2[j, 0]) / yd
                dy = (region2[yd * (xr + 1) + j, 1] - region2[j, 1]) / yd
                region2[(i+1) * (xr + 1) + j, 0] = region2[i * (xr + 1) + j, 0] + dx
                region2[(i+1) * (xr + 1) + j, 1] = region2[i * (xr + 1) + j, 1] + dy

        region3 = np.zeros([(xr - 1) * (yd + 1), 2])
        for i in range(xr-1):
            region3[i, 0] = 0
            region3[i, 1] = (i+1) * deltay
        for i in range(xr-1):
            region3[yd * (xr - 1) + i, 0] = R * np.cos((5 * np.pi / 4) - (i+1) * ((np.pi / 2) / xr)) + xmax / 2
            region3[yd * (xr - 1) + i, 1] = R * np.sin((5 * np.pi / 4) - (i+1) * ((np.pi / 2) / xr)) + ymax / 2
        for i in range(yd-1):
            for j in range(0, xr-1):
                dx = (region3[yd * (xr - 1) + j, 0] - region3[j, 0]) / yd
                dy = (region3[yd * (xr - 1) + j, 1] - region3[j, 1]) / yd
                region3[(i+1) * (xr - 1) + j, 0] = region3[i * (xr - 1) + j, 0] + dx
                region3[(i+1) * (xr - 1) + j, 1] = region3[i * (xr - 1) + j, 1] + dy

        region4 = np.zeros([(xr - 1) * (yd + 1), 2])
        for i in range(xr-1):
            region4[i, 0] = xmax
            region4[i, 1] = (i+1) * deltay
        for i in range(0, xr-1):
            region4[yd * (xr - 1) + i, 0] = R * np.cos((7 * np.pi / 4) + (i+1) * ((np.pi / 2) / xr)) + xmax / 2
            region4[yd * (xr - 1) + i, 1] = R * np.sin((7 * np.pi / 4) + (i+1) * ((np.pi / 2) / xr)) + ymax / 2
        for i in range(yd-1):
            for j in range(0, xr-1):
                dx = (region4[yd * (xr - 1) + j, 0] - region4[j, 0]) / yd
                dy = (region4[yd * (xr - 1) + j, 1] - region4[j, 1]) / yd
                region4[(i+1) * (xr - 1) + j, 0] = region4[i * (xr - 1) + j, 0] + dx
                region4[(i+1) * (xr - 1) + j, 1] = region4[i * (xr - 1) + j, 1] + dy

        for i in range(yd + 1):
            NL[i * 4 * xr:(i+1) * 4 * xr, :] = np.vstack([
                region1[i * (xr + 1):(i+1) * (xr + 1), :],
                region4[i * (xr - 1):(i+1) * (xr - 1), :],
                np.flipud(region2[i * (xr + 1):(i+1) * (xr + 1), :]),
                np.flipud(region3[i * (xr - 1):(i+1) * (xr - 1), :])
            ])

        EL_cuad = np.zeros([n_elementos, 4])
        for i in range(yd):
            for j in range(4 * xr):
                idx = i * (4 * xr) + j 
                if j == 0:
                    EL_cuad[idx, 0] = i * (4 * xr) + j
                    EL_cuad[idx, 1] = EL_cuad[idx, 0] + 1
                    EL_cuad[idx, 3] = EL_cuad[idx, 0] + 4 * xr
                    EL_cuad[idx, 2] = EL_cuad[idx, 3] + 1
                elif j == 4 * xr - 1:
                    EL_cuad[idx, 0] = (i+1) * (4 * xr) - 1
                    EL_cuad[idx, 1] = i * (4 * xr) 
                    EL_cuad[idx, 2] = EL_cuad[idx, 0] + 1
                    EL_cuad[idx, 3] = EL_cuad[idx, 0] + 4 * xr
                else:
                    EL_cuad[idx, 0] = EL_cuad[idx - 1, 1]
                    EL_cuad[idx, 3] = EL_cuad[idx - 1, 2]
                    EL_cuad[idx, 2] = EL_cuad[idx, 3] + 1
                    EL_cuad[idx, 1] = EL_cuad[idx, 0] + 1




        NoE_tri = 2 * n_elementos
        EL_tri = np.zeros([NoE_tri, 3], dtype=int)
        for i in range(n_elementos):
            EL_tri[2 * i, :] = [int(EL_cuad[i, 0]), int(EL_cuad[i, 1]), int(EL_cuad[i, 2])]
            EL_tri[2 * i + 1, :] = [int(EL_cuad[i, 0]), int(EL_cuad[i, 2]), int(EL_cuad[i, 3])]

        EL = EL_tri

    EL = EL.astype(int)

    return (NL,EL)

        
      
def graficar_malla(NL, EL):
    n_nodos = NL.shape[0]
    n_elementos = EL.shape[0]

    plt.figure(figsize=(8, 6))
    plt.axis("equal")

    for j in range(n_elementos):
        x = [NL[EL[j, 0], 0], NL[EL[j, 1], 0], NL[EL[j, 2], 0], NL[EL[j, 0], 0]]
        y = [NL[EL[j, 0], 1], NL[EL[j, 1], 1], NL[EL[j, 2], 1], NL[EL[j, 0], 1]]
        plt.plot(x, y, 'darkorange', linewidth=1)

    for i in range(n_nodos):
        plt.annotate(str(i), xy=(NL[i,0], NL[i,1]), fontsize=8, ha='right', va='bottom')
        plt.plot(NL[i, 0], NL[i, 1], 'ko', markersize=3)

    for j in range(n_elementos):
        cx = (NL[EL[j, 0], 0] + NL[EL[j, 1], 0] + NL[EL[j, 2], 0]) / 3
        cy = (NL[EL[j, 0], 1] + NL[EL[j, 1], 1] + NL[EL[j, 2], 1]) / 3
        desplazamiento_texto = 0.015  
        cx -= desplazamiento_texto

        plt.annotate(str(j), xy=(cx, cy), color='darkcyan', fontsize=8)

    plt.title("Malla generada")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()



        
        
config = leer_configuracion('especificaciones_malla.txt',parametros_por_defecto)

NL, EL = crear_malla(config["xmax"], config["ymax"], config["xr"], config["yd"], config["R"], config["tipo"])

graficar_malla(NL, EL)

np.savetxt("nodos.txt", NL, fmt="%.6f", delimiter=",", header="x, y", comments='')

np.savetxt("elementos.txt", EL, fmt="%d", delimiter=",", header="nodo1, nodo2, nodo3", comments='')

  





        
