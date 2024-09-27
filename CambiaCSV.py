import streamlit as st
import pandas as pd

# Interfaz para subir archivos en Streamlit
st.title("Cargar y modificar CSV")

# Subir archivo CSV
uploaded_file = st.file_uploader("Subí tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Leer el archivo CSV
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')

    # Renombrar las columnas que especificaste
    df = df.rename(columns={
        'Costo FOB': 'Costo en U$s',  # Cambio de 'Costo FOB' a 'Costo en U$s'
        'Precio jugueteria Face': 'Precio',  # Cambio de 'Precio Jugueteria Face' a 'Precio'
        'Precio': 'Precio x Mayor'  # Cambio de 'Precio' a 'Precio x Mayor'
    })

    # Eliminar columnas que no sirven
    df = df.drop(columns=['Precio Face + 50', 'Precio Bonus'], errors='ignore')

    # Agregar nuevas columnas vacías (pueden completarse luego)
    df['Proveedor'] = ''
    df['Pasillo'] = ''
    df['Estante'] = ''
    df['Fecha de Vencimiento'] = ''

    # Mostrar una tabla de datos modificada en la interfaz de Streamlit
    st.write("Archivo modificado:")
    st.dataframe(df)

    # Guardar el archivo modificado en Excel
    st.write("Descargá el archivo modificado en formato Excel:")
    df.to_excel("archivo_modificado_streamlit.xlsx", index=False)
    
    # Proporcionar un enlace para descargar el archivo
    with open("archivo_modificado_streamlit.xlsx", "rb") as file:
        btn = st.download_button(
            label="Descargar archivo modificado",
            data=file,
            file_name="archivo_modificado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
