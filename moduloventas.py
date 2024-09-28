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
