import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Convertidor de CSV a Excel",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📁 Convertidor de CSV a Excel")

def detectar_delimitador(uploaded_file):
    """ Detecta el delimitador correcto en la CSV """
    delimitadores = [',', ';', '\t', '|']
    first_lines = uploaded_file.read(1024).decode('ISO-8859-1')
    uploaded_file.seek(0)  # Volver al inicio del archivo
    return max(delimitadores, key=lambda d: first_lines.count(d))

def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    return buffer.getvalue()

def procesar_archivo(uploaded_file, tipo, columnas_a_renombrar, columnas_a_eliminar, columnas_a_agregar, columnas_id, columnas_completas):
    if uploaded_file is not None:
        try:
            delimitador = detectar_delimitador(uploaded_file)
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=delimitador, on_bad_lines='skip', dtype=str)
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            st.write(f"🔍 **Columnas detectadas en {tipo} (Original):**")
            st.write(df.columns.tolist())

            # Renombrar columnas
            for col_viejo, col_nuevo in columnas_a_renombrar.items():
                if col_viejo in df.columns:
                    df.rename(columns={col_viejo: col_nuevo}, inplace=True)

            # Eliminar columnas innecesarias
            df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns], errors='ignore', inplace=True)

            # Agregar columnas faltantes
            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = '0.00'

            # Ajustes específicos para Productos
            if tipo == "Productos":
                # Calcular el precio x menor como 90% más que el costo en pesos
                if 'Costo (Pesos)' in df.columns:
                    df['Precio x Menor'] = df['Costo (Pesos)'].astype(float) * 1.90
                else:
                    df['Precio x Menor'] = '0.00'

            # Reordenar columnas asegurando que todas existan
            columnas_disponibles = [col for col in columnas_completas if col in df.columns]
            df = df[columnas_disponibles]

            st.write(f"📊 **Archivo de {tipo} modificado:**")
            st.dataframe(df)

            excel = convertir_a_excel(df)
            timestamp = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y%m%d_%H%M%S")
            file_name = f"archivo_modificado_{tipo.lower()}_{timestamp}.xlsx"

            st.download_button(
                label=f"📥 Descargar archivo modificado de {tipo}",
                data=excel,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar el archivo de {tipo}: {e}")

# -------------------------
# Sección de Productos
# -------------------------
st.header("🛍️ Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("📤 Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    columnas_a_renombrar = {
        'Precio': 'Precio x Mayor',
        'Precio Jugueterias face': 'Precio Venta',
    }
    columnas_a_eliminar = ['Precio 25 plus', 'Precio face+50', 'Precio BONUS', 'Precio Mayorista', 'Precio Online', 'Precio face Dolar']
    columnas_a_agregar = ['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento', 'Columna', 'StockSuc2', 'StockSucNat']
    columnas_id = ['Id']

    columnas_completas_productos = [
        'Id', 'Codigo', 'Nombre', 'Activo', 'Fecha Creado', 'Fecha Modificado', 'Descripcion', 'Orden',
        'Codigo de Barras', 'unidad por bulto', 'Presentacion/paquete', 'forzar venta x cantidad',
        'Costo (Pesos)', 'Costo (USD)', 'Etiquetas', 'Stock', 'StockSuc2', 'StockSucNat',
        'Proveedor', 'Categorias', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor',
        'Pasillo', 'Estante', 'Columna', 'Fecha de Vencimiento', 'imagen', 'imagen_1', 'imagen_2', 'imagen_3',
        'youtube_link', 'Costo Compuesto', 'Item1', 'Item2', 'Armado'
    ]

    procesar_archivo(uploaded_file_productos, "Productos", columnas_a_renombrar, columnas_a_eliminar, columnas_a_agregar, columnas_id, columnas_completas_productos)

# -------------------------
# Sección de Clientes
# -------------------------
st.header("👥 Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("📤 Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    columnas_completas_clientes = ['Id', 'Id Cliente', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Dirección']
    procesar_archivo(uploaded_file_clientes, "Clientes", {}, [], [], ['Id', 'Id Cliente'], columnas_completas_clientes)

# -------------------------
# Sección de Pedidos
# -------------------------
st.header("📦 Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("📤 Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    columnas_completas_pedidos = ['Id', 'Id Cliente', 'Fecha Pedido', 'Producto', 'Cantidad', 'Precio', 'Estado']
    procesar_archivo(uploaded_file_pedidos, "Pedidos", {}, [], [], ['Id', 'Id Cliente'], columnas_completas_pedidos)
