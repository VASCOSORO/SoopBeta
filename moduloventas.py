import streamlit as st
import pandas as pd

# Cargar el archivo Excel que contiene los datos de los clientes
file_path = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Ruta del archivo Excel local
df_clientes = pd.read_excel(file_path)

# Configuración de la página
st.set_page_config(page_title="📁 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("📁 Módulo de Ventas")

# Sección del cliente
st.header("🧑‍💼 Datos del Cliente")

# Buscador de cliente
cliente_buscado = st.text_input("Buscar cliente", placeholder="Escribí el nombre del cliente...")

# Buscar coincidencias de clientes
clientes_filtrados = df_clientes[df_clientes['Nombre'].str.contains(cliente_buscado, case=False, na=False)]

if not clientes_filtrados.empty:
    cliente_seleccionado = st.selectbox("Selecciona el cliente", clientes_filtrados['Nombre'].tolist())
    
    # Obtener datos del cliente seleccionado
    cliente_data = df_clientes[df_clientes['Nombre'] == cliente_seleccionado].iloc[0]
    
    # Mostrar detalles del cliente
    st.write(f"**Descuento:** {cliente_data['Descuento']}%")
    st.write(f"**Última compra:** {cliente_data['Fecha Modificado']}")
    
    # Vendedor asignado
    vendedores = cliente_data['Vendedores'].split(',') if pd.notna(cliente_data['Vendedores']) else ['No asignado']
    vendedor_default = vendedores[0]
    vendedor_seleccionado = st.selectbox("Vendedor asignado", vendedores)
    
    if vendedor_default != vendedor_seleccionado:
        st.warning(f"Estás cambiando el vendedor asignado. El vendedor original era {vendedor_default}.")
    
    # Notas del cliente
    notas_cliente = cliente_data['Notas'] if pd.notna(cliente_data['Notas']) else 'Sin notas'
    st.write(f"**Notas del cliente:** {notas_cliente}")
    
    # Enlace a WhatsApp usando el número de celular del cliente
    celular_cliente = cliente_data['Celular'] if pd.notna(cliente_data['Celular']) else 'Sin número de WhatsApp'
    if pd.notna(cliente_data['Celular']):
        whatsapp_url = f"https://wa.me/{celular_cliente}"
        st.markdown(f"[Enviar mensaje por WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

    # Botón para ir a la ficha del cliente
    st.button("Ver ficha del cliente")

# Mostrar tabla de clientes
st.header("📋 Lista de Clientes (Vista previa)")
st.dataframe(df_clientes[['Nombre', 'Descuento', 'Celular', 'Vendedores']])
