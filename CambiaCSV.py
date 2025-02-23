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
    delimitadores = [',', ';', '\t', '|']
    first_lines = uploaded_file.read(1024).decode('ISO-8859-1')
    uploaded_file.seek(0)
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

            # Asegurar que 'Costo (Pesos)' y 'Costo (USD)' existan
            if 'Costo' in df.columns and 'Costo (Pesos)' not in df.columns:
                df['Costo (Pesos)'] = df['Costo']
            if 'Costo FOB' in df.columns and 'Costo (USD)' not in df.columns:
                df['Costo (USD)'] = df['Costo FOB']

            # Convertir a valores numéricos
            columnas_numericas = ['Costo (Pesos)', 'Costo (USD)', 'Precio x Mayor', 'Precio Venta']
            for col in columnas_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Si 'Precio x Menor' no existe, calcularlo correctamente como un 90% más del costo en pesos
            if 'Costo (Pesos)' in df.columns:
                df['Precio x Menor'] = df['Costo (Pesos)'] * 1.90

            # Agregar columnas faltantes
            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = '0.00'

            # Reordenar columnas
            columnas_finales = list(dict.fromkeys(columnas_completas))
            columnas_disponibles = [col for col in columnas_finales if col in df.columns]
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
# Convertidores
# -------------------------
st.header("🛍️ Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("📤 Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    procesar_archivo(uploaded_file_productos, "Productos", 
        columnas_a_renombrar={'Precio': 'Precio x Mayor', 'Precio Jugueterias face': 'Precio Venta'},
        columnas_a_eliminar=['Precio 25 plus', 'Precio face+50', 'Precio BONUS', 'Precio Mayorista', 'Precio Online'],
        columnas_a_agregar=['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento', 'Columna', 'StockSuc2', 'StockSucNat'],
        columnas_id=['Id'],
        columnas_completas=['Id', 'Codigo', 'Nombre', 'Activo', 'Fecha Creado', 'Fecha Modificado', 'Descripcion', 'Orden', 
            'Codigo de Barras', 'Costo (Pesos)', 'Costo (USD)', 'Stock', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor', 
            'Costo Compuesto', 'Ultimo en Modificar'])

st.header("👥 Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("📤 Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

st.header("📦 Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("📤 Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")
