import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="📁 Módulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 Módulo Productos")

# Función para convertir DataFrame a CSV en memoria
def convertir_a_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
    return buffer.getvalue()

# Función para agregar el footer
def agregar_footer():
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

# Sidebar para cargar el archivo CSV o Excel
st.sidebar.header("Cargar Archivo CSV o Excel de Productos")
uploaded_file = st.sidebar.file_uploader("📤 Subir archivo CSV o Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Detectar el tipo de archivo subido y leerlo
        if uploaded_file.name.endswith('.csv'):
            try:
                # Intentar leer el CSV con detección automática de delimitador y saltar líneas problemáticas
                df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            except Exception as e:
                st.error(f"❌ Error al procesar el CSV: {e}")
                st.stop()
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("❌ Formato de archivo no soportado. Por favor, sube un archivo CSV o XLSX.")
            st.stop()

        # Renombrar columnas según las indicaciones
        renombrar_columnas = {
            'precio': 'Precio x Mayor',
            'PRecios Jugueterias FAce': 'precio',
            'inner': 'Paquete/Presentación'
        }
        df.rename(columns=renombrar_columnas, inplace=True)

        # Eliminar columnas no necesarias si existen
        columnas_a_eliminar = ['precio 25 plus', 'precio precio face dolar', 'precio face+50', 'precio bonus']
        df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns], inplace=True)

        # Verificar y agregar columnas nuevas si no existen
        columnas_nuevas = [
            'Precio Promocional con Descuento', 
            'Precio x Mayor con Descuento', 
            'Precio x Menor con Descuento', 
            'Suc2Activ', 
            'StockSuc2', 
            'Código de Barras', 
            'Alto', 
            'Ancho',
            'Columna',
            'Fecha de Vencimiento',
            'Última modificación fecha',
            'Último en modificar',
            'Nota 1'
        ]
        for columna in columnas_nuevas:
            if columna not in df.columns:
                df[columna] = None

        # Establecer todos los valores en 'Suc2Activ' a "No"
        df['Suc2Activ'] = 'No'

        # Mostrar los nombres de las columnas para depuración
        st.sidebar.write("🔍 **Columnas en el archivo:**")
        st.sidebar.write(df.columns.tolist())

        # Inicialización de la variable df_modificado
        df_modificado = df.copy()

        # Configuración de la tabla AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(
            editable=True,  # Permitir edición
            groupable=True,
            resizable=True,
            sortable=True,
            wrapText=True,
            autoHeight=True
        )

        for column in df.columns:
            gb.configure_column(column, autoWidth=True)

        gridOptions = gb.build()

        # Mostrar el número de artículos filtrados
        st.write(f"Total de Artículos Filtrados: {len(df)}")

        # Mostrar la tabla editable
        mostrar_tabla = st.checkbox("Mostrar Vista Preliminar de la Tabla")

        if mostrar_tabla:
            st.header("📊 Tabla de Productos:")
            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                fit_columns_on_grid_load=True,
                theme='streamlit',
                enable_enterprise_modules=False,
                height=600,
                reload_data=False
            )

            # Actualizar df_modificado con la respuesta del grid
            df_modificado = grid_response['data']

        # Funcionalidad para agregar un nuevo producto
        st.header("➕ Agregar Nuevo Producto:")
        with st.expander("Agregar Producto"):
            with st.form(key='agregar_producto_unique'):

                # Sección de datos principales
                st.subheader("Datos Principales")
                nuevo_codigo = st.text_input("Código")
                nuevo_codigo_barras = st.text_input("Código de Barras")
                nuevo_nombre = st.text_input("Nombre")
                nuevo_categoria = st.text_input("Categoría")
                nuevo_descripcion = st.text_area("Descripción")
                nuevo_tamaño = st.text_input("Tamaño")
                nuevo_alto = st.number_input("Alto", min_value=0.0, step=0.01)
                nuevo_ancho = st.number_input("Ancho", min_value=0.0, step=0.01)

                # Línea separadora
                st.markdown("---")

                # Sección de precios y costos
                st.subheader("Precios y Costos")
                col1, col2, col3 = st.columns(3)
                with col1:
                    nuevo_precio_costo_pesos = st.number_input("Costo (Pesos)", min_value=0.0, step=0.01)
                    nuevo_precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01)
                    nuevo_precio_x_menor = st.number_input("Precio x Menor", min_value=0.0, step=0.01)
                with col2:
                    nuevo_precio_costo_usd = st.number_input("Costo (USD)", min_value=0.0, step=0.01)
                    nuevo_precio_x_mayor_descuento = st.number_input("Precio x Mayor con Descuento", min_value=0.0, step=0.01)
                    nuevo_precio_x_menor_descuento = st.number_input("Precio x Menor con Descuento", min_value=0.0, step=0.01)
                with col3:
                    nuevo_precio_venta_unitario = st.number_input("Precio Venta Unitario", min_value=0.0, step=0.01)
                    nuevo_precio_promocional_descuento = st.number_input("Precio Promocional con Descuento", min_value=0.0, step=0.01)

                # Campos adicionales
                st.subheader("Campos Adicionales")
                nuevo_fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')))
                nuevo_columna = st.text_input("Columna")
                nuevo_pasillo = st.text_input("Pasillo")
                nuevo_estante = st.text_input("Estante")

                # Nota 1
                nuevo_nota1 = st.text_area("Nota 1")

                submit_nuevo = st.form_submit_button(label='Agregar Producto')

                if submit_nuevo:
                    if not nuevo_codigo or not nuevo_nombre:
                        st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
                    elif df_modificado['Código'].astype(str).str.contains(nuevo_codigo).any():
                        st.error("❌ El Código ya existe. Por favor, utiliza un Código único.")
                    else:
                        # Agregar el nuevo producto al DataFrame
                        nuevo_producto = {
                            'Código': nuevo_codigo,
                            'Código de Barras': nuevo_codigo_barras,
                            'Nombre': nuevo_nombre,
                            'Categoría': nuevo_categoria,
                            'Descripción': nuevo_descripcion,
                            'Tamaño': nuevo_tamaño,
                            'Alto': nuevo_alto,
                            'Ancho': nuevo_ancho,
                            'Precio Promocional con Descuento': nuevo_precio_promocional_descuento,
                            'Precio x Mayor': nuevo_precio_x_mayor,
                            'Precio x Mayor con Descuento': nuevo_precio_x_mayor_descuento,
                            'Precio x Menor': nuevo_precio_x_menor,
                            'Precio x Menor con Descuento': nuevo_precio_x_menor_descuento,
                            'Precio Venta Unitario': nuevo_precio_venta_unitario,
                            'Precio': nuevo_precio_venta_unitario,  # Asegurarse de que "precio" se asigne correctamente
                            'Suc2Activ': 'No',
                            'StockSuc2': None,
                            'Costo (Pesos)': nuevo_precio_costo_pesos,
                            'Costo (USD)': nuevo_precio_costo_usd,
                            'Paquete/Presentación': None,  # Puedes ajustar si hay un valor por defecto
                            'Columna': nuevo_columna,
                            'Pasillo': nuevo_pasillo,
                            'Estante': nuevo_estante,
                            'Fecha de Vencimiento': nuevo_fecha_vencimiento,
                            'Última modificación fecha': None,  # Puedes establecer automáticamente la fecha
                            'Último en modificar': None,  # Puedes vincularlo con el usuario actual si es necesario
                            'Nota 1': nuevo_nota1
                        }
                        df_modificado = df_modificado.append(nuevo_producto, ignore_index=True)
                        st.success("✅ Producto agregado exitosamente.")

        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
    else:
        st.info("📂 Por favor, sube un archivo CSV o Excel para comenzar.")

    # Botón para descargar el archivo CSV o Excel modificado
    if uploaded_file is not None:
        st.header("💾 Descargar Archivo Modificado:")
        csv = convertir_a_csv(df_modificado)
        excel = convertir_a_excel(df_modificado)

        argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        timestamp = datetime.now(argentina).strftime("%Y%m%d_%H%M%S")

        # Opción para descargar como CSV
        st.download_button(
            label="📥 Descargar CSV Modificado",
            data=csv,
            file_name=f"productos_modificados_{timestamp}.csv",
            mime="text/csv"
        )

        # Opción para descargar como XLSX
        st.download_button(
            label="📥 Descargar Excel Modificado",
            data=excel,
            file_name=f"productos_modificados_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Agregar el footer
    agregar_footer()
