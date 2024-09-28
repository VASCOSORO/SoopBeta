import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Convertidor de CSV a Excel",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 Convertidor de CSV para Productos, Clientes y Pedidos")

# Función para limpiar y convertir las columnas 'Id' y 'Id Cliente'
def limpiar_id(valor):
    if pd.isnull(valor):
        return ""
    # Eliminar puntos y comas
    valor_limpio = str(valor).replace('.', '').replace(',', '')
    return valor_limpio

# Función para convertir DataFrame a Excel en memoria
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    excel_bytes = buffer.getvalue()
    return excel_bytes

# Función general para procesar archivos
def procesar_archivo(
    uploaded_file,
    tipo,
    columnas_a_renombrar,
    columnas_a_eliminar,
    columnas_a_agregar,
    columnas_id
):
    if uploaded_file is not None:
        try:
            # Leer el archivo CSV con separador ';' y codificación 'ISO-8859-1'
            df = pd.read_csv(
                uploaded_file,
                encoding='ISO-8859-1',
                sep=';',
                on_bad_lines='skip',
                dtype=str  # Leer todas las columnas como cadenas para evitar problemas de tipo
            )

            # Mostrar los nombres de las columnas para depuración
            st.write(f"🔍 **Columnas encontradas en {tipo}:**")
            st.write(df.columns.tolist())

            # Verificar y limpiar las columnas de identificación
            for columna in columnas_id:
                if columna in df.columns:
                    df[columna] = df[columna].apply(limpiar_id)
                    st.write(f"✅ **Columna '{columna}' limpiada correctamente.**")
                else:
                    st.warning(f"⚠️ La columna '{columna}' no se encuentra en el archivo de {tipo}.")

            # Renombrar las columnas especificadas, manejando variaciones en el nombre
            if columnas_a_renombrar:
                columnas_a_renombrar_final = {}
                for original, nuevo in columnas_a_renombrar.items():
                    # Crear un patrón regex para manejar mayúsculas/minúsculas
                    pattern = re.compile(re.escape(original), re.IGNORECASE)
                    matches = [col for col in df.columns if pattern.fullmatch(col)]
                    for match in matches:
                        columnas_a_renombrar_final[match] = nuevo
                if columnas_a_renombrar_final:
                    df = df.rename(columns=columnas_a_renombrar_final)
                    st.write(f"🔄 **Renombrando columnas en {tipo}:**")
                    st.write(columnas_a_renombrar_final)
                else:
                    st.warning(f"⚠️ No se encontraron columnas para renombrar en {tipo}.")

            # Eliminar columnas que no sirven
            if columnas_a_eliminar:
                columnas_existentes_a_eliminar = [col for col in columnas_a_eliminar if col in df.columns]
                if columnas_existentes_a_eliminar:
                    df = df.drop(columns=columnas_existentes_a_eliminar, errors='ignore')
                    st.write(f"🗑️ **Eliminando columnas en {tipo}:** {columnas_existentes_a_eliminar}")
                else:
                    st.warning(f"⚠️ No se encontraron columnas para eliminar en {tipo}.")

            # Agregar nuevas columnas vacías si no existen
            if columnas_a_agregar:
                nuevas_agregadas = []
                for columna in columnas_a_agregar:
                    if columna not in df.columns:
                        df[columna] = ''
                        nuevas_agregadas.append(columna)
                if nuevas_agregadas:
                    st.write(f"➕ **Nuevas columnas agregadas en {tipo}:** {nuevas_agregadas}")

            # Convertir las columnas de identificación a cadenas para evitar comas en la visualización
            for columna in columnas_id:
                if columna in df.columns:
                    df[columna] = df[columna].astype(str)

            # Mostrar una tabla de datos modificada en la interfaz de Streamlit
            st.write(f"📊 **Archivo de {tipo} modificado:**")
            st.dataframe(df)

            # Convertir el DataFrame a Excel en memoria
            excel = convertir_a_excel(df)

            # Verificar el tamaño del archivo Excel
            st.write(f"📝 **Tamaño del archivo Excel en bytes:** {len(excel)}")

            # Proporcionar un enlace para descargar el archivo
            st.download_button(
                label=f"📥 Descargar archivo modificado de {tipo}",
                data=excel,
                file_name=f"archivo_modificado_{tipo.lower()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar el archivo de {tipo}: {e}")

# Sección para el archivo de Productos
st.header("🛍️ Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("📤 Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    # Define las columnas específicas para Productos
    columnas_a_renombrar = {
        'precio': 'Precio x Mayor',                       # Cambio de 'precio' a 'Precio x Mayor'
        'Precio Jugueterias Face': 'Precio'               # Cambio de 'Precio Jugueterias Face' a 'Precio'
    }
    columnas_a_eliminar = ['Precio Face + 50', 'Precio Bonus']
    columnas_a_agregar = ['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento']
    columnas_id = ['Id']

    procesar_archivo(
        uploaded_file=uploaded_file_productos,
        tipo="Productos",
        columnas_a_renombrar=columnas_a_renombrar,
        columnas_a_eliminar=columnas_a_eliminar,
        columnas_a_agregar=columnas_a_agregar,
        columnas_id=columnas_id
    )

# Sección para el archivo de Clientes
st.header("👥 Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("📤 Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    # Define las columnas específicas para Clientes
    columnas_a_renombrar_clientes = {}        # No hay renombrado específico para Clientes
    columnas_a_eliminar_clientes = []         # No hay eliminación específica para Clientes
    columnas_a_agregar_clientes = []          # No hay nuevas columnas para Clientes
    columnas_id_clientes = ['Id', 'Id Cliente']

    procesar_archivo(
        uploaded_file=uploaded_file_clientes,
        tipo="Clientes",
        columnas_a_renombrar=columnas_a_renombrar_clientes,
        columnas_a_eliminar=columnas_a_eliminar_clientes,
        columnas_a_agregar=columnas_a_agregar_clientes,
        columnas_id=columnas_id_clientes
    )

# Sección para el archivo de Pedidos
st.header("📦 Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("📤 Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    # Define las columnas específicas para Pedidos
    columnas_a_renombrar_pedidos = {}         # No hay renombrado específico para Pedidos
    columnas_a_eliminar_pedidos = []          # No hay eliminación específica para Pedidos
    columnas_a_agregar_pedidos = []           # No hay nuevas columnas para Pedidos
    columnas_id_pedidos = ['Id', 'Id Cliente']

    procesar_archivo(
        uploaded_file=uploaded_file_pedidos,
        tipo="Pedidos",
        columnas_a_renombrar=columnas_a_renombrar_pedidos,
        columnas_a_eliminar=columnas_a_eliminar_pedidos,
        columnas_a_agregar=columnas_a_agregar_pedidos,
        columnas_id=columnas_id_pedidos
    )
