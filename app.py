import streamlit as st
import pytesseract
from PIL import Image

# Configuración de la página pa' que se vea bien mela en PC y celular
st.set_page_config(page_title="Generador de WhatsApp - COD", page_icon="📱", layout="wide")

st.title("📱 Generador de Respuestas Rápidas - WhatsApp")
st.markdown("Pegue los datos del cliente o suba el pantallazo del pedido para generar el mensaje exacto.")

# --- BARRA LATERAL: CONTROLES DE LA APP ---
st.sidebar.header("⚙️ Controles del Mensaje")

etapa = st.sidebar.selectbox(
    "Etapa del Proceso:",
    ["Confirmación de Compra", "Envío de Guía", "Novedad de Transportadora"]
)

# Control B: Solo visible si es Confirmación de Compra
perfil_cliente = None
if etapa == "Confirmación de Compra":
    perfil_cliente = st.sidebar.radio(
        "Perfil del Cliente:",
        ["Normal", "Riesgo"]
    )

st.sidebar.divider()
st.sidebar.info("💡 **Nota:** El texto generado se puede copiar con un solo clic en el botón de la esquina del cuadro.")

# --- FUNCIÓN PA' SACAR LOS DATOS (EL MACHETAZO) ---
def parsear_datos(texto):
    # Valores por defecto por si el sistema no pesca nada
    datos = {"nombre": "[NOMBRE]", "direccion": "[DIRECCIÓN]", "ciudad": "[CIUDAD]"}
    
    if not texto.strip():
        return datos

    # Intentamos pescar los datos (ajustable según cómo escupa los datos Droppi o Shopify)
    lineas = texto.split('\n')
    for linea in lineas:
        linea_lower = linea.lower()
        if "nombre" in linea_lower or "cliente" in linea_lower:
            datos["nombre"] = linea.split(":", 1)[-1].strip() if ":" in linea else linea.strip()
        elif "direcci" in linea_lower:
            datos["direccion"] = linea.split(":", 1)[-1].strip() if ":" in linea else linea.strip()
        elif "ciudad" in linea_lower or "municipio" in linea_lower:
            datos["ciudad"] = linea.split(":", 1)[-1].strip() if ":" in linea else linea.strip()
            
    return datos

# --- TABS: ENTRADA DE DATOS ---
tab1, tab2 = st.tabs(["📝 Pegar Texto", "📸 Subir Imagen"])

texto_crudo = ""

with tab1:
    texto_crudo_input = st.text_area("Pegue aquí la información copiada (Shopify/Droppi):", height=150)
    if texto_crudo_input:
        texto_crudo = texto_crudo_input

with tab2:
    imagen_subida = st.file_uploader("Suba el pantallazo del pedido (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])
    if imagen_subida is not None:
        try:
            image = Image.open(imagen_subida)
            st.image(image, caption="Imagen cargada", use_container_width=True)
            with st.spinner("Extrayendo texto de la imagen, espere un momentico..."):
                texto_crudo = pytesseract.image_to_string(image, lang='spa') 
                st.success("¡Texto extraído coronado!")
                st.expander("Ver texto extraído en crudo").write(texto_crudo)
        except Exception as e:
            st.error(f"Pailas, hubo un error procesando la imagen: {e}")

# Procesamos los datos sacados
datos_extraidos = parsear_datos(texto_crudo)

st.divider()

# --- FORMULARIO PARA CONFIRMAR O EDITAR LOS DATOS ---
st.subheader("✍️ Verifique los datos antes de generar el mensaje")
col1, col2, col3 = st.columns(3)
with col1:
    nombre_final = st.text_input("Nombre:", value=datos_extraidos["nombre"])
with col2:
    direccion_final = st.text_input("Dirección:", value=datos_extraidos["direccion"])
with col3:
    ciudad_final = st.text_input("Ciudad:", value=datos_extraidos["ciudad"])

# --- LÓGICA DE PLANTILLAS (OUTPUT) ---
st.subheader("💬 Mensaje Generado")

mensaje_final = ""

if etapa == "Confirmación de Compra":
    if perfil_cliente == "Normal":
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte Sognovitta:\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\nEl valor a pagar al recibir es de $89.900 COP. Recuerda que el pago es únicamente en EFECTIVO. Por favor, responda con 'CONFIRMAR' si los datos están correctos para despachar hoy mismo."
    else: # Riesgo
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte Sognovitta:\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\n⚠️ Nota de despacho: Debido a la altísima demanda, requerimos un pequeño anticipo de seguridad de $10.000 COP para separar tu unidad y generar la guía hoy mismo. Este valor se descuenta de tu total, por lo que al recibir el producto solo pagarás el saldo de $79.900 COP en efectivo. Por favor, responda con 'CONFIRMAR' para apartar y recibir el pedido."

elif etapa == "Envío de Guía":
    mensaje_final = f"¡Hola {nombre_final}! 🚛 Excelente noticia, tu pedido de Sognovitta ya va en camino hacia {ciudad_final}. Tu número de guía es: [DEJAR ESPACIO PARA GUÍA]. Recuerda tener listo el efectivo para cuando llegue el mensajero. ¡Cualquier duda nos escribes!"

elif etapa == "Novedad de Transportadora":
    mensaje_final = f"¡Hola {nombre_final}! 🚨 La transportadora nos informa que tu pedido ya está en {ciudad_final} listo para entrega, pero no han podido contactarte. Por favor, confírmanos tu disponibilidad en {direccion_final} para que no devuelvan el paquete."

# El st.code permite que salga el botón de copiar y pegar en una
st.code(mensaje_final, language="text")