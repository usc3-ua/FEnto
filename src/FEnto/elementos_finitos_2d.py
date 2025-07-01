
# Método de elementos finitos 2D

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

NL = np.loadtxt('nodos.txt', delimiter = ',', skiprows = 1)

EL = np.loadtxt('elementos.txt', delimiter = ',', skiprows = 1, dtype = int)

N = np.shape(NL)[0]

x = np.zeros(N)
y = np.zeros(N)

for i in range(N):
    x[i] = NL[i,0]
    y[i] = NL[i,1]

M = np.shape(EL)[0]

parametros_por_defecto = {
    "alpha_x": "1+x",
    "alpha_y": "exp(y)",
    "beta": "cos(y)",
    "f": "-1.0-0.1*exp(y)*cos(0.1*y)+0.01*exp(y)*sin(0.1*y)+cos(y)*(x+sin(0.1*y))",
    "gamma_1": "bordeizquierdo+bordederecho+bordesuperior+bordeinferior",
    "p": [0.0, 0.1, 0.2, 0.3, 0.4,0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.009999833334166666,\
          1.0099998333341667, 0.019998666693333084, 1.0199986666933332, 0.02999550020249566,\
          1.0299955002024956, 0.03998933418663417, 1.0399893341866342, 0.04997916927067833,\
          1.0499791692706784, 0.059964006479444595, 1.0599640064794447, 0.06994284733753275,\
          1.0699428473375328, 0.07991469396917271, 1.0799146939691726, 0.08987854919801105,\
          1.089878549198011, 0.09983341664682815, 0.19983341664682816, 0.29983341664682817,\
          0.39983341664682814, 0.4998334166468282, 0.5998334166468282, 0.6998334166468281,\
          0.7998334166468282, 0.8998334166468283, 0.9998334166468281, 1.0998334166468282],
    "gamma": [],
    "q": []
}


safe_env_2 = {"pi": np.pi, "e": np.e}

def identificacion_malla(elementos):
    from collections import Counter

    def segmentos_elementos(elementos):
        segmentos = []

        for tri in elementos:
            segmentos.append(tuple(sorted((tri[0], tri[1]))))
            segmentos.append(tuple(sorted((tri[1], tri[2]))))
            segmentos.append(tuple(sorted((tri[2], tri[0]))))
        return segmentos

    segmentos = segmentos_elementos(EL)

    segmentos_cuenta = Counter(segmentos)

    segmentos_bordes = [segmento for segmento, cuenta in segmentos_cuenta.items() if cuenta == 1]
   
    Lx_min = np.min(x)
    Ly_min = np.min(y)
    Lx_max = np.max(x)
    Ly_max = np.max(y)

    segmentos_agujero = []
    for segmento in segmentos_bordes:
        n1, n2 = segmento
        if not (
            np.isclose(x[n1], Lx_min) or np.isclose(x[n1], Lx_max) or np.isclose(y[n1], Ly_min) or np.isclose(y[n1], Ly_max) or
            np.isclose(x[n2], Lx_min) or np.isclose(x[n2], Lx_max) or np.isclose(y[n2], Ly_min) or np.isclose(y[n2], Ly_max)
        ):
            segmentos_agujero.append(segmento)

    longitud_agujero = len(segmentos_agujero)

    nodos_agujero = list(set([nodo for segmento in segmentos_agujero for nodo in segmento]))

    return segmentos_bordes, Lx_min, Ly_min, Lx_max, Ly_max, longitud_agujero, nodos_agujero

    



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

            import itertools

            _, _, _, _, _, longitud_agujero, _ = identificacion_malla(EL)

            bordes = ["bordeizquierdo", "bordederecho", "bordesuperior", "bordeinferior"]

            if longitud_agujero > 1:
                bordes.append("interior")
                
            valores_validos_gamma_1 = set()

            for k in range(0, len(bordes) + 1):
                for comb in itertools.combinations(bordes, k):
                    valores_validos_gamma_1.add("+".join(comb))

            if clave in ["alpha_x", "alpha_y", "beta", "f"]:
                try:
                    compile(valor, "<string>", "eval")
                    config_leida[clave] = valor
                except Exception as e:
                    raise ValueError(f"La expresión de '{clave}' no es válida: {e}") from None

            elif clave == "gamma_1":
                es_numero = False
                try:
                    _ = float(valor)
                    es_numero = True
                except ValueError:
                    pass
                if es_numero:
                    raise ValueError(f"La clave '{clave}' no puede tener un valor numérico: '{valor}'")
                valor_minusculas = valor.lower()
                valor_sin_espacios = valor_minusculas.replace(" ", "")

                if valor_sin_espacios not in valores_validos_gamma_1:
                    raise ValueError(f"La clave '{clave}' no puede tener el valor '{valor}'. Debe ser uno de {valores_validos_gamma_1}")
                config_leida[clave] = valor_sin_espacios

            elif clave == "p":
                try:
                    valores = [eval(v.strip(),{"__builtins__": None}, safe_env_2) for v in valor.split(",")]

                    if "gamma_1" not in config_leida:
                        config_leida["gamma_1"] = defecto["gamma_1"]

                    Nd, _, _, _, _ =  aplicacion_condiciones(x,y, config_leida["gamma_1"])
                    
                    if len(valores) != Nd:
                        raise ValueError(f"La clave '{clave}' no tiene la longitud adecuada tiene {len(valores)} elementos en lugar de {Nd}")

                    config_leida[clave] = valores
                    
                except ValueError as e:
                    raise ValueError(f"Error en '{clave}': {e}") from None

            elif clave in ["q", "gamma"]:
                try:
                    valores = [eval(v.strip(),{"__builtins__": None}, safe_env_2) for v in valor.split(",")]

                    if "gamma_1" not in config_leida:
                        config_leida["gamma_1"] = defecto["gamma_1"]

                    _, _, _, Ms, _ = aplicacion_condiciones(x,y, config_leida["gamma_1"])
                    
                    if len(valores) != Ms:
                        raise ValueError(f"La clave '{clave}' no tiene la longitud adecuada tiene {len(valores)} elementos en lugar de {Ms}")

                    config_leida[clave] = valores
                except ValueError as e:
                    raise ValueError(f"Error en '{clave}': {e}") from None

        fichero.close()
        
        if "gamma_1" in config_leida:
            gamma_1_valor = config_leida.get("gamma_1", "")

            if longitud_agujero == 0:
                if gamma_1_valor == "bordeizquierdo+bordederecho+bordesuperior+bordeinferior":
                    if "p" not in config_leida:
                        raise ValueError("Cuando 'gamma_1' es 'borde izquierdo + borde derecho + borde superior + borde inferior', el parámetro 'p' debe estar definido.")
                if gamma_1_valor == "":
                    faltantes = [k for k in ("gamma", "q") if k not in config_leida]
                    if faltantes:
                        raise ValueError(f"Cuando 'gamma_1' está vacía los siguientes parámetros deben estar definidos: {faltantes}")
                else:
                    faltantes = [k for k in ("p", "gamma", "q") if k not in config_leida]
                    if faltantes:
                        raise ValueError(
                            f"Cuando 'gamma_1' es '{gamma_1_valor}', los siguientes parámetros deben estar definidos: {faltantes}")
            else:
                if gamma_1_valor == "bordeizquierdo+bordederecho+bordesuperior+bordeinferior+interior":
                    if "p" not in config_leida:
                        raise ValueError("Cuando 'gamma_1' es 'borde izquierdo + borde derecho + borde superior + borde inferior + interior', el parámetro 'p' debe estar definido.")
                if gamma_1_valor == "":
                    faltantes = [k for k in ("gamma", "q") if k not in config_leida]
                    if faltantes:
                        raise ValueError(f"Cuando 'gamma_1' está vacía los siguientes parámetros deben estar definidos: {faltantes}")
                else:
                    faltantes = [k for k in ("p", "gamma", "q") if k not in config_leida]
                    if faltantes:
                        raise ValueError(
                            f"Cuando 'gamma_1' es '{gamma_1_valor}', los siguientes parámetros deben estar definidos: {faltantes}")

                


        config = defecto.copy()
        config.update(config_leida)
    except FileNotFoundError:


        config = defecto.copy()
        config.update(config_leida)
    except FileNotFoundError:
        config = defecto.copy()
        print(f"⚠️ Archivo '{archivo}' no encontrado. Usando valores por defecto.")
    
    return config




def aplicacion_condiciones(x,y,gamma_1):
    nodos_gamma = []
    
    segmentos_bordes, Lx_min, Ly_min, Lx_max, Ly_max, longitud_agujero, nodos_agujero = identificacion_malla(EL)

    for i in range(N):
        if (np.isclose(x[i], Lx_min) or
            np.isclose(x[i], Lx_max) or
            np.isclose(y[i], Ly_min) or
            np.isclose(y[i], Ly_max)):
            nodos_gamma.append(i)

    nd = []

    if gamma_1 == "bordeizquierdo":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
    elif gamma_1 == "bordederecho":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
    elif gamma_1 == "bordeinferior":
        for i in range(N):
            if np.isclose(y[i], Ly_min):
                nd.append(i)
    elif gamma_1 == "bordesuperior":
        for i in range(N):
            if np.isclose(y[i], Ly_max):
                nd.append(i)
    elif gamma_1 == "bordesuperior+borde inferior":
        for i in range(N):
            if np.isclose(y[i], Ly_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordederecho":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(x[i], Lx_max):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordederecho+bordesuperior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordesuperior+bordeinferior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
    elif gamma_1 == "bordederecho+bordesuperior+bordeinferior":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordesuperior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordeinferior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordederecho+bordeinferior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(x[i], Lx_min):
                nd.append(i)
    elif gamma_1 == "bordederecho+bordesuperior":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
    elif gamma_1 == "bordeizquierdo+bordederecho+bordesuperior+bordeinferior":
        nd = nodos_gamma
    elif gamma_1 == "bordederecho+bordeinferior":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
    elif gamma_1 == "interior":
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordesuperior+bordeinferior+interior":
        for i in range(N):
            if np.isclose(y[i], Ly_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordeizquierdo+bordederecho+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(x[i], Lx_max):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordeizquierdo+bordederecho+bordesuperior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordeizquierdo+bordesuperior+bordeinferior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordederecho+bordesuperior+bordeinferior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 ==  "bordeizquierdo+bordesuperior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordeizquierdo+bordeinferior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordeizquierdo+bordederecho+bordeinferior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_min):
                nd.append(i)
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(x[i], Lx_min):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordederecho+bordesuperior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_max):
                nd.append(i)
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordeizquierdo+bordederecho+bordesuperior+bordeinferior+interior":
        nd = nodos_gamma
        nd.extend(nodos_agujero)
    elif gamma_1 == "bordederecho+bordeinferior+interior":
        for i in range(N):
            if np.isclose(x[i], Lx_max):
                nd.append(i)
            if np.isclose(y[i], Ly_min):
                nd.append(i)
        nd.extend(nodos_agujero)
    else:
        nd = []



    Nd = len(nd) 

    gamma_2 = list(set(nodos_gamma) - set(nd)) 

    segmentos_gamma_2 = [segmento for segmento in segmentos_bordes if not (segmento[0] in nd and segmento[1] in nd)]

    Ms = len(segmentos_gamma_2) 

    return Nd, nd, gamma_2, Ms, segmentos_gamma_2



safe_env = {
    "x": 1,
    "y": 1,
    "cos": np.cos,
    "sin": np.sin,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "pi": np.pi
}


def elementos_finitos(alpha_x, alpha_y, beta, f, p, gamma, q):
    
    valores_alpha_x = np.zeros(M)
    valores_alpha_y = np.zeros(M)
    valores_beta = np.zeros(M)
    valores_f = np.zeros(M)
    n = np.zeros((3,M))

    for e in range(0,M):
        nodos_por_elemento = EL[e]
        x_nodos = x[nodos_por_elemento]
        y_nodos = y[nodos_por_elemento]
        x_c = np.mean(x_nodos)
        y_c = np.mean(y_nodos)
        safe_env["x"] = x_c
        safe_env["y"] = y_c
      
        valores_alpha_x[e] = eval(alpha_x, {"__builtins__": {}}, safe_env)
        valores_alpha_y[e] = eval(alpha_y, {"__builtins__": {}}, safe_env)
        valores_beta[e] = eval(beta, {"__builtins__": {}}, safe_env)
        valores_f[e] = eval(f, {"__builtins__": {}}, safe_env)

        for i in range(0,3):
            n[i,e] = nodos_por_elemento[i]

    K = np.zeros((N,N))
    b = np.zeros(N)

    for e in range(0,M):
        K_e = np.zeros((3,3))
        b_e = np.zeros(3)
        c_e = np.zeros(3)

        ni = int(n[0,e]) 
        nj = int(n[1,e]) 
        nm = int(n[2,e]) 

        b_e[0] = y[nj] - y[nm] 
        b_e[1] = y[nm] - y[ni] 
        b_e[2] = y[ni] - y[nj] 
        c_e[0] = x[nm] - x[nj] 
        c_e[1] = x[ni] - x[nm] 
        c_e[2] = x[nj] - x[ni]

        delta_e = 1/2*(b_e[0]*c_e[1]-b_e[1]*c_e[0])

        for i in range(0,3):
            for j in range(0,3):
                if i==j:
                    delta_Kronecker = 1
                else:
                    delta_Kronecker = 0

                K_e[i,j] = 1/(4*delta_e)*(valores_alpha_x[e]*b_e[i]*b_e[j] + \
                            valores_alpha_y[e]*c_e[i]*c_e[j]) + \
                            delta_e/12*valores_beta[e]*(1+delta_Kronecker)

                K[int(n[i,e]), int(n[j,e])] = K[int(n[i,e]), int(n[j,e])] + K_e[i,j]


             
        b_el = np.zeros(3)
        for k in range(0,3):
            b_el[k] = valores_f[e]*delta_e/3 

            b[int(n[k,e])] = b[int(n[k,e])] + b_el[k]


    Nd, nd, gamma_2, Ms, segmentos_gamma_2 = aplicacion_condiciones(x,y,config["gamma_1"])

    l = np.zeros(Ms)

    ns = np.zeros((2,Ms))
    
    for s in range(0,Ms):
      for i in range(0,2):
        ns[i,s] = segmentos_gamma_2[s][i]


    for s in range(0,Ms):
      ni = int(ns[0,s]) 
      nj = int(ns[1,s]) 
      l[s] = np.sqrt((x[ni]-x[nj])**2 + (y[ni]-y[nj])**2) 
      K_s = np.zeros((2,2))

      for i in range(0,2):
        for j in range(0,2):
          if i == j:
            delta_Kronecker = 1
          else:
            delta_Kronecker = 0
          K_s[i,j] = gamma[s]*l[s]/6*(1+delta_Kronecker) 
          
          K[int(ns[i,s]), int(ns[j,s])] = K[int(ns[i,s]), int(ns[j,s])] + K_s[i,j]


      b_s = np.zeros(2)
      for k in range(0,2):
          b_s[k] = q[s]*l[s]/2 

          b[int(ns[k,s])] = b[int(ns[k,s])] + b_s[k]

    
    for i in range(0,Nd): 
      for j in range(0,N): 
        if j == nd[i]: 
          K[j,j] = 1
          b[j] = p[i]
        else:
          K[nd[i],j] = 0

        if j not in nd:
            b[j] = b[j] - K[j,nd[i]]*p[i]
            K[j,nd[i]] = 0


    return K,b


config = leer_configuracion("configuracion2d.txt", parametros_por_defecto)

K,b = elementos_finitos(config["alpha_x"], config["alpha_y"], config["beta"], config["f"], config["p"], config["gamma"], config["q"])

phi = np.linalg.solve(K,b)

fig = plt.figure()
ax = fig.add_subplot(projection='3d') 

surf = ax.plot_trisurf(x, y, phi, cmap='viridis')

ax.set_title("Solución Numérica φ")
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('φ')

plt.show()



      

            
    
