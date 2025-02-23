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

            # Asegurar que existan las columnas necesarias
            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = ''

            # Convertir valores numéricos
            columnas_numericas = ['Costo (Pesos)', 'Costo (USD)', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor']
            for col in columnas_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            if tipo == "Productos":
                # Historial de precios
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
                        df[col] = 0.00

                # Guardar valores anteriores y calcular diferencias
                df['Costo Anterior (Pesos)'] = df['Costo (Pesos)']
                df['Costo Anterior (USD)'] = df['Costo (USD)']
                df['Precio x Mayor Anterior'] = df['Precio x Mayor']
                df['Precio Venta Anterior'] = df['Precio Venta']
                df['Precio x Menor Anterior'] = df['Precio x Menor']

                df['Diferencia Costo (Pesos)'] = df['Costo (Pesos)'] - df['Costo Anterior (Pesos)']
                df['Diferencia Costo (USD)'] = df['Costo (USD)'] - df['Costo Anterior (USD)']
                df['Diferencia Precio x Mayor'] = df['Precio x Mayor'] - df['Precio x Mayor Anterior']
                df['Diferencia Precio Venta'] = df['Precio Venta'] - df['Precio Venta Anterior']
                df['Diferencia Precio x Menor'] = df['Precio x Menor'] - df['Precio x Menor Anterior']

                df['Costo Compuesto'] = df[['Item1', 'Item2', 'Costo Armado']].sum(axis=1)

            # Reordenar columnas
            columnas_finales = list(dict.fromkeys(columnas_completas + columnas_historial + columnas_diferencias + columnas_costos))
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
        columnas_a_renombrar={'Precio': 'Precio x Mayor', 'Precio Jugueterias face': 'Precio Venta', 'Precio Online': 'Precio x Menor'},
        columnas_a_eliminar=['Precio 25 plus', 'Precio face+50', 'Precio BONUS', 'Precio Mayorista'],
        columnas_a_agregar=['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento', 'Columna'],
        columnas_id=['Id'],
        columnas_completas=['Id', 'Codigo', 'Nombre', 'Activo', 'Fecha Creado', 'Fecha Modificado', 'Descripcion', 'Orden',
            'Codigo de Barras', 'unidad por bulto', 'Inner', 'Forzar Venta x Multiplos', 'Costo (Pesos)', 'Costo (USD)',
            'Stock', 'Precio x Mayor', 'Precio Venta', 'Precio x Menor', 'Categorias', 'Proveedor', 'Costo Compuesto',
            'Ultimo en Modificar'])

st.header("👥 Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("📤 Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    procesar_archivo(uploaded_file_clientes, "Clientes", {}, [], [],
                     ['Id'], ['Id', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Dirección'])

st.header("📦 Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("📤 Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    procesar_archivo(uploaded_file_pedidos, "Pedidos", {}, [], [],
                     ['Id'], ['Id', 'Id Cliente', 'Fecha Pedido', 'Producto', 'Cantidad', 'Precio', 'Estado'])
