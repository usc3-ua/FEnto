<div align="center">
  <img src="imágenes/Fento2.png" alt="Logo" width="350" />
</div>

<br>

Paquete que permite resolver ecuaciones en derivadas parciales unidimensionales y bidimensionales usando el método de elementos finitos.

# Instalación

Es suficiente con ejecutar en consola lo siguiente:

```bash
python3− m venv env
source env/bin/activate
python -m pip install git+https://github.com/usc3-ua/FEnto.git
```
donde los dos primeros comandos crean y activan un entorno virtual de nombre 'env'. Este paso no es estrictamente necesario pero sí recomendable, pues permite aislar las dependencias del proyecto y evitar conflictos con otras instalaciones del sistema.

# Programa 1D

El programa de nombre `elementos_finitos_1d.py` permite resolver ecuaciones diferenciales unidimensionales con la forma siguiente:

<div align="center">
  <img src="imágenes/ecuacion1d.jpeg" width="270" />
</div>

utilizando el método de elementos finitos. Para poder utilizarlo, es necesario crear un archivo de configuración denominado `configuracion.txt` que contenga las especificaciones concretas del problema que se pretenda resolver. Se seguirá la notación `clave = valor` para especificar los valores de las variables.

En primer lugar es necesario definir el límite superior del dominio L, denotado como xmax, que debe ser un número positivo. Además, se especifica el número de nodos (n_nodos) que se van a utilizar para la resolución, que debe ser un valor entero y mayor que dos. Esto se debe a que los elementos que se usan en el programa son elementos lineales y, en consecuencia, si se tienen n_nodos se tendrán (n_nodos-1) elementos (y el menor número de elementos que se puede tener para resolver un problema es uno).

```
xmax = 1

n_nodos = 21
```

Una vez hecho esto, hay que indicar cómo se quiere que sea el tamaño de los elementos. Para eso se usa la variable `tamano_longitudes`, que tiene dos valores posibles: `uniforme` o `personalizado`. Si se escoge `uniforme` el programa va a dividir el dominio de forma que se generen elementos de igual tamaño. Si se escoge `personalizado` será obligatorio definir otra variable de nombre `longitudes_elementos` en la cual se especificarán las longitudes de cada uno de los elementos como números positivos separados por comas. No será necesario especificar `longitudes_elementos` en el caso de escoger `tamano_longitudes = uniforme`. Para el caso personalizado se podría tener lo siguiente:

```
tamano_longitudes = personalizado

longitudes_elementos = 0.05,0.05,0.06,0.04,0.03,0.07,0.05,0.05,0.02,0.08,0.05,0.05,0.06,0.04,0.07,0.03,0.08,0.02,0.05,0.05
```

A continuación, se definen α, β y *f* como funciones de x o valores constantes con lenguaje matemático de python.

```
alpha = x**3+x

beta = 5*x

f = -89*x**3-95*x**5+18*x**2+38*x-9
```

Se podrán aplicar condiciones de contorno tanto de Dirichlet como de Robin o de Neumann en ambos extremos del dominio. Por ejemplo, si se escoge condición de contorno de Dirichlet en x = 0 se tiene:

<div align="center">
  <img src="imágenes/dirichlet1d.jpeg" width="80" />
</div>

Entonces en el fichero de configuración habrá que especificar el tipo de condición que se usa en `tipo_condicion_0` y obligatoriamente el valor específico de *p* que se quiere en `valor_dirichlet_0`.

```
tipo_condicion_0 = Dirichlet

valor_dirichlet_0 = 10
```

Si se quieren usar condiciones de contorno de Robin en *x=L* se tiene lo siguiente:

<div align="center">
  <img src="imágenes/robin1d.jpeg" width="150" />
</div>

entonces habrá que especificar el tipo de condición en `tipo_condicion_L`, el valor de γ en `gamma_robin_L` y el valor de *q* en `q_robin_L`:

```
tipo_condicion_L = robin

gamma_robin_L = -1

q_robin_L = 43
```

Obviamente, podrían aplicarse también condiciones de Robin en x=0 y condiciones de Dirichlet en x=L, únicamente habría que especficarlo de la misma forma que se ha mostrado pero intercambiando L por 0 y viceversa en el nombre de las variables. Para poder aplicar condiciones de Neumann basta con escoger γ=0 en las condiciones de Robin.









