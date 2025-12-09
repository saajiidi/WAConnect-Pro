
import unittest
from whatsapp_generator import WhatsAppLinkGenerator

class TestWhatsAppGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = WhatsAppLinkGenerator()

    def test_normalize_phone_bd(self):
        # Case 1: Standard BD mobile number
        phone = "01712345678"
        # User wants +88(11digit) -> +8801712345678
        expected = "+8801712345678" 
        self.assertEqual(self.generator.normalize_phone(phone), expected, f"Failed for {phone}")

    def test_normalize_phone_bd_with_88(self):
        # Case 2: Already has 88
        phone = "8801712345678"
        expected = "+8801712345678"
        self.assertEqual(self.generator.normalize_phone(phone), expected, f"Failed for {phone}")

    def test_normalize_phone_bd_with_plus_88(self):
        # Case 3: Already has +88
        phone = "+8801712345678"
        expected = "+8801712345678"
        self.assertEqual(self.generator.normalize_phone(phone), expected, f"Failed for {phone}")

    def test_normalize_phone_other(self):
        # Case 4: Random short number or other (just ensuring it doesn't break basic logic)
        phone = "123456"
        # Current logic adds + if missing
        self.assertTrue(self.generator.normalize_phone(phone).startswith("+880")) #detect country code Bangladesh if not present

    #now for other country detect country code from phone number pattern
    

if __name__ == '__main__':
    unittest.main()
