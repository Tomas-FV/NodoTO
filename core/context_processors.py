import os


def contacto(request):
    """Expone datos de contacto (WhatsApp, email, Instagram) desde variables de entorno."""
    return {
        'contact_email': os.getenv('CONTACT_EMAIL', ''),
        'contact_whatsapp_number': os.getenv('CONTACT_WHATSAPP_NUMBER', ''),
        'contact_instagram_url': os.getenv('CONTACT_INSTAGRAM_URL', ''),
    }
