import streamlit as st
import pandas as pd

# Simular base de datos de productos
productos = {
    "SE-52817": {"nombre": "PISTOLA PREMIUM LANZA DARDOS BATMAN", "precio": 7645.00, "forzado": False},
    "EP-4138": {"nombre": "Goma de Borrar En Mamadera", "precio": 900.00, "forzado": True, "multiplo": 24},
    # Agrega más productos aquí
}

# Inicializar sesión de estado para el pedido
if "pedido" not in st.session_state:
    st.session_state.pedido = []

# Función para agregar un producto al pedido
def agregar_producto(codigo, cantidad):
    producto = productos.get(codigo)
    if producto:
        if producto.get("forzado") and cantidad % producto.get("multiplo", 1) != 0:
            st.warning(f"La cantidad debe ser múltiplo de {producto['multiplo']}.")
        else:
            st.session_state.pedido.append({
                "codigo": codigo,
                "nombre": producto["nombre"],
                "cantidad": cantidad,
                "precio_unitario": producto["precio"],
                "importe": cantidad * producto["precio"]
            })
            st.success(f"Producto {producto['nombre']} agregado con éxito!")

# Función para eliminar un producto del pedido
def eliminar_producto(index):
    st.session_state.pedido.pop(index)
    st.success("Producto eliminado del pedido.")

# Encabezado
st.title("Sistema de Gestión de Pedidos")

# Selector de cliente (simulado)
st.selectbox("Cliente", ["Pedido de prueba", "Cliente 2", "Cliente 3"])

# Campo de búsqueda de productos
producto_seleccionado = st.text_input("Código del producto", placeholder="EP-4138...")
cantidad_seleccionada = st.number_input("Cantidad", min_value=1, value=1)

# Agregar producto al pedido
if st.button("Agregar"):
    agregar_producto(producto_seleccionado, cantidad_seleccionada)

# Mostrar lista de productos en el pedido
st.subheader("Pedido actual")
if len(st.session_state.pedido) > 0:
    total_articulos = sum(item["cantidad"] for item in st.session_state.pedido)
    total_importe = sum(item["importe"] for item in st.session_state.pedido)

    st.write(f"Total de artículos: {total_articulos}")
    st.write(f"Total del pedido: ${total_importe:.2f}")

    # Mostrar la tabla de productos en el pedido
    for index, item in enumerate(st.session_state.pedido):
        st.write(f"{item['cantidad']} x {item['nombre']} - ${item['precio_unitario']:.2f} c/u - Importe: ${item['importe']:.2f}")
        if st.button(f"Eliminar {item['nombre']}", key=f"eliminar_{index}"):
            eliminar_producto(index)
else:
    st.write("No hay productos en el pedido.")

# Botón para descargar el pedido en Excel
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
