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

def limpiar_id(valor):
    if pd.isnull(valor):
        return ""
    return str(valor).replace('.', '')

def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    return buffer.getvalue()

def merge_duplicate_columns(df, sep=" | "):
    # Para cada columna única, si aparece más de una vez, se fusionan sus datos
    unique_cols = list(df.columns)
    for col in pd.unique(unique_cols):
        dup_cols = [c for c in df.columns if c == col]
        if len(dup_cols) > 1:
            df[col] = df[dup_cols].apply(lambda row: sep.join([str(x) for x in row if pd.notna(x) and x != ""]), axis=1)
            df.drop(columns=dup_cols[1:], inplace=True)
    return df

def procesar_archivo(uploaded_file, tipo, columnas_a_renombrar, columnas_a_eliminar, columnas_a_agregar, columnas_id, columnas_completas):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(
                uploaded_file,
                encoding='ISO-8859-1',
                sep=';',
                on_bad_lines='skip',
                dtype=str
            )
            # Limpiar nombres de columnas: quitar espacios y normalizar
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
            
            # Corrección específica: si se encuentra "Precio Jugueterias" y "face", renombrarla a "Precio Venta"
            for col in df.columns:
                if 'Precio Jugueterias' in col and 'face' in col:
                    df.rename(columns={col: 'Precio Venta'}, inplace=True)
                    break

            st.write(f"🔍 **Columnas encontradas en {tipo}:**")
            st.write(df.columns.tolist())

            # Limpiar columnas de ID
            for columna in columnas_id:
                if columna in df.columns:
                    df[columna] = df[columna].apply(limpiar_id)

            # Renombrar columnas según el diccionario
            if columnas_a_renombrar:
                df = df.rename(columns=columnas_a_renombrar)

            # Eliminar columnas no deseadas
            if columnas_a_eliminar:
                df = df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns], errors='ignore')

            # Agregar columnas que falten en el CSV (con valor vacío)
            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = ''

            # Asegurar que existan todas las columnas requeridas (antes de fusionar duplicados)
            for col in columnas_completas:
                if col not in df.columns:
                    df[col] = ''

            # Fusionar columnas duplicadas sin perder datos
            df = merge_duplicate_columns(df)

            # Verificar nuevamente que todas las columnas requeridas estén presentes
            for col in columnas_completas:
                if col not in df.columns:
                    df[col] = ''

            # Reordenar las columnas según el orden definido
            df = df[columnas_completas]

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

# Lista completa de columnas para Productos (según la ficha que utilizás)
columnas_completas_productos = [
    'id', 'Codigo', 'Nombre', 'Activo', 'Fecha Creado', 'Fecha Modificado', 'Descripcion', 'Orden',
    'Codigo de Barras', 'unidad por bulto', 'Presentacion/paquete', 'forzar venta x cantidad',
    'Costo (Pesos)', 'Costo (USD)', 'Etiquetas', 'Stock', 'StockSuc2', 'StockSucNat',
    'Proveedor', 'Categorias', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor',
    'Pasillo', 'Estante', 'Columna', 'Fecha de Vencimiento', 'imagen', 'imagen_1', 'imagen_2', 'imagen_3',
    'youtube_link', 'Costo Compuesto', 'Item1', 'Item2', 'Armado'
]

# -------------------------
# Sección de Productos
# -------------------------
st.header("🛍️ Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("📤 Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    columnas_a_renombrar = {
        'Precio': 'Precio x Mayor',
        'Costo FOB': 'Costo (USD)',
        'Precio Precio face Dolar': 'Precio Venta'
    }
    columnas_a_eliminar = ['Precio 25 plus', 'Precio face+50', 'Precio BONUS', 'Precio Mayorista', 'Precio Online', 'Precio face Dolar']
    columnas_a_agregar = ['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento', 'Columna', 'StockSuc2', 'StockSucNat']
    columnas_id = ['Id']
    
    procesar_archivo(uploaded_file_productos, "Productos", columnas_a_renombrar, columnas_a_eliminar, columnas_a_agregar, columnas_id, columnas_completas_productos)

# -------------------------
# Sección de Clientes (ejemplo básico)
# -------------------------
st.header("👥 Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("📤 Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")
if uploaded_file_clientes is not None:
    columnas_completas_clientes = ['Id', 'Id Cliente', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Dirección']
    procesar_archivo(uploaded_file_clientes, "Clientes", {}, [], [], ['Id', 'Id Cliente'], columnas_completas_clientes)

# -------------------------
# Sección de Pedidos (ejemplo básico)
# -------------------------
st.header("📦 Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("📤 Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")
if uploaded_file_pedidos is not None:
    columnas_completas_pedidos = ['Id', 'Id Cliente', 'Fecha Pedido', 'Producto', 'Cantidad', 'Precio', 'Estado']
    procesar_archivo(uploaded_file_pedidos, "Pedidos", {}, [], [], ['Id', 'Id Cliente'], columnas_completas_pedidos)

# Footer personalizado
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
