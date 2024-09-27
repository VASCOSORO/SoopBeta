import streamlit as st
import pandas as pd

# Interfaz para subir archivos en Streamlit
st.title("Convertidor de CSV para Productos y Clientes")

# Sección para el archivo de Productos
st.header("Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    # Leer el archivo CSV
    df_productos = pd.read_csv(uploaded_file_productos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')

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
uploaded_file_clientes = st.file_uploader("Subí tu archivo CSV de Clientes", type=["csv"], key="clientes")

if uploaded_file_clientes is not None:
    # Leer el archivo CSV
    df_clientes = pd.read_csv(uploaded_file_clientes, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')

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
