import streamlit as st
import pandas as pd

# Cargar los datos de clientes y productos desde los archivos correspondientes
file_path_clientes = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Archivo de clientes
file_path_productos = 'archivo_modificado_productos_20240928_201237.xlsx'  # Archivo de productos

df_clientes = pd.read_excel(file_path_clientes)
df_productos = pd.read_excel(file_path_productos)

# Configuración de la página
st.set_page_config(page_title="📁 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("📁 Módulo de Ventas")

# Sección de cliente
st.header("🧑‍💼 Datos del Cliente")

# Buscador autocompletable de cliente con vendedor asignado al lado
col1, col2 = st.columns([2, 1])

with col1:
    cliente_seleccionado = st.selectbox(
        "Buscar cliente", df_clientes['Nombre'].unique(), 
        help="Escribí el nombre del cliente o seleccioná uno de la lista."
    )

# Obtener los datos del cliente seleccionado
cliente_data = df_clientes[df_clientes['Nombre'] == cliente_seleccionado].iloc[0]

with col2:
    # Vendedor asignado
    vendedores = cliente_data['Vendedores'].split(',') if pd.notna(cliente_data['Vendedores']) else ['No asignado']
    vendedor_default = vendedores[0]
    vendedor_seleccionado = st.selectbox("Vendedor asignado", vendedores)

# Mostrar detalles seleccionados (solo el vendedor por ahora)
st.write(f"**Cliente:** {cliente_seleccionado}")
st.write(f"**Vendedor asignado:** {vendedor_seleccionado}")

# Mantengo la estructura del resto del código para que funcione todo correctamente después de esto.
