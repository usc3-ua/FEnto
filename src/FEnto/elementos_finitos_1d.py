
# Método de elementos finitos 1D

import numpy as np

import matplotlib.pyplot as plt

parametros_por_defecto = {
    "xmax": 1,
    "n_nodos":101,
    "tamano_longitudes": "uniforme", 
    "longitudes_elementos": None,
    "alpha": "x**3+x",
    "beta": "5*x",
    "f": "-89*x**3-95*x**5+18*x**2+38*x-9",
    "tipo_condicion_0": "robin",
    "tipo_condicion_L": "dirichlet",
    "valor_dirichlet_0": None,       
    "valor_dirichlet_L": 27,       
    "gamma_robin_0": 1,         
    "q_robin_0": 10,
    "gamma_robin_L": None,         
    "q_robin_L": None
}

def leer_configuracion(archivo, defecto):
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
            
            valores_validos_tamano_longitudes = {"personalizado", "uniforme"}
            valores_validos_tipo_condicion = {"dirichlet", "robin"}

            if clave == "xmax":
                try:
                    valor_float = float(valor)
                    if valor_float <= 0:
                        raise ValueError
                    config_leida[clave] = valor_float
                except Exception:
                    raise ValueError(f"La línea '{linea_original.strip()}' contiene un error, xmax debe ser un número mayor que cero")

            elif clave == "n_nodos":
                try:
                    valor_entero = int(valor)
                    if valor_entero < 2:
                        raise ValueError
                    config_leida[clave] = valor_entero
                except Exception:
                    raise ValueError(f"La línea '{linea_original.strip()}' contiene un error, n_nodos debe ser un entero mayor que 2")
                
            elif clave == "tamano_longitudes":
                    es_numero = False
                    try:
                        _ = float(valor)
                        es_numero = True
                    except ValueError:
                        pass
                    if es_numero:
                        raise ValueError(f"La clave '{clave}' no puede tener un valor numérico: '{valor}'")
                    valor_minusculas = valor.lower()
                    if valor_minusculas not in valores_validos_tamano_longitudes:
                        raise ValueError(f"La clave '{clave}' no puede tener el valor '{valor}'. Debe ser uno de {valores_validos_tamano_longitudes}")
                    config_leida[clave] = valor_minusculas

            elif clave == "longitudes_elementos":
                try:
                    valores = [float(v.strip()) for v in valor.split(",")]
                    if not all(v > 0 for v in valores):
                        raise ValueError("Todos los valores en 'longitudes_elementos' deben ser positivos.")
                    if "n_nodos" not in config_leida:
                        config_leida["n_nodos"] = defecto["n_nodos"]
                    if len(valores) != config_leida["n_nodos"] - 1:
                        raise ValueError(f"Se esperaban {config_leida['n_nodos'] - 1} longitudes, pero se encontraron {len(valores)}.")
                    if "xmax" not in config_leida:
                        config_leida["xmax"] = defecto["xmax"]
                    suma = sum(valores)
                    if abs(suma - config_leida["xmax"]) > 1e-8:  
                        raise ValueError(f"La suma de 'longitudes_elementos' ({suma}) no coincide con xmax ({config_leida['xmax']}).")
                    config_leida[clave] = valores
                except ValueError as e:
                    raise ValueError(f"Error en 'longitudes_elementos': {e}") from None

            elif clave in ["alpha", "beta", "f"]:
                try:
                    x = 1
                    eval(valor, {"x": x, "__builtins__": {}})
                    config_leida[clave] = valor
                except Exception as e:
                    raise ValueError(f"La expresión de {clave} no es válida: {e}") from None
                    
            elif clave in ["tipo_condicion_0","tipo_condicion_L"]:
                es_numero = False
                try:
                    _ = float(valor)
                    es_numero = True
                except ValueError:
                    pass
                if es_numero:
                    raise ValueError(f"La clave '{clave}' no puede tener un valor numérico: '{valor}'")
                valor_minusculas = valor.lower()
                if valor_minusculas not in valores_validos_tipo_condicion:
                    raise ValueError(f"La clave '{clave}' no puede tener el valor '{valor}'. Debe ser uno de {valores_validos_tipo_condicion} (Neumann es un caso particular de Robin)")
                config_leida[clave] = valor_minusculas

            elif clave in ["valor_dirichlet_0", "valor_dirichlet_L", "gamma_robin_0", "gamma_robin_L", "q_robin_0", "q_robin_L"]:
                try:
                    config_leida[clave] = float(valor)
                except Exception as e:
                    raise ValueError(f"La línea '{linea_original.strip()}' contiene un error, {clave} debe ser un número")
                
            
        fichero.close()

        if "tamano_longitudes" in config_leida:
            tipo = config_leida["tamano_longitudes"]
            if tipo == "personalizado":
                if "longitudes_elementos" not in config_leida:
                    raise ValueError("Se ha especificado 'tamano_longitudes = personalizado', pero falta 'longitudes_elementos' en el archivo de configuración.")
    
        if "tipo_condicion_0" in config_leida:
            tipo = config_leida["tipo_condicion_0"]
            if tipo == "dirichlet":
                if "valor_dirichlet_0" not in config_leida:
                    raise ValueError("Se ha especificado 'tipo_condicion_0 = dirichlet', pero falta 'valor_dirichlet_0' en el archivo de configuración.")
            elif tipo == "robin":
                faltantes = []
                if "gamma_robin_0" not in config_leida:
                    faltantes.append("gamma_robin_0")
                if "q_robin_0" not in config_leida:
                    faltantes.append("q_robin_0")
                if faltantes:
                    raise ValueError(f"Se ha especificado 'tipo_condicion_0 = robin', pero faltan los siguientes parámetros en el archivo de configuración: {', '.join(faltantes)}")

    
        if "tipo_condicion_L" in config_leida:
            tipo = config_leida["tipo_condicion_L"]
            if tipo == "dirichlet":
                if "valor_dirichlet_L" not in config_leida:
                    raise ValueError("Se ha especificado 'tipo_condicion_L = dirichlet', pero falta 'valor_dirichlet_L' en el archivo de configuración.")
            elif tipo == "robin":
                faltantes = []
                if "gamma_robin_L" not in config_leida:
                    faltantes.append("gamma_robin_L")
                if "q_robin_L" not in config_leida:
                    faltantes.append("q_robin_L")
                if faltantes:
                    raise ValueError(f"Se ha especificado 'tipo_condicion_L = robin', pero faltan los siguientes parámetros en el archivo de configuración: {', '.join(faltantes)}")

        config = defecto.copy()
        config.update(config_leida)
       
    except FileNotFoundError:
        config = defecto.copy()
        print(f"⚠️ Archivo '{archivo}' no encontrado. Usando valores por defecto.")
    return config
        

def Dirichlet(xmax, n_nodos, tamano_longitudes, longitudes_elementos, alpha, beta, f, tipo_condicion_0, tipo_condicion_L, valor_dirichlet_0, valor_dirichlet_L, gamma_robin_0, q_robin_0, gamma_robin_L, q_robin_L):
    n_elementos = n_nodos - 1 

    if tamano_longitudes == "personalizado":
        x_coords = np.zeros(n_nodos)
        x_coords[0] = 0
        for i in range(1, n_nodos):
            x_coords[i] = x_coords[i-1] + longitudes_elementos[i-1]

    else:
        x_coords = np.linspace(0,xmax,n_nodos)
        longitudes_elementos = np.ones(n_elementos)*(x_coords[1]-x_coords[0])

    ptosmedios_elementos = np.zeros(n_elementos)

    for i in range(0, n_elementos):
        ptosmedios_elementos[i] = (x_coords[i]+x_coords[i+1])/2

    K = np.zeros((n_nodos, n_nodos))

    b = np.zeros(n_nodos)

    valoresalpha = np.zeros(n_elementos)

    for j in range(0,n_elementos):
        x = ptosmedios_elementos[j]
        valoresalpha[j] = eval(alpha)

    valoresbeta = np.zeros(n_elementos)

    for k in range(0,n_elementos):
        x = ptosmedios_elementos[k]
        valoresbeta[k] = eval(beta)

    K[0,0] = valoresalpha[0]/longitudes_elementos[0] + valoresbeta[0]*longitudes_elementos[0]/3

    K[n_nodos-1, n_nodos-1] = valoresalpha[n_elementos-1]/longitudes_elementos[n_elementos-1] + valoresbeta[n_elementos-1]*longitudes_elementos[n_elementos-1]/3

    for l in range(0, n_nodos-1):
        K[l+1,l] = - valoresalpha[l]/longitudes_elementos[l] + valoresbeta[l]*longitudes_elementos[l]/6

        K[l,l+1] = K[l+1,l]

    for m in range(1, n_nodos-1):
        K[m,m] = valoresalpha[m-1]/longitudes_elementos[m-1] + valoresbeta[m-1]*longitudes_elementos[m-1]/3 + valoresalpha[m]/longitudes_elementos[m]  + valoresbeta[m]*longitudes_elementos[m]/3

    for n in range(n_nodos):
        if n == 0:
            x = ptosmedios_elementos[0]
            b[n] = eval(f) * longitudes_elementos[0] / 2
        elif n == n_nodos - 1:
            x = ptosmedios_elementos[n_elementos-1]
            b[n] = eval(f) * longitudes_elementos[n_elementos-1] / 2
        else:
            x1 = ptosmedios_elementos[n]
            x2 = ptosmedios_elementos[n - 1]
            b1 = eval(f, {"x": x1}) * longitudes_elementos[n] / 2
            b2 = eval(f, {"x": x2}) * longitudes_elementos[n - 1] / 2
            b[n] = b1 + b2
            

    if tipo_condicion_0 == "dirichlet":
        K[0,:] = np.zeros(n_nodos) 
        K[0,0] = 1 
        b[0] = valor_dirichlet_0

    else:
        K[0, 0] += gamma_robin_0
        b[0] += q_robin_0


    if tipo_condicion_L == "robin":
        K[n_nodos-1, n_nodos-1] += gamma_robin_L
        b[n_nodos-1] += q_robin_L

    else:
        K[n_nodos-1,:] = np.zeros(n_nodos) 
        K[n_nodos-1,n_nodos-1] = 1 
        b[n_nodos-1] = valor_dirichlet_L

    
    return K,b,x_coords

config = leer_configuracion("configuracion1d.txt", parametros_por_defecto)

K, b, nodos = Dirichlet(config["xmax"], config["n_nodos"], config["tamano_longitudes"], config["longitudes_elementos"], config["alpha"], config["beta"], config["f"], config["tipo_condicion_0"], config["tipo_condicion_L"], config["valor_dirichlet_0"], config["valor_dirichlet_L"], config["gamma_robin_0"], config["q_robin_0"], config["gamma_robin_L"], config["q_robin_L"])

phi = np.linalg.solve(K, b)

print("Solución MEF en los nodos:")
for i in range(len(nodos)):
    print(f"ϕ({nodos[i]:.2f}) = {phi[i]:.4f}")


plt.figure(figsize=(8,5))
plt.plot(nodos, phi, marker='o', linestyle='-', color='darkcyan')
plt.title('Solución mediante el método de Elementos Finitos')
plt.xlabel('x')
plt.ylabel('ϕ(x)')
plt.show()





    

    
    
