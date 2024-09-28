import streamlit as st
import pandas as pd

# Cargar los datos desde el archivo Excel
file_path = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Ruta al archivo de clientes
df_clientes = pd.read_excel(file_path)

# Simulación de base de datos de productos
df_productos = pd.DataFrame({
    'Codigo': ['TM-26494', '41649'],
    'Nombre': ['Pulsera Puppy', 'Labial Infantil'],
    'Precio': [1963, 1599],
    'Stock': [5, 10]
})

# Configuración de la página
st.set_page_config(page_title="📁 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("📁 Módulo de Ventas")

# Sección de cliente
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

# Sección de productos
st.header("🛒 Buscador de Productos")

# Buscador de productos
producto_buscado = st.text_input("Buscar producto", placeholder="Escribí el nombre del producto...")

# Buscar coincidencias de productos
productos_filtrados = df_productos[df_productos['Nombre'].str.contains(producto_buscado, case=False, na=False)]

if not productos_filtrados.empty:
    producto_seleccionado = st.selectbox("Selecciona el producto", productos_filtrados['Nombre'].tolist())
    
    # Datos del producto seleccionado
    producto_data = df_productos[df_productos['Nombre'] == producto_seleccionado].iloc[0]
    st.write(f"**Precio:** ${producto_data['Precio']}")
    st.write(f"**Stock disponible:** {producto_data['Stock']}")
    
    # Campo para seleccionar cantidad
    cantidad = st.number_input("Cantidad", min_value=1, max_value=producto_data['Stock'], step=1)
    
    # Botón para agregar el producto al pedido
    if st.button("Agregar producto"):
        # Añadir producto al pedido con la cantidad seleccionada
        if 'pedido' not in st.session_state:
            st.session_state.pedido = []
        
        # Agregar el producto con los detalles
        producto_agregado = {
            'Codigo': producto_data['Codigo'],
            'Nombre': producto_data['Nombre'],
            'Cantidad': cantidad,
            'Precio': producto_data['Precio'],
            'Importe': cantidad * producto_data['Precio']
        }
        st.session_state.pedido.append(producto_agregado)
        st.success(f"Se agregó {cantidad} unidad(es) de {producto_data['Nombre']} al pedido.")

# Mostrar el pedido actual
if 'pedido' in st.session_state and st.session_state.pedido:
    st.header("📦 Pedido actual")
    
    # Convertir la lista de productos en un DataFrame
    pedido_df = pd.DataFrame(st.session_state.pedido)
    
    # Mostrar la tabla del pedido
    st.table(pedido_df[['Codigo', 'Nombre', 'Cantidad', 'Precio', 'Importe']])
    
    # Total de ítems y total del pedido
    total_items = pedido_df['Cantidad'].sum()
    total_monto = pedido_df['Importe'].sum()
    
    st.write(f"**Total de items:** {total_items}")
    st.write(f"**Total del pedido:** ${total_monto}")
    
    # Botón para guardar el pedido
    if st.button("Guardar pedido"):
        st.success("Pedido guardado exitosamente.")
        # Aquí se guardaría el pedido en la base de datos

