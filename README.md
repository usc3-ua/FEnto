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

# Contenido

Este paquete permite resolver ecuaciones tanto unidimensionales como bidimensionales usando el método de elementos finitos.

Las ecuaciones en 1D que se admiten tienen la forma siguiente:

donde φ es la función desconocida, α y β son parámetros conocidos o funciones asociadas con las propiedades físicas del dominio de la solución, y *f* es la función de excitación o fuente.




pueden especificarse como funciones de *x* o constantes.





