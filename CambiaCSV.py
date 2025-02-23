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

            # Si 'Precio x Menor' no existe, calcularlo como un 90% más del costo en pesos
            if 'Costo (Pesos)' in df.columns:
                df['Precio x Menor'] = df['Costo (Pesos)'].astype(float) * 1.90
            else:
                df['Precio x Menor'] = '0.00'

            # Agregar columnas faltantes
            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = '0.00'

            # Ajustes específicos para Productos
            if tipo == "Productos":
                columnas_historial = [
                    'Costo Anterior (Pesos)', 'Costo Anterior (USD)', 'Precio x Mayor Anterior',
                    'Precio Venta Anterior', 'Precio x Menor Anterior'
                ]
                columnas_diferencias = [
                    'Diferencia Costo (Pesos)', 'Diferencia Costo (USD)', 'Diferencia Precio x Mayor',
                    'Diferencia Precio Venta', 'Diferencia Precio x Menor'
                ]
                columnas_costos = ['Item1', 'Item2', 'Costo Armado', 'Costo Compuesto', 'Ultimo en Modificar']

                for col in columnas_historial + columnas_diferencias + columnas_costos:
                    if col not in df.columns:
                        df[col] = '0.00'

                # Convertir valores numéricos
                cols_a_convertir = [
                    'Costo (Pesos)', 'Costo (USD)', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor',
                    'Item1', 'Item2', 'Costo Armado'
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

                # Calcular Costo Compuesto
                df['Costo Compuesto'] = df[['Item1', 'Item2', 'Costo Armado']].sum(axis=1)

                columnas_completas.extend(columnas_historial + columnas_diferencias + columnas_costos)

            # Reordenar columnas
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
