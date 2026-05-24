import streamlit as st
import pytesseract
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Benz Natural - Generador WhatsApp", page_icon="💚", layout="wide")

st.title("💚 Benz Natural Shop - Automatización Logística")
st.markdown("Pegue los datos o suba el pantallazo para generar el mensaje exacto para Sognovitta.")

# --- 🛒 DICCIONARIO DE PRECIOS ACTUALIZADO ---
promociones = {
    "1 Unidad": {"total": "89.900", "saldo": "79.900"},
    "Lleva 3 Paga 2 (2+1 GRATIS)": {"total": "179.800", "saldo": "169.800"},
    "Lleva 5 Paga 3 (3+2 GRATIS)": {"total": "269.700", "saldo": "259.700"}
}

# --- BARRA LATERAL: CONTROLES DE LA APP ---
st.sidebar.header("⚙️ Configuración del Mensaje")

etapa = st.sidebar.selectbox(
    "Etapa del Proceso:",
    ["Confirmación de Compra", "Envío de Guía", "Novedad de Transportadora"]
)

# Control de Promociones
promo_seleccionada = st.sidebar.selectbox(
    "Seleccione la Oferta Vendida:",
    list(promociones.keys())
)

# Sacamos los precios dinámicamente
precio_total = promociones[promo_seleccionada]["total"]
precio_saldo = promociones[promo_seleccionada]["saldo"]

# Control B: Perfil de riesgo
perfil_cliente = None
if etapa == "Confirmación de Compra":
    perfil_cliente = st.sidebar.radio(
        "Perfil del Cliente (Pago Contraentrega):",
        ["Normal (Historial Limpio)", "Riesgo (Devoluciones Previas)"]
    )

st.sidebar.divider()
st.sidebar.info("💡 **Consejo:** Use el botón de 'Copy' en la esquina de la caja de texto final para WhatsApp.")

# --- FUNCIÓN PA' SACAR LOS DATOS (EL ARREGLO BULLETPROOF) ---
def parsear_datos(texto):
    datos = {"nombre": "[NOMBRE]", "direccion": "[DIRECCIÓN]", "ciudad": "[CIUDAD]"}
    if not texto.strip():
        return datos

    lineas = texto.split('\n')
    lineas_limpias = [linea.strip() for linea in lineas if linea.strip()]
    
    temp_nombre = ""
    temp_apellido = ""

    for i, linea in enumerate(lineas_limpias):
        linea_lower = linea.lower()
        
        # 1. Pescar Nombre (Basta con que la línea tenga la palabra 'nombre')
        if "nombre" in linea_lower:
            if i + 1 < len(lineas_limpias):
                temp_nombre = lineas_limpias[i+1]
        
        # 2. Pescar Apellido (Basta con que la línea tenga la palabra 'apellido')
        elif "apellido" in linea_lower:
            if i + 1 < len(lineas_limpias):
                temp_apellido = lineas_limpias[i+1]

        # 3. Pescar Dirección Exacta (Mano, este es el machetazo clave)
        # Si encuentra "direc" o "exacta", sabemos que la línea de abajo es la dirección
        elif "direc" in linea_lower or "exacta" in linea_lower:
            if i + 1 < len(lineas_limpias):
                datos["direccion"] = lineas_limpias[i+1].upper()

        # 4. Pescar Ciudad / City
        elif "city" in linea_lower or "ciudad" in linea_lower or "municipio" in linea_lower:
            if i + 1 < len(lineas_limpias):
                datos["ciudad"] = lineas_limpias[i+1].upper()
            
    # Si logramos extraer algo del nombre o apellido, lo unimos limpio
    if temp_nombre or temp_apellido:
        datos["nombre"] = f"{temp_nombre} {temp_apellido}".strip().title()
        
    return datos

# --- TABS: ENTRADA DE DATOS ---
tab1, tab2 = st.tabs(["📝 Pegar Texto", "📸 Subir Imagen (OCR)"])

texto_crudo = ""

with tab1:
    texto_crudo_input = st.text_area("Pegue el texto crudo aquí (de Shopify/Dropi):", height=200, placeholder="Copie todo el detalle del pedido...")
    if texto_crudo_input:
        texto_crudo = texto_crudo_input

with tab2:
    imagen_subida = st.file_uploader("Suba el pantallazo del pedido (formatos PNG, JPG):", type=["png", "jpg", "jpeg"])
    if imagen_subida is not None:
        try:
            image = Image.open(imagen_subida)
            st.image(image, caption="Imagen cargada", use_container_width=True)
            with st.spinner("Leyendo el texto del pantallazo, espere un momentico..."):
                texto_crudo = pytesseract.image_to_string(image, lang='spa') 
                st.success("¡Texto extraído melo!")
                with st.expander("Ver texto crudo extraído (OCR)"):
                    st.text(texto_crudo)
        except Exception as e:
            st.error(f"Pailas mano, hubo un error procesando la imagen. Error: {e}")

# Procesamos datos sacados con la nueva función permisiva
datos_extraidos = parsear_datos(texto_crudo)

st.divider()

# --- VERIFICACIÓN DE DATOS ANTES DE GENERAR ---
st.subheader("✍️ 1. Verifique los datos extraídos")
st.info("Ajuste los datos si el OCR no leyó bien alguna parte.")
col1, col2, col3 = st.columns(3)
with col1:
    nombre_final = st.text_input("Nombre del Cliente:", value=datos_extraidos["nombre"])
with col2:
    direccion_final = st.text_input("Dirección de Envío:", value=datos_extraidos["direccion"])
with col3:
    ciudad_final = st.text_input("Ciudad/Municipio:", value=datos_extraidos["ciudad"])

# --- LÓGICA DE PLANTILLAS (OUTPUT FINAL) ---
st.subheader("💬 2. Mensaje de WhatsApp Generado")

mensaje_final = ""

if etapa == "Confirmación de Compra":
    if perfil_cliente == "Normal (Historial Limpio)":
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte tu pedido de Sognovitta ({promo_seleccionada}):\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\nEl valor a pagar al recibir es de ${precio_total} COP. Recuerda que el pago es únicamente en EFECTIVO. Por favor, responda con 'CONFIRMAR' si los datos están correctos para despachar hoy mismo."
    else: # Riesgo
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte tu pedido de Sognovitta ({promo_seleccionada}):\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\n⚠️ Nota de despacho: Debido a la altísima demanda y para asegurar tu unidad, requerimos un pequeño anticipo de seguridad de $10.000 COP para generar la guía hoy mismo. Este valor se descuenta de tu total, por lo que al recibir el producto solo pagarás el saldo de ${precio_saldo} COP en efectivo al mensajero. Por favor, responda con 'CONFIRMAR' para apartar tu pedido."

elif etapa == "Envío de Guía":
    mensaje_final = f"¡Hola {nombre_final}! 🚛 Excelente noticia, tu pedido de Sognovitta ({promo_seleccionada}) ya va en camino hacia {ciudad_final}. Tu número de guía es: [DEJAR ESPACIO PARA ESCRIBIR GUÍA AQUÍ]. Recuerda tener listo el efectivo (${precio_total} COP) para cuando llegue el mensajero. ¡Cualquier duda nos escribes!"

elif etapa == "Novedad de Transportadora":
    mensaje_final = f"¡Hola {nombre_final}! 🚨 La transportadora nos informa que tu pedido ya está en {ciudad_final} listo para entrega, pero no han podido contactarte. Por favor, confírmanos tu disponibilidad en {direccion_final} para coordinar la entrega y que no devuelvan el paquete."

st.code(mensaje_final, language="text")
