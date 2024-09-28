import streamlit as st
import pandas as pd

# Cargar los datos del archivo de productos
file_path_productos = 'archivo_modificado_productos_20240928_201237.xlsx'  # Ruta al archivo
df_productos = pd.read_excel(file_path_productos)

# Configuración de la página
st.set_page_config(page_title="📁 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("📁 Módulo de Ventas")

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
    st.write(f"**Código:** {producto_data['Codigo']}")
    st.write(f"**Descripción:** {producto_data['Descripcion']}")
    st.write(f"**Precio:** ${producto_data['Precio']}")
    st.write(f"**Stock disponible:** {producto_data['Stock']}")
    st.image(producto_data['imagen'], width=150)

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
