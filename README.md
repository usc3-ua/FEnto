<div align="center">
  <img src="imágenes/Fento2.png" alt="Logo" width="350" />
</div>

<br>

Paquete que permite resolver ecuaciones en derivadas parciales usando el método de elementos finitos.

# Instalación

Es suficiente con ejecutar en consola el comando siguiente:

```bash
python -m pip install git+https://github.com/usc3-ua/FEnto.git
```
donde 'python' es un alias para python3.

Sin embargo, es recomendable crear y activar previamente un entorno virtual:

```bash
python3− m venv env
source env/bin/activate
```

donde env es el nombre del entorno.

# Contenido y uso

Este paquete permite resolver ecuaciones tanto unidimensionales como bidimensionales usando el método de elementos finitos.

Las ecuaciones en 1D que se admiten tienen la forma siguiente:

<div align="center">
  <img src="imágenes/ecuacion1d.jpeg" width="270" />
</div>

donde φ es la función desconocida, α y β son parámetros conocidos o funciones asociadas con las propiedades físicas del dominio de la solución, y *f* es la función de excitación o fuente. 

Para hacer uso del programa que permite resolver la ecuación anterior se debe crear un fichero de texto de nombre configuracion.txt que contenga las especificaciones del problema que se pretende resolver. En primer lugar, se proporcionan expresiones para α, β  y *f* con lenguaje matemático de python, pueden escogerse funciones de *x* o constantes.

Como condiciones de contorno se pueden usar tanto de Dirichlet como de Robin o de Neumann. Por ejemplo, si se escoge condición de contorno de Dirichlet en x = 0 se tiene:

<div align="center">
  <img src="imágenes/dirichlet1d.jpeg" width="80" />
</div>

Entonces en el fichero de configuración habrá que especificar el tipo de condición que se usa y el valor específico de *p* que se quiere usar:

```
tipo_condicion_0 = Dirichlet

valor_dirichlet_0 = 10
```


<div align="center">
  <img src="imágenes/robin1d.jpeg" width="150" />
</div>








