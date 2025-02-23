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
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

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

            # Agregar historial de precios y costos
            columnas_historial = [
                'Costo Anterior (Pesos)', 'Costo Anterior (USD)', 'Precio x Mayor Anterior',
                'Precio Venta Anterior', 'Precio x Menor Anterior'
            ]
            columnas_diferencias = [
                'Diferencia Costo (Pesos)', 'Diferencia Costo (USD)', 'Diferencia Precio x Mayor',
                'Diferencia Precio Venta', 'Diferencia Precio x Menor'
            ]
            
            for col in columnas_historial + columnas_diferencias:
                if col not in df.columns:
                    df[col] = '0.00'

            # Convertir a valores numéricos para cálculos
            cols_a_convertir = [
                'Costo (Pesos)', 'Costo (USD)', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor'
            ] + columnas_historial

            df[cols_a_convertir] = df[cols_a_convertir].astype(float)

            # Guardar valores anteriores
            df['Costo Anterior (Pesos)'] = df['Costo (Pesos)']
            df['Costo Anterior (USD)'] = df['Costo (USD)']
            df['Precio x Mayor Anterior'] = df['Precio x Mayor']
            df['Precio Venta Anterior'] = df['Precio Venta']
            df['Precio x Menor Anterior'] = df['Precio x Menor']

            # Calcular diferencias
            df['Diferencia Costo (Pesos)'] = df['Costo (Pesos)'] - df['Costo Anterior (Pesos)']
            df['Diferencia Costo (USD)'] = df['Costo (USD)'] - df['Costo Anterior (USD)']
            df['Diferencia Precio x Mayor'] = df['Precio x Mayor'] - df['Precio x Mayor Anterior']
            df['Diferencia Precio Venta'] = df['Precio Venta'] - df['Precio Venta Anterior']
            df['Diferencia Precio x Menor'] = df['Precio x Menor'] - df['Precio x Menor Anterior']

            # Reordenar columnas
            columnas_completas.extend(columnas_historial + columnas_diferencias)
            df = df[[col for col in columnas_completas if col in df.columns]]

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

# Lista completa de columnas para Productos
columnas_completas_productos = [
    'id', 'Codigo', 'Nombre', 'Activo', 'Fecha Creado', 'Fecha Modificado', 'Descripcion', 'Orden',
    'Codigo de Barras', 'unidad por bulto', 'Presentacion/paquete', 'forzar venta x cantidad',
    'Costo (Pesos)', 'Costo (USD)', 'Etiquetas', 'Stock', 'StockSuc2', 'StockSucNat',
    'Proveedor', 'Categorias', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor',
    'Pasillo', 'Estante', 'Columna', 'Fecha de Vencimiento', 'imagen', 'imagen_1', 'imagen_2', 'imagen_3',
    'youtube_link', 'Costo Compuesto', 'Item1', 'Item2', 'Armado'
]

# Sección de Productos
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
