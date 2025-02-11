import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime
import pytz  # Importar pytz para manejo de zonas horarias

# Configuración de la página
st.set_page_config(
    page_title="Convertidor de CSV a Excel",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 Convertidor de CSV")

def limpiar_id(valor):
    if pd.isnull(valor):
        return ""
    return str(valor).replace('.', '')

def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    return buffer.getvalue()

def procesar_archivo(uploaded_file, tipo, columnas_a_renombrar, columnas_a_eliminar, columnas_a_agregar, columnas_id):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(
                uploaded_file,
                encoding='ISO-8859-1',
                sep=';',
                on_bad_lines='skip',
                dtype=str
            )
            df.columns = df.columns.str.strip()

            st.write(f"🔍 **Columnas encontradas en {tipo}:**")
            st.write(df.columns.tolist())

            for columna in columnas_id:
                if columna in df.columns:
                    df[columna] = df[columna].apply(limpiar_id)

            if columnas_a_renombrar:
                df = df.rename(columns=columnas_a_renombrar)

            if columnas_a_eliminar:
                df = df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns], errors='ignore')

            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = ''

            st.write(f"📊 **Archivo de {tipo} modificado:**")
            st.dataframe(df)

            excel = convertir_a_excel(df)
            argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            timestamp = datetime.now(argentina).strftime("%Y%m%d_%H%M%S")
            file_name = f"archivo_modificado_{tipo.lower()}_{timestamp}.xlsx"

            st.download_button(
                label=f"📥 Descargar archivo modificado de {tipo}",
                data=excel,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar el archivo de {tipo}: {e}")

st.header("🛍️ Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("📤 Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    columnas_a_renombrar = {
        'Precio': 'Precio x Mayor',
        'Precio Jugueterias Face': 'Precio Venta',
        'Costo FOB': 'Costo usd',
        'Precio Precio face Dolar': 'Precio USD'
    }
    columnas_a_eliminar = ['Precio 25 plus', 'Precio face+50', 'Precio BONUS', 'Precio Mayorista', 'Precio Online', 'Precio face Dolar']
    columnas_a_agregar = ['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento', 'Columna', 'Stock Suc2', 'Stock SucNat']
    columnas_id = ['Id']

    procesar_archivo(uploaded_file_productos, "Productos", columnas_a_renombrar, columnas_a_eliminar, columnas_a_agregar, columnas_id)

# Sección para el archivo de Clientes
st.header("👥 Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("📤 Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    columnas_a_renombrar_clientes = {}
    columnas_a_eliminar_clientes = []
    columnas_a_agregar_clientes = []
    columnas_id_clientes = ['Id', 'Id Cliente']

    procesar_archivo(uploaded_file_clientes, "Clientes", columnas_a_renombrar_clientes, columnas_a_eliminar_clientes, columnas_a_agregar_clientes, columnas_id_clientes)

# Sección para el archivo de Pedidos
st.header("📦 Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("📤 Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    columnas_a_renombrar_pedidos = {}
    columnas_a_eliminar_pedidos = []
    columnas_a_agregar_pedidos = []
    columnas_id_pedidos = ['Id', 'Id Cliente']

    procesar_archivo(uploaded_file_pedidos, "Pedidos", columnas_a_renombrar_pedidos, columnas_a_eliminar_pedidos, columnas_a_agregar_pedidos, columnas_id_pedidos)

# Agregar CSS personalizado para el footer
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f1f1f1;
    color: #555;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
}
</style>
<div class="footer">
    Powered by VASCO.SORO
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
