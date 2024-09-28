import streamlit as st
import pandas as pd

# Cargar la base de datos real de productos
df_productos = pd.read_excel("1083.xlsx")

# Inicializar la lista de pedidos en el estado de la sesión
if "pedido" not in st.session_state:
    st.session_state.pedido = []

# Función para agregar un producto al pedido
def agregar_producto(producto_nombre, cantidad):
    producto = df_productos[df_productos['Producto'] == producto_nombre]
    if not producto.empty:
        nombre = producto.iloc[0]['Producto']
        precio = producto.iloc[0]['Precio']
        venta_forzada = producto.iloc[0].get('Venta Forzada', False)
        multiplo = producto.iloc[0].get('Multiplo_Venta', 1)
        
        # Validar si la venta está forzada
        if venta_forzada and cantidad % multiplo != 0:
            st.warning(f"La cantidad debe ser múltiplo de {multiplo}.")
        else:
            st.session_state.pedido.append({
                "producto": nombre,
                "cantidad": cantidad,
                "precio_unitario": precio,
                "importe": cantidad * precio
            })
            st.success(f"Producto {nombre} agregado con éxito!")

# Función para eliminar un producto del pedido
def eliminar_producto(index):
    st.session_state.pedido.pop(index)
    st.success("Producto eliminado del pedido.")

# Encabezado
st.title("Sistema de Gestión de Pedidos con Base de Datos Real")

# Campo para ingresar el nombre del producto
producto_seleccionado = st.selectbox("Selecciona el producto", df_productos['Producto'].unique())
cantidad_seleccionada = st.number_input("Cantidad", min_value=1, value=1)

# Botón para agregar el producto al pedido
if st.button("Agregar producto"):
    agregar_producto(producto_seleccionado, cantidad_seleccionada)

# Mostrar la lista de productos en el pedido
st.subheader("Pedido actual:")
if len(st.session_state.pedido) > 0:
    total_articulos = sum(item["cantidad"] for item in st.session_state.pedido)
    total_importe = sum(item["importe"] for item in st.session_state.pedido)

    st.write(f"Total de artículos: {total_articulos}")
    st.write(f"Total del pedido: ${total_importe:.2f}")

    # Mostrar la tabla de productos en el pedido
    for index, item in enumerate(st.session_state.pedido):
        st.write(f"{item['cantidad']} x {item['producto']} - ${item['precio_unitario']:.2f} c/u - Importe: ${item['importe']:.2f}")
        if st.button(f"Eliminar {item['producto']}", key=f"eliminar_{index}"):
            eliminar_producto(index)
else:
    st.write("No hay productos en el pedido.")

# Botón para descargar el pedido en Excel si hay productos
if len(st.session_state.pedido) > 0:
    df_pedido = pd.DataFrame(st.session_state.pedido)
    df_pedido.to_excel("pedido_final.xlsx", index=False)
    with open("pedido_final.xlsx", "rb") as file:
        st.download_button(
            label="Descargar pedido en Excel",
            data=file,
            file_name="pedido_final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
