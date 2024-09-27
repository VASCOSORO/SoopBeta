import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# Cargar el archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel('1083.xlsx', engine='openpyxl')  # Cargar el archivo Excel
    return df

# Función para cargar la imagen desde una URL
def cargar_imagen(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# Función para cambiar el color del stock
def obtener_color_stock(stock):
    if stock > 5:
        return 'green'
    elif stock < 0:
        return 'red'
    elif stock < 3:
        return 'orange'
    else:
        return 'black'

# Mostrar producto en formato completo (con imagen)
def mostrar_producto_completo(producto):
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size: 28px; font-weight: bold;'>Código: {producto['Codigo']} | Precio: ${producto['Precio']} | Stock: {producto['Stock']}</span>", unsafe_allow_html=True)

    imagen_url = producto.get('imagen', '')
    if imagen_url:
        imagen = cargar_imagen(imagen_url)
        if imagen:
            st.image(imagen, use_column_width=True)
        else:
            st.write("Imagen no disponible.")

    # Mostrar descripción debajo de la imagen
    st.markdown(f"<p style='font-size: 26px;'>Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}</p>", unsafe_allow_html=True)
    
    # Mostrar categorías debajo de la descripción
    st.write(f"<p style='font-size: 24px;'>Categorías: {producto['Categorias']}</p>", unsafe_allow_html=True)

    # Checkbox para mostrar ubicación
    if st.checkbox('Mostrar Ubicación'):
        st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

# Mostrar productos en formato de lista con imágenes (paginar resultados)
def mostrar_lista_productos(df, pagina, productos_por_pagina=10):
    inicio = (pagina - 1) * productos_por_pagina
    fin = inicio + productos_por_pagina
    productos_pagina = df.iloc[inicio:fin]

    for i, producto in productos_pagina.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            imagen_url = producto.get('imagen', '')
            if imagen_url:
                imagen = cargar_imagen(imagen_url)
                if imagen:
                    st.image(imagen, width=140)
                else:
                    st.write("Imagen no disponible.")

        with col2:
            st.write(f"### {producto['Nombre']}")
            stock_color = obtener_color_stock(producto['Stock'])
            st.markdown(f"Código: {producto['Codigo']} | Precio: ${producto['Precio']} | <span style='color: {stock_color};'>STOCK: {producto['Stock']}</span>", unsafe_allow_html=True)
            st.write(f"Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}")
            st.write(f"Categorías: {producto['Categorias']}")
        st.write("---")

# Cargar datos
df = load_data()

# Título
st.markdown("<h1 style='text-align: center;'>🐻 Soop Buscador de Productos</h1>", unsafe_allow_html=True)

# Mostrar número de filas y columnas cargadas
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Campo de búsqueda
busqueda = st.selectbox("Escribí acá para buscar", [''] + list(df['Nombre']), index=0)

# Variables para verificar si se tildaron las casillas
col_opciones = st.columns(3)
with col_opciones[0]:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_opciones[1]:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col_opciones[2]:
    sugerir_por_rubro = st.checkbox("Sugerir por Rubro (Próximamente)")

# Condición para mostrar la imagen del bot
if busqueda == '' and not (ver_por_categorias or ordenar_por_novedad or sugerir_por_rubro):
    st.image('bot (8).png', width=480, use_column_width='auto')

# Verificar si el usuario ha escrito algo y filtrar productos
if busqueda:
    productos_filtrados = df[df['Nombre'].str.contains(busqueda, case=False)]
    if not productos_filtrados.empty:
        producto_seleccionado = productos_filtrados.iloc[0]
        mostrar_producto_completo(producto_seleccionado)

# Ver lista por categorías
if ver_por_categorias:
    todas_las_categorias = df['Categorias'].dropna().unique()
    categorias_individuales = set()
    for categorias in todas_las_categorias:
        for categoria in categorias.split(','):
            categorias_individuales.add(categoria.strip())
    categoria_seleccionada = st.selectbox('Categorías:', sorted(categorias_individuales))
    if categoria_seleccionada:
        productos_categoria = df[df['Categorias'].str.contains(categoria_seleccionada)]
        pagina = st.number_input('Página:', min_value=1, value=1)
        mostrar_lista_productos(productos_categoria, pagina)

# Ordenar por novedad
if ordenar_por_novedad:
    if 'Fecha Creado' in df.columns:
        df_ordenado = df.sort_values('Fecha Creado', ascending=False)
        pagina = st.number_input('Página:', min_value=1, value=1)
        mostrar_lista_productos(df_ordenado, pagina)
    else:
        st.warning("No se encontró la columna 'Fecha Creado'.")

# Sugerir por Rubro (en desarrollo)
if sugerir_por_rubro:
    st.info("Esta función estará disponible próximamente.")
