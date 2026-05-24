import streamlit as st
import pytesseract
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Generador de WhatsApp - COD", page_icon="📱", layout="wide")

st.title("📱 Generador de Respuestas Rápidas - WhatsApp")
st.markdown("Pegue los datos del cliente o suba el pantallazo del pedido para generar el mensaje exacto.")

# --- 🛒 DICCIONARIO DE PRECIOS (MODIFIQUE ESTO A SU GUSTO MANO) ---
# Aquí usted pone el nombre del combo, el precio total, y el saldo si da los 10k de anticipo
promociones = {
    "1 Unidad": {"total": "89.900", "saldo": "79.900"},
    "Lleva 2": {"total": "149.900", "saldo": "139.900"},
    "Lleva 3 Paga 2": {"total": "179.900", "saldo": "169.900"},
    "Lleva 4": {"total": "210.000", "saldo": "200.000"}
}

# --- BARRA LATERAL: CONTROLES DE LA APP ---
st.sidebar.header("⚙️ Controles del Mensaje")

etapa = st.sidebar.selectbox(
    "Etapa del Proceso:",
    ["Confirmación de Compra", "Envío de Guía", "Novedad de Transportadora"]
)

# NUEVO CONTROL: Seleccionar la promoción
promo_seleccionada = st.sidebar.selectbox(
    "Promoción / Unidades Vendidas:",
    list(promociones.keys())
)

# Sacamos los precios según lo que usted escoja arriba
precio_total = promociones[promo_seleccionada]["total"]
precio_saldo = promociones[promo_seleccionada]["saldo"]

# Control B: Solo visible si es Confirmación de Compra
perfil_cliente = None
if etapa == "Confirmación de Compra":
    perfil_cliente = st.sidebar.radio(
        "Perfil del Cliente:",
        ["Normal", "Riesgo"]
    )

st.sidebar.divider()
st.sidebar.info("💡 **Nota:** El texto generado se puede copiar con un solo clic en el botón de la esquina del cuadro.")

# --- FUNCIÓN PA' SACAR LOS DATOS MEJORADA (MANO ESTE ES EL ARREGLO) ---
def parsear_datos(texto):
    datos = {"nombre": "[NOMBRE]", "direccion": "[DIRECCIÓN]", "ciudad": "[CIUDAD]"}
    if not texto.strip():
        return datos

    # 1. Limpiamos el texto, quitando líneas vacías excesivas y espacios
    lineas = texto.split('\n')
    lineas_limpias = [linea.strip() for linea in lineas if linea.strip()]
    
    # Flags y variables temporales para armar el nombre
    temp_nombre = ""
    temp_apellido = ""
    found_nombre_completo = False
    found_apellido_completo = False

    # 2. Analizamos línea por línea
    for i, linea in enumerate(lineas_limpias):
        linea_lower = linea.lower()
        
        # --- LÓGICA PARA EL NOMBRE MEJORADA ---
        # Buscamos la clave exacta 'nombre completo'
        if "nombre completo" == linea_lower:
            # Si la línea siguiente existe, es el nombre (ej: Stella)
            if i + 1 < len(lineas_limpias):
                temp_nombre = lineas_limpias[i+1]
                found_nombre_completo = True
        
        # Buscamos la clave exacta 'apellido completo'
        elif "apellido completo" == linea_lower:
            # Si la línea siguiente existe, es el apellido (ej: Velez Zambrano)
            if i + 1 < len(lineas_limpias):
                temp_apellido = lineas_limpias[i+1]
                found_apellido_completo = True

        # Si ya encontramos las dos partes, las armamos
        if found_nombre_completo and found_apellido_completo:
            datos["nombre"] = f"{temp_nombre} {temp_apellido}".strip()
            # Reseteamos flags por si acaso salen múltiples órdenes en un mismo texto
            found_nombre_completo = False
            found_apellido_completo = False

        # --- LÓGICA PARA LA DIRECCIÓN MEJORADA ---
        # Buscamos la clave exacta 'dirección exacta' (con y sin tilde por si acaso)
        elif "dirección exacta" == linea_lower or "direccion exacta" == linea_lower:
            # Si la línea siguiente existe, es la dirección (ej: CRA 29b #44-27)
            if i + 1 < len(lineas_limpias):
                datos["direccion"] = lineas_limpias[i+1]

        # --- LÓGICA PARA LA CIUDAD MEJORADA ---
        # Buscamos la clave exacta 'city' (como sale en la imagen) o 'ciudad'
        elif "city" == linea_lower or "ciudad" == linea_lower:
            # Si la línea siguiente existe, es la ciudad (ej: CALI)
            if i + 1 < len(lineas_limpias):
                datos["ciudad"] = lineas_limpias[i+1]
            
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
                st.expander("Ver texto extraído en crudo (OCR Output)").write(texto_crudo)
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
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte Sognovitta ({promo_seleccionada}):\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\nEl valor a pagar al recibir es de ${precio_total} COP. Recuerda que el pago es únicamente en EFECTIVO. Por favor, responda con 'CONFIRMAR' si los datos están correctos para despachar hoy mismo."
    else: # Riesgo
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte Sognovitta ({promo_seleccionada}):\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\n⚠️ Nota de despacho: Debido a la altísima demanda, requerimos un pequeño anticipo de seguridad de $10.000 COP para separar tu unidad y generar la guía hoy mismo. Este valor se descuenta de tu total, por lo que al recibir el producto solo pagarás el saldo de ${precio_saldo} COP en efectivo. Por favor, responda con 'CONFIRMAR' para apartar y recibir el pedido."

elif etapa == "Envío de Guía":
    mensaje_final = f"¡Hola {nombre_final}! 🚛 Excelente noticia, tu pedido de Sognovitta ({promo_seleccionada}) ya va en camino hacia {ciudad_final}. Tu número de guía es: [DEJAR ESPACIO PARA GUÍA]. Recuerda tener listo el efectivo para cuando llegue el mensajero. ¡Cualquier duda nos escribes!"

elif etapa == "Novedad de Transportadora":
    mensaje_final = f"¡Hola {nombre_final}! 🚨 La transportadora nos informa que tu pedido ya está en {ciudad_final} listo para entrega, pero no han podido contactarte. Por favor, confírmanos tu disponibilidad en {direccion_final} para que no devuelvan el paquete."

st.code(mensaje_final, language="text")
