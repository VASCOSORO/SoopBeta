import streamlit as st
import pandas as pd
import re

# Función para limpiar y convertir a entero
def limpiar_id(valor):
    if pd.isnull(valor):
        return None
    # Eliminar puntos y comas
    valor_limpio = re.sub(r'[.,]', '', str(valor))
    try:
        return int(valor_limpio)
    except ValueError:
        return None

# Interfaz para subir archivos en Streamlit
st.title("Convertidor de CSV para Productos, Clientes y Pedidos")

# Sección para el archivo de Productos
st.header("Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    # Leer el archivo CSV
    df_productos = pd.read_csv(uploaded_file_productos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    
    # Limpiar y convertir la columna 'Id' a entero
    if 'Id' in df_productos.columns:
        df_productos['Id'] = df_productos['Id'].apply(limpiar_id)
    
    # Renombrar las columnas que especificaste
    df_productos = df_productos.rename(columns={
        'Costo FOB': 'Costo en U$s',  # Cambio de 'Costo FOB' a 'Costo en U$s'
        'Precio jugueteria Face': 'Precio',  # Cambio de 'Precio Jugueteria Face' a 'Precio'
        'Precio': 'Precio x Mayor'  # Cambio de 'Precio' a 'Precio x Mayor'
    })
    
    # Eliminar columnas que no sirven
    df_productos = df_productos.drop(columns=['Precio Face + 50', 'Precio Bonus'], errors='ignore')
    
    # Agregar nuevas columnas vacías (pueden completarse luego)
    df_productos['Proveedor'] = ''
    df_productos['Pasillo'] = ''
    df_productos['Estante'] = ''
    df_productos['Fecha de Vencimiento'] = ''
    
    # Mostrar una tabla de datos modificada en la interfaz de Streamlit
    st.write("Archivo de Productos modificado:")
    st.dataframe(df_productos)
    
    # Guardar el archivo modificado en Excel
    excel_productos = df_productos.to_excel(index=False)
    
    # Proporcionar un enlace para descargar el archivo
    st.download_button(
        label="Descargar archivo modificado de Productos",
        data=excel_productos,
        file_name="archivo_modificado_productos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Sección para el archivo de Clientes
st.header("Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    # Leer el archivo CSV
    df_clientes = pd.read_csv(uploaded_file_clientes, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    
    # Limpiar y convertir las columnas 'Id' y 'Id Cliente' a entero
    if 'Id' in df_clientes.columns:
        df_clientes['Id'] = df_clientes['Id'].apply(limpiar_id)
    if 'Id Cliente' in df_clientes.columns:
        df_clientes['Id Cliente'] = df_clientes['Id Cliente'].apply(limpiar_id)
    
    # Mostrar una tabla de datos en la interfaz de Streamlit
    st.write("Archivo de Clientes cargado:")
    st.dataframe(df_clientes)
    
    # Guardar el archivo en formato Excel
    excel_clientes = df_clientes.to_excel(index=False)
    
    # Proporcionar un enlace para descargar el archivo
    st.download_button(
        label="Descargar archivo modificado de Clientes",
        data=excel_clientes,
        file_name="archivo_modificado_clientes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Sección para el archivo de Pedidos
st.header("Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    # Leer el archivo CSV
    df_pedidos = pd.read_csv(uploaded_file_pedidos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    
    # Limpiar y convertir las columnas 'Id' y 'Id Cliente' a entero
    if 'Id' in df_pedidos.columns:
        df_pedidos['Id'] = df_pedidos['Id'].apply(limpiar_id)
    if 'Id Cliente' in df_pedidos.columns:
        df_pedidos['Id Cliente'] = df_pedidos['Id Cliente'].apply(limpiar_id)
    
    # Mostrar una tabla de datos en la interfaz de Streamlit
    st.write("Archivo de Pedidos cargado:")
    st.dataframe(df_pedidos)
    
    # Guardar el archivo en formato Excel
    excel_pedidos = df_pedidos.to_excel(index=False)
    
    # Proporcionar un enlace para descargar el archivo
    st.download_button(
        label="Descargar archivo modificado de Pedidos",
        data=excel_pedidos,
        file_name="archivo_modificado_pedidos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
