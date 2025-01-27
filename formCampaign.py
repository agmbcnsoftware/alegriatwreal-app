import streamlit as st
import pandas as pd
import time

def send_whatsapp(p1, p2, p3):
    # Aquí colocas tu lógica para enviar el mensaje de WhatsApp.
    st.write(f"Enviando mensaje con: {p1}, {p2}, {p3}")

def normalize_phone_number(phone):
    # Normaliza el número de teléfono
    phone = str(phone).strip().replace(" ", "")  # Elimina espacios adicionales
    if len(phone) == 9 and phone.isdigit():
        return f"whatsapp:+34{phone}"
    elif phone.startswith("+"):
        return f"whatsapp:{phone}"
    else:
        return None

# Título de la aplicación
st.title("Enviar mensajes de WhatsApp")

# Cargar archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leer el archivo Excel como DataFrame de Pandas
    try:
        df = pd.read_excel(uploaded_file)

        # Mostrar un mensaje con el número de filas y columnas
        st.success(f"Archivo cargado con éxito: {df.shape[0]} filas y {df.shape[1]} columnas")

        # Mostrar todas las filas del DataFrame con scroll
        st.dataframe(df, height=250)

        # Línea divisoria
        st.markdown("---")

        # Crear listas desplegables para seleccionar las columnas
        columns = df.columns.tolist()
        col1, col2, col3 = st.columns(3)

        with col1:
            phone_column = st.selectbox("Teléfono", columns, key="phone_col")
        with col2:
            col2_selection = st.selectbox("Primera variebla", columns, key="col2")
        with col3:
            col3_selection = st.selectbox("Segunda variable", columns, key="col3")

        # Línea divisoria
        st.markdown("---")

        # Botón para procesar los datos
        if st.button("Enviar mensajes de WhatsApp"):
            for index, row in df.iterrows():
                phone = normalize_phone_number(row[phone_column])
                if phone is None:
                    st.warning(f"Número de teléfono inválido en la fila {index + 1}: {row[phone_column]}")
                    continue
                
                p2 = row[col2_selection]
                p3 = row[col3_selection]

                # Llamar al método send_whatsapp con los valores seleccionados
                send_whatsapp(phone, p2, p3)
                time.sleep(0.5)

            st.success("Mensajes enviados exitosamente")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

