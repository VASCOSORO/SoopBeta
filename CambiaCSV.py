import streamlit as st
import pandas as pd

# Interfaz para subir archivos en Streamlit
st.title("Convertidor de CSV para Productos, Clientes y Pedidos")

# Sección para el archivo de Productos
st.header("Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    # Leer el archivo CSV, forzando 'Id' a ser un número entero sin decimales
    df_productos = pd.read_csv(uploaded_file_productos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip', dtype={'Id': str})

    # Asegurar que los IDs no tengan comas y sean números enteros
    df_productos['Id'] = df_productos['Id'].str.replace(".", "").astype(int)

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
    st.write("Descargá el archivo modificado en formato Excel:")
    df_productos.to_excel("archivo_modificado_productos_streamlit.xlsx", index=False)

    # Proporcionar un enlace para descargar el archivo
    with open("archivo_modificado_productos_streamlit.xlsx", "rb") as file:
        btn = st.download_button(
            label="Descargar archivo modificado de Productos",
            data=file,
            file_name="archivo_modificado_productos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Sección para el archivo de Clientes
st.header("Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    # Leer el archivo CSV, forzando 'Id' y 'Id Cliente' a ser enteros
    df_clientes = pd.read_csv(uploaded_file_clientes, encoding='ISO-8859-1', sep=';', on_bad_lines='skip', dtype={'Id': str, 'Id Cliente': str})

    # Asegurar que los IDs no tengan separadores de miles con comas, y sean enteros
    df_clientes['Id'] = df_clientes['Id'].str.replace(".", "").astype(int)
    df_clientes['Id Cliente'] = df_clientes['Id Cliente'].str.replace(".", "").astype(int)

    # Mostrar una tabla de datos en la interfaz de Streamlit
    st.write("Archivo de Clientes cargado:")
    st.dataframe(df_clientes)

    # Guardar el archivo en formato Excel
    df_clientes.to_excel("archivo_modificado_clientes_streamlit.xlsx", index=False)

    # Proporcionar un enlace para descargar el archivo
    with open("archivo_modificado_clientes_streamlit.xlsx", "rb") as file:
        btn = st.download_button(
            label="Descargar archivo modificado de Clientes",
            data=file,
            file_name="archivo_modificado_clientes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Sección para el archivo de Pedidos
st.header("Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    # Leer el archivo CSV, forzando 'Id' y 'Id Cliente' a ser enteros
    df_pedidos = pd.read_csv(uploaded_file_pedidos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip', dtype={'Id': str, 'Id Cliente': str})

    # Asegurar que los IDs no tengan separadores de miles con comas, y sean enteros
    df_pedidos['Id'] = df_pedidos['Id'].str.replace(".", "").astype(int)
    df_pedidos['Id Cliente'] = df_pedidos['Id Cliente'].str.replace(".", "").astype(int)

    # Mostrar una tabla de datos en la interfaz de Streamlit
    st.write("Archivo de Pedidos cargado:")
    st.dataframe(df_pedidos)

    # Guardar el archivo en formato Excel
    df_pedidos.to_excel("archivo_modificado_pedidos_streamlit.xlsx", index=False)

    # Proporcionar un enlace para descargar el archivo
    with open("archivo_modificado_pedidos_streamlit.xlsx", "rb") as file:
        btn = st.download_button(
            label="Descargar archivo modificado de Pedidos",
            data=file,
            file_name="archivo_modificado_pedidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
