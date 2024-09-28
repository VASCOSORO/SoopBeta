import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="📁 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("📁 Módulo de Ventas")

# Simulamos una base de datos de clientes y productos
df_clientes = pd.DataFrame({
    'Nombre': ['Juan Perez', 'Maria Lopez', 'Carlos Fernandez'],
    'Descuento': [10, 15, 5],
    'Ultima compra': ['2024-09-10', '2024-09-15', '2024-09-12'],
    'Vendedor': ['Carlos', 'Juan', 'Maria'],
    'Notas': ['Cliente preferencial', '', 'Pendiente de pago'],
    'WhatsApp': ['+5491123456789', '+5491198765432', '+5491187654321']
})

df_productos = pd.DataFrame({
    'Codigo': ['TM-26494', '41649'],
    'Nombre': ['Pulsera Puppy', 'Labial Infantil'],
    'Precio': [1963, 1599],
    'Stock': [5, 10]
})

# Sección de cliente
st.header("🧑‍💼 Datos del Cliente")
cliente_buscado = st.text_input("Buscar cliente", placeholder="Escribí el nombre del cliente...")

# Buscar coincidencias
clientes_filtrados = df_clientes[df_clientes['Nombre'].str.contains(cliente_buscado, case=False, na=False)]

if not clientes_filtrados.empty:
    cliente_seleccionado = st.selectbox("Selecciona el cliente", clientes_filtrados['Nombre'].tolist())
    
    # Datos del cliente seleccionado
    cliente_data = df_clientes[df_clientes['Nombre'] == cliente_seleccionado].iloc[0]
    st.write(f"**Descuento:** {cliente_data['Descuento']}%")
    st.write(f"**Última compra:** {cliente_data['Ultima compra']}")
    
    # Selección del vendedor
    vendedor = cliente_data['Vendedor'].split(',')[0]  # Primer vendedor asignado por defecto
    vendedor_seleccionado = st.selectbox("Vendedor asignado", cliente_data['Vendedor'].split(','))
    
    if vendedor != vendedor_seleccionado:
        st.warning(f"Estás cambiando el vendedor asignado. El vendedor original era {vendedor}.")
    
    # Notas del cliente
    st.write(f"**Notas:** {cliente_data['Notas'] if cliente_data['Notas'] else 'Sin notas.'}")
    
    # Enlace a WhatsApp
    whatsapp_url = f"https://wa.me/{cliente_data['WhatsApp']}"
    st.markdown(f"[Enviar mensaje por WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

    # Botón para acceder a la ficha del cliente
    st.button("Ver ficha del cliente")

# Sección de productos
st.header("🛒 Buscador de Productos")
producto_buscado = st.text_input("Buscar producto", placeholder="Escribí el nombre del producto...")

# Buscar coincidencias
productos_filtrados = df_productos[df_productos['Nombre'].str.contains(producto_buscado, case=False, na=False)]

if not productos_filtrados.empty:
    producto_seleccionado = st.selectbox("Selecciona el producto", productos_filtrados['Nombre'].tolist())
    
    # Datos del producto seleccionado
    producto_data = df_productos[df_productos['Nombre'] == producto_seleccionado].iloc[0]
    st.write(f"**Precio:** ${producto_data['Precio']}")
    st.write(f"**Stock disponible:** {producto_data['Stock']}")
    
    # Botón para agregar el producto al pedido
    if st.button("Agregar producto"):
        st.session_state.pedido.append(producto_data)  # Añadir producto al pedido

# Mostrar la tabla del pedido
if 'pedido' not in st.session_state:
    st.session_state.pedido = []

if st.session_state.pedido:
    st.header("📦 Pedido actual")
    pedido_df = pd.DataFrame(st.session_state.pedido)
    pedido_df['Importe'] = pedido_df['Cantidad'] * pedido_df['Precio']
    
    st.table(pedido_df[['Codigo', 'Nombre', 'Cantidad', 'Precio', 'Importe']])
    
    # Total de items y total del pedido
    total_items = len(pedido_df)
    total_monto = pedido_df['Importe'].sum()
    
    st.write(f"**Total de items:** {total_items}")
    st.write(f"**Total del pedido:** ${total_monto}")
    
    # Botón de guardar
    if st.button("Guardar pedido"):
        st.success("Pedido guardado exitosamente.")

