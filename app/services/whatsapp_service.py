import urllib.parse
import webbrowser

class WhatsAppService:
    @staticmethod
    def generate_whatsapp_link(mobile, message):
        """
        mobile: 10-digit mobile number
        message: Multi-line string message
        """
        # Ensure mobile starts with 91 (India) if it's 10 digits
        if len(mobile) == 10:
            mobile = f"91{mobile}"
            
        encoded_msg = urllib.parse.quote(message)
        link = f"https://wa.me/{mobile}?text={encoded_msg}"
        return link

    @staticmethod
    def open_whatsapp_web(mobile, message):
        link = WhatsAppService.generate_whatsapp_link(mobile, message)
        webbrowser.open(link)
