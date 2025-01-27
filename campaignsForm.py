import streamlit as st
import pandas as pd

def send_whatsapp(p1, p2, p3):
    # Aquí colocas tu lógica para enviar el mensaje de WhatsApp.
    st.write(f"Enviando mensaje con: {p1}, {p2}, {p3}")

# Título de la aplicación
st.title("Enviar mensajes de WhatsApp desde un Excel")

# Cargar archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leer el archivo Excel como DataFrame de Pandas
    try:
        df = pd.read_excel(uploaded_file)

        # Mostrar un mensaje con el número de filas y columnas
        st.success(f"Archivo cargado con éxito: {df.shape[0]} filas y {df.shape[1]} columnas")

        # Mostrar las primeras filas del DataFrame
        st.dataframe(df.head())

        # Crear listas desplegables para seleccionar las columnas
        columns = df.columns.tolist()
        col1 = st.selectbox("Selecciona la primera columna", columns, key="col1")
        col2 = st.selectbox("Selecciona la segunda columna", columns, key="col2")
        col3 = st.selectbox("Selecciona la tercera columna", columns, key="col3")

        # Botón para procesar los datos
        if st.button("Enviar mensajes de WhatsApp"):
            for index, row in df.iterrows():
                p1 = row[col1]
                p2 = row[col2]
                p3 = row[col3]

                # Llamar al método send_whatsapp con los valores seleccionados
                send_whatsapp(p1, p2, p3)

            st.success("Mensajes enviados exitosamente")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
