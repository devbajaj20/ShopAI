"""
Multilingual Support Module
Languages: English, Hindi, Tamil, Telugu, Spanish, French, German
"""

import re
from typing import Dict, Optional, Tuple

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
}

INTENT_TRANSLATIONS: Dict[str, Dict[str, list]] = {
    'hi': {
        'add':      ['जोड़ो', 'जोड़ें', 'डालो', 'चाहिए', 'लेना', 'खरीदना', 'add karo', 'dalo',
                     'लो', 'दे दो', 'खरीदो'],
        'remove':   ['हटाओ', 'हटाएं', 'निकालो', 'delete karo', 'निकाल दो'],
        'search':   ['खोजो', 'ढूंढो', 'दिखाओ', 'search karo', 'dikhao', 'दिखा दो'],
        'view':     ['कार्ट दिखाओ', 'cart dikhao', 'cart dekho', 'मेरा कार्ट'],
        'checkout': ['checkout karo', 'payment karo', 'order karo', 'खरीदो', 'ऑर्डर करो'],
    },
    'ta': {
        'add':      ['சேர்க்க', 'சேர்', 'வேண்டும்', 'வாங்க', 'போடு', 'ஒரு', 'இரண்டு'],
        'remove':   ['நீக்க', 'அகற்று', 'எடு', 'delete செய்'],
        'search':   ['தேடு', 'காட்டு', 'பார்க்க', 'search செய்'],
        'view':     ['cart காட்டு', 'cart பார்க்க', 'என் cart'],
        'checkout': ['checkout', 'பணம் செலுத்து', 'order செய்', 'வாங்கு'],
    },
    'te': {
        'add':      ['చేర్చు', 'వేయి', 'కావాలి', 'కొనాలి', 'పెట్టు', 'ఒక', 'రెండు'],
        'remove':   ['తీసివేయి', 'తొలగించు', 'పదుగు', 'delete చేయి'],
        'search':   ['వెతుకు', 'చూపించు', 'కనుగొను', 'search చేయి'],
        'view':     ['cart చూపించు', 'cart చూడు', 'నా cart'],
        'checkout': ['checkout', 'చెల్లించు', 'order చేయి', 'కొను'],
    },
    'es': {
        'add':      ['agregar', 'añadir', 'poner', 'quiero', 'comprar', 'pon', 'un', 'una'],
        'remove':   ['quitar', 'eliminar', 'borrar', 'sacar', 'cancelar'],
        'search':   ['buscar', 'encontrar', 'mostrar', 'busca'],
        'view':     ['ver carrito', 'mostrar carrito', 'mi carrito'],
        'checkout': ['pagar', 'finalizar', 'comprar ahora', 'proceder'],
    },
    'fr': {
        'add':      ['ajouter', 'mettre', 'je veux', 'acheter', 'ajoute', 'un', 'une'],
        'remove':   ['retirer', 'enlever', 'supprimer', 'annuler'],
        'search':   ['chercher', 'trouver', 'montrer', 'afficher'],
        'view':     ['voir panier', 'afficher panier', 'mon panier'],
        'checkout': ['payer', 'finaliser', 'commander', 'procéder'],
    },
    'de': {
        'add':      ['hinzufügen', 'kaufen', 'ich möchte', 'gib mir', 'legen', 'ein', 'eine'],
        'remove':   ['entfernen', 'löschen', 'herausnehmen', 'stornieren'],
        'search':   ['suchen', 'finden', 'zeigen', 'anzeigen'],
        'view':     ['warenkorb anzeigen', 'was ist im warenkorb', 'warenkorb'],
        'checkout': ['bezahlen', 'bestellen', 'kasse'],
    },
}

COLOR_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'hi': {
        'लाल': 'red', 'नीला': 'blue', 'नीली': 'blue', 'हरा': 'green', 'पीला': 'yellow',
        'काला': 'black', 'काली': 'black', 'सफेद': 'white', 'गुलाबी': 'pink',
        'बैंगनी': 'purple', 'नारंगी': 'orange', 'भूरा': 'brown', 'स्लेटी': 'gray',
        'ग्रे': 'gray', 'नेवी': 'navy',
    },
    'ta': {
        'சிவப்பு': 'red', 'நீலம்': 'blue', 'பச்சை': 'green', 'மஞ்சள்': 'yellow',
        'கருப்பு': 'black', 'வெள்ளை': 'white', 'இளஞ்சிவப்பு': 'pink',
        'ஊதா': 'purple', 'ஆரஞ்சு': 'orange', 'பழுப்பு': 'brown', 'சாம்பல்': 'gray',
    },
    'te': {
        'ఎరుపు': 'red', 'నీలం': 'blue', 'నీలి': 'blue', 'ఆకుపచ్చ': 'green', 'పసుపు': 'yellow',
        'నలుపు': 'black', 'తెలుపు': 'white', 'గులాబీ': 'pink',
        'ఊదా': 'purple', 'నారింజ': 'orange', 'గోధుమ': 'brown', 'బూడిద': 'gray',
    },
    'es': {
        'rojo': 'red', 'azul': 'blue', 'verde': 'green', 'amarillo': 'yellow',
        'negro': 'black', 'blanco': 'white', 'rosa': 'pink', 'morado': 'purple',
        'naranja': 'orange', 'marrón': 'brown', 'gris': 'gray',
    },
    'fr': {
        'rouge': 'red', 'bleu': 'blue', 'vert': 'green', 'jaune': 'yellow',
        'noir': 'black', 'blanc': 'white', 'rose': 'pink', 'violet': 'purple',
        'orange': 'orange', 'marron': 'brown', 'gris': 'gray',
    },
    'de': {
        'rot': 'red', 'blau': 'blue', 'grün': 'green', 'gelb': 'yellow',
        'schwarz': 'black', 'weiß': 'white', 'rosa': 'pink', 'lila': 'purple',
        'orange': 'orange', 'braun': 'brown', 'grau': 'gray',
    },
}

PRODUCT_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'hi': {
        # Shirts / T-shirts
        'टी-शर्ट': 't-shirt', 'टीशर्ट': 't-shirt', 'टी शर्ट': 't-shirt',
        'कमीज़': 'shirt', 'कमीज': 'shirt', 'शर्ट': 'shirt',
        # Bottoms
        'जींस': 'jeans', 'जीन्स': 'jeans', 'पैंट': 'pants', 'पतलून': 'pants',
        'ट्रैक पैंट': 'track pants', 'ट्रैकपैंट': 'track pants',
        # Outerwear
        'जैकेट': 'jacket', 'कोट': 'coat', 'ब्लेज़र': 'blazer',
        # Dresses
        'ड्रेस': 'dress', 'फ्रॉक': 'dress', 'कुर्ती': 'dress',
        # Knitwear
        'स्वेटर': 'sweater', 'हुडी': 'hoodie', 'हूडी': 'hoodie',
        # Footwear
        'जूते': 'shoes', 'जूता': 'shoes', 'चप्पल': 'sandals',
        'सैंडल': 'sandals', 'बूट': 'boots', 'स्नीकर': 'sneakers',
        'स्नीकर्स': 'sneakers',
        # Bags — NOTE: बाग = bag (also means garden, but in shopping context = bag)
        'बाग': 'bag', 'बैग': 'bag', 'थैला': 'bag', 'पर्स': 'bag',
        'बैकपैक': 'backpack', 'पीठ बैग': 'backpack',
        'लैपटॉप बैग': 'laptop bag', 'टोट': 'tote',
    },
    'ta': {
        'சட்டை': 'shirt', 'டி-ஷர்ட்': 't-shirt', 'டி ஷர்ட்': 't-shirt',
        'ஜீன்ஸ்': 'jeans', 'ஜீன்': 'jeans', 'பேண்ட்': 'pants',
        'ஜாக்கெட்': 'jacket', 'கோட்': 'coat', 'ப்ளேஸர்': 'blazer',
        'உடை': 'dress', 'காலணி': 'shoes', 'செருப்பு': 'sandals',
        'சாண்டல்': 'sandals', 'பூட்ஸ்': 'boots', 'ஸ்னீக்கர்': 'sneakers',
        'பை': 'bag', 'சீல்': 'bag', 'ஸ்வெட்டர்': 'sweater', 'ஹுடி': 'hoodie',
        'பேக்பேக்': 'backpack',
    },
    'te': {
        'చొక్కా': 'shirt', 'టీ-షర్ట్': 't-shirt', 'టీ షర్ట్': 't-shirt',
        'జీన్స్': 'jeans', 'పాంట్': 'pants', 'జాకెట్': 'jacket',
        'కోట్': 'coat', 'బ్లేజర్': 'blazer', 'దుస్తులు': 'dress',
        'చెప్పులు': 'shoes', 'శాండిల్': 'sandals', 'బూట్లు': 'boots',
        'స్నీకర్': 'sneakers', 'స్నీకర్లు': 'sneakers',
        'సంచి': 'bag', 'బ్యాగ్': 'bag', 'స్వెటర్': 'sweater', 'హుడీ': 'hoodie',
        'బ్యాక్‌పాక్': 'backpack',
    },
    'es': {
        'camisa': 'shirt', 'camiseta': 't-shirt', 'vaqueros': 'jeans',
        'pantalón': 'pants', 'pantalones': 'pants',
        'chaqueta': 'jacket', 'abrigo': 'coat', 'blazer': 'blazer',
        'vestido': 'dress', 'zapatos': 'shoes', 'sandalias': 'sandals',
        'botas': 'boots', 'zapatillas': 'sneakers',
        'bolso': 'bag', 'bolsa': 'bag', 'mochila': 'backpack',
        'suéter': 'sweater', 'sudadera': 'hoodie',
    },
    'fr': {
        'chemise': 'shirt', 't-shirt': 't-shirt', 'jean': 'jeans',
        'pantalon': 'pants', 'veste': 'jacket', 'manteau': 'coat',
        'blazer': 'blazer', 'robe': 'dress', 'chaussures': 'shoes',
        'sandales': 'sandals', 'bottes': 'boots', 'baskets': 'sneakers',
        'sac': 'bag', 'sac à dos': 'backpack',
        'pull': 'sweater', 'sweat': 'hoodie',
    },
    'de': {
        'hemd': 'shirt', 't-shirt': 't-shirt', 'jeans': 'jeans',
        'hose': 'pants', 'jacke': 'jacket', 'mantel': 'coat',
        'blazer': 'blazer', 'kleid': 'dress', 'schuhe': 'shoes',
        'sandalen': 'sandals', 'stiefel': 'boots', 'turnschuhe': 'sneakers',
        'tasche': 'bag', 'rucksack': 'backpack',
        'pullover': 'sweater', 'hoodie': 'hoodie',
    },
}

# Localized product name display (english_name → localized display name)
PRODUCT_NAME_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'hi': {
        'Cotton T-Shirt': 'कॉटन टी-शर्ट', 'Graphic T-Shirt': 'ग्राफिक टी-शर्ट',
        'Polo T-Shirt': 'पोलो टी-शर्ट', 'Cotton Shirt': 'कॉटन शर्ट',
        'Linen Shirt': 'लिनन शर्ट', 'Silk Shirt': 'सिल्क शर्ट',
        'Flannel Shirt': 'फ्लेनल शर्ट', 'Denim Jeans': 'डेनिम जींस',
        'Slim Fit Jeans': 'स्लिम फिट जींस', 'Chino Pants': 'चिनो पैंट',
        'Track Pants': 'ट्रैक पैंट', 'Silk Dress': 'सिल्क ड्रेस',
        'Cotton Dress': 'कॉटन ड्रेस', 'Floral Dress': 'फ्लोरल ड्रेस',
        'Party Dress': 'पार्टी ड्रेस', 'Winter Jacket': 'विंटर जैकेट',
        'Denim Jacket': 'डेनिम जैकेट', 'Leather Jacket': 'लेदर जैकेट',
        'Windbreaker Jacket': 'विंडब्रेकर जैकेट', 'Blazer': 'ब्लेज़र',
        'Woolen Sweater': 'ऊनी स्वेटर', 'Hoodie': 'हुडी',
        'Zip-Up Hoodie': 'जिप हुडी', 'Running Shoes': 'रनिंग जूते',
        'Casual Sneakers': 'कैजुअल स्नीकर', 'Leather Boots': 'लेदर बूट',
        'Sports Sandals': 'स्पोर्ट्स सैंडल', 'Formal Shoes': 'फॉर्मल जूते',
        'Slip-On Sneakers': 'स्लिप-ऑन स्नीकर', 'Leather Bag': 'लेदर बैग',
        'Canvas Backpack': 'कैनवस बैकपैक', 'Tote Bag': 'टोट बैग',
        'Laptop Bag': 'लैपटॉप बैग', 'Crossbody Bag': 'क्रॉसबॉडी बैग',
    },
    'ta': {
        'Cotton T-Shirt': 'பருத்தி டி-ஷர்ட்', 'Graphic T-Shirt': 'கிராபிக் டி-ஷர்ட்',
        'Polo T-Shirt': 'போலோ டி-ஷர்ட்', 'Cotton Shirt': 'பருத்தி சட்டை',
        'Linen Shirt': 'லினன் சட்டை', 'Silk Shirt': 'பட்டு சட்டை',
        'Flannel Shirt': 'பிளானல் சட்டை', 'Denim Jeans': 'டெனிம் ஜீன்ஸ்',
        'Slim Fit Jeans': 'ஸ்லிம் ஃபிட் ஜீன்ஸ்', 'Chino Pants': 'சினோ பேண்ட்',
        'Track Pants': 'ட்ராக் பேண்ட்', 'Silk Dress': 'பட்டு உடை',
        'Cotton Dress': 'பருத்தி உடை', 'Floral Dress': 'பூ உடை',
        'Party Dress': 'பார்ட்டி உடை', 'Winter Jacket': 'குளிர்கால ஜாக்கெட்',
        'Denim Jacket': 'டெனிம் ஜாக்கெட்', 'Leather Jacket': 'தோல் ஜாக்கெட்',
        'Windbreaker Jacket': 'விண்ட்பிரேக்கர்', 'Blazer': 'ப்ளேஸர்',
        'Woolen Sweater': 'கம்பளி ஸ்வெட்டர்', 'Hoodie': 'ஹுடி',
        'Zip-Up Hoodie': 'ஜிப் ஹுடி', 'Running Shoes': 'ஓட்ட காலணி',
        'Casual Sneakers': 'சாதாரண ஸ்னீக்கர்', 'Leather Boots': 'தோல் பூட்ஸ்',
        'Sports Sandals': 'விளையாட்டு சாண்டல்', 'Formal Shoes': 'அலுவல் காலணி',
        'Slip-On Sneakers': 'ஸ்லிப்-ஆன் ஸ்னீக்கர்', 'Leather Bag': 'தோல் பை',
        'Canvas Backpack': 'கேன்வாஸ் பேக்பேக்', 'Tote Bag': 'டோட் பை',
        'Laptop Bag': 'லேப்டாப் பை', 'Crossbody Bag': 'க்ராஸ்பாடி பை',
    },
    'te': {
        'Cotton T-Shirt': 'కాటన్ టీ-షర్ట్', 'Graphic T-Shirt': 'గ్రాఫిక్ టీ-షర్ట్',
        'Polo T-Shirt': 'పోలో టీ-షర్ట్', 'Cotton Shirt': 'కాటన్ చొక్కా',
        'Linen Shirt': 'లినన్ చొక్కా', 'Silk Shirt': 'సిల్క్ చొక్కా',
        'Flannel Shirt': 'ఫ్లానెల్ చొక్కా', 'Denim Jeans': 'డెనిమ్ జీన్స్',
        'Slim Fit Jeans': 'స్లిమ్ ఫిట్ జీన్స్', 'Chino Pants': 'చినో పాంట్',
        'Track Pants': 'ట్రాక్ పాంట్', 'Silk Dress': 'సిల్క్ దుస్తులు',
        'Cotton Dress': 'కాటన్ దుస్తులు', 'Floral Dress': 'పువ్వుల దుస్తులు',
        'Party Dress': 'పార్టీ దుస్తులు', 'Winter Jacket': 'వింటర్ జాకెట్',
        'Denim Jacket': 'డెనిమ్ జాకెట్', 'Leather Jacket': 'లెదర్ జాకెట్',
        'Windbreaker Jacket': 'విండ్‌బ్రేకర్', 'Blazer': 'బ్లేజర్',
        'Woolen Sweater': 'ఉన్ని స్వెటర్', 'Hoodie': 'హుడీ',
        'Zip-Up Hoodie': 'జిప్ హుడీ', 'Running Shoes': 'రన్నింగ్ చెప్పులు',
        'Casual Sneakers': 'కాజువల్ స్నీకర్', 'Leather Boots': 'లెదర్ బూట్లు',
        'Sports Sandals': 'స్పోర్ట్స్ శాండిల్', 'Formal Shoes': 'ఫార్మల్ చెప్పులు',
        'Slip-On Sneakers': 'స్లిప్-ఆన్ స్నీకర్', 'Leather Bag': 'లెదర్ సంచి',
        'Canvas Backpack': 'క్యాన్వాస్ బ్యాక్‌పాక్', 'Tote Bag': 'టోట్ సంచి',
        'Laptop Bag': 'లాప్‌టాప్ సంచి', 'Crossbody Bag': 'క్రాస్‌బాడీ సంచి',
    },
    'es': {
        'Cotton T-Shirt': 'Camiseta de Algodón', 'Graphic T-Shirt': 'Camiseta Gráfica',
        'Polo T-Shirt': 'Polo', 'Cotton Shirt': 'Camisa de Algodón',
        'Linen Shirt': 'Camisa de Lino', 'Silk Shirt': 'Camisa de Seda',
        'Flannel Shirt': 'Camisa de Franela', 'Denim Jeans': 'Vaqueros',
        'Slim Fit Jeans': 'Vaqueros Slim', 'Chino Pants': 'Pantalón Chino',
        'Track Pants': 'Pantalón Deportivo', 'Silk Dress': 'Vestido de Seda',
        'Cotton Dress': 'Vestido de Algodón', 'Floral Dress': 'Vestido Floral',
        'Party Dress': 'Vestido de Fiesta', 'Winter Jacket': 'Chaqueta de Invierno',
        'Denim Jacket': 'Chaqueta Vaquera', 'Leather Jacket': 'Chaqueta de Cuero',
        'Windbreaker Jacket': 'Cortavientos', 'Blazer': 'Blazer',
        'Woolen Sweater': 'Suéter de Lana', 'Hoodie': 'Sudadera',
        'Zip-Up Hoodie': 'Sudadera con Cremallera', 'Running Shoes': 'Zapatillas Running',
        'Casual Sneakers': 'Zapatillas Casuales', 'Leather Boots': 'Botas de Cuero',
        'Sports Sandals': 'Sandalias Deportivas', 'Formal Shoes': 'Zapatos Formales',
        'Slip-On Sneakers': 'Zapatillas sin Cordones', 'Leather Bag': 'Bolso de Cuero',
        'Canvas Backpack': 'Mochila de Lona', 'Tote Bag': 'Bolsa Tote',
        'Laptop Bag': 'Maletín para Portátil', 'Crossbody Bag': 'Bolso Bandolera',
    },
    'fr': {
        'Cotton T-Shirt': 'T-shirt en Coton', 'Graphic T-Shirt': 'T-shirt Graphique',
        'Polo T-Shirt': 'Polo', 'Cotton Shirt': 'Chemise en Coton',
        'Linen Shirt': 'Chemise en Lin', 'Silk Shirt': 'Chemise en Soie',
        'Flannel Shirt': 'Chemise en Flanelle', 'Denim Jeans': 'Jean Denim',
        'Slim Fit Jeans': 'Jean Slim', 'Chino Pants': 'Pantalon Chino',
        'Track Pants': 'Jogging', 'Silk Dress': 'Robe en Soie',
        'Cotton Dress': 'Robe en Coton', 'Floral Dress': 'Robe Fleurie',
        'Party Dress': 'Robe de Soirée', 'Winter Jacket': 'Veste d\'Hiver',
        'Denim Jacket': 'Veste en Jean', 'Leather Jacket': 'Veste en Cuir',
        'Windbreaker Jacket': 'Coupe-Vent', 'Blazer': 'Blazer',
        'Woolen Sweater': 'Pull en Laine', 'Hoodie': 'Sweat à Capuche',
        'Zip-Up Hoodie': 'Sweat Zippé', 'Running Shoes': 'Chaussures de Course',
        'Casual Sneakers': 'Baskets Casual', 'Leather Boots': 'Bottes en Cuir',
        'Sports Sandals': 'Sandales de Sport', 'Formal Shoes': 'Chaussures Formelles',
        'Slip-On Sneakers': 'Baskets sans Lacets', 'Leather Bag': 'Sac en Cuir',
        'Canvas Backpack': 'Sac à Dos en Toile', 'Tote Bag': 'Tote Bag',
        'Laptop Bag': 'Sacoche pour Ordinateur', 'Crossbody Bag': 'Sac Bandoulière',
    },
    'de': {
        'Cotton T-Shirt': 'Baumwoll-T-Shirt', 'Graphic T-Shirt': 'Grafik-T-Shirt',
        'Polo T-Shirt': 'Poloshirt', 'Cotton Shirt': 'Baumwollhemd',
        'Linen Shirt': 'Leinenhemd', 'Silk Shirt': 'Seidenhemd',
        'Flannel Shirt': 'Flanellhemd', 'Denim Jeans': 'Denim-Jeans',
        'Slim Fit Jeans': 'Slim-Fit-Jeans', 'Chino Pants': 'Chinohose',
        'Track Pants': 'Trainingshose', 'Silk Dress': 'Seidenkleid',
        'Cotton Dress': 'Baumwollkleid', 'Floral Dress': 'Blumenkleid',
        'Party Dress': 'Partykleid', 'Winter Jacket': 'Winterjacke',
        'Denim Jacket': 'Jeansjacke', 'Leather Jacket': 'Lederjacke',
        'Windbreaker Jacket': 'Windbreaker', 'Blazer': 'Blazer',
        'Woolen Sweater': 'Wollpullover', 'Hoodie': 'Kapuzenpullover',
        'Zip-Up Hoodie': 'Zip-Hoodie', 'Running Shoes': 'Laufschuhe',
        'Casual Sneakers': 'Freizeitschuhe', 'Leather Boots': 'Lederstiefel',
        'Sports Sandals': 'Sportsandalen', 'Formal Shoes': 'Formelle Schuhe',
        'Slip-On Sneakers': 'Slip-On-Sneaker', 'Leather Bag': 'Ledertasche',
        'Canvas Backpack': 'Canvas-Rucksack', 'Tote Bag': 'Tragetasche',
        'Laptop Bag': 'Laptoptasche', 'Crossbody Bag': 'Umhängetasche',
    },
}

SIZE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'hi': {'छोटा': 'small', 'मध्यम': 'medium', 'बड़ा': 'large'},
    'ta': {'சிறியது': 'small', 'நடுத்தரம்': 'medium', 'பெரியது': 'large'},
    'te': {'చిన్నది': 'small', 'మధ్యమం': 'medium', 'పెద్దది': 'large'},
    'es': {'pequeño': 'small', 'mediano': 'medium', 'grande': 'large', 'pequeña': 'small'},
    'fr': {'petit': 'small', 'moyen': 'medium', 'grand': 'large', 'petite': 'small'},
    'de': {'klein': 'small', 'mittel': 'medium', 'groß': 'large'},
}

# Quantity words per language → digit word for NLP
QUANTITY_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'hi': {
        'एक': '1', 'दो': '2', 'तीन': '3', 'चार': '4',
        'पाँच': '5', 'पांच': '5',
    },
    'ta': {
        'ஒரு': '1', 'இரண்டு': '2', 'மூன்று': '3', 'நான்கு': '4',
    },
    'te': {
        'ఒక': '1', 'రెండు': '2', 'మూడు': '3', 'నాలుగు': '4',
    },
    'es': { 'dos': '2', 'tres': '3', 'cuatro': '4' },
    'fr': { 'deux': '2', 'trois': '3', 'quatre': '4' },
    'de': { 'zwei': '2', 'drei': '3', 'vier': '4' },
}

# Material translations per language → English
MATERIAL_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'hi': {
        'कॉटन': 'cotton', 'कपास': 'cotton', 'रेशम': 'silk', 'सिल्क': 'silk',
        'ऊन': 'wool', 'वूलन': 'wool', 'डेनिम': 'denim', 'लेदर': 'leather',
        'चमड़ा': 'leather', 'लिनन': 'linen', 'फ्लीस': 'fleece',
    },
    'ta': {
        'பருத்தி': 'cotton', 'பட்டு': 'silk', 'கம்பளி': 'wool',
        'டெனிம்': 'denim', 'தோல்': 'leather',
    },
    'te': {
        'కాటన్': 'cotton', 'పత్తి': 'cotton', 'సిల్క్': 'silk',
        'ఉన్ని': 'wool', 'డెనిమ్': 'denim', 'లెదర్': 'leather',
    },
    'es': {
        'algodón': 'cotton', 'seda': 'silk', 'lana': 'wool',
        'cuero': 'leather', 'lino': 'linen',
    },
    'fr': {
        'coton': 'cotton', 'soie': 'silk', 'laine': 'wool',
        'cuir': 'leather', 'lin': 'linen',
    },
    'de': {
        'baumwolle': 'cotton', 'seide': 'silk', 'wolle': 'wool',
        'leder': 'leather', 'leinen': 'linen',
    },
}

UI_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
        'greeting': "Hello! I'm your AI shopping assistant. Try commands like:",
        'example1': '"Add two medium blue cotton shirts under ₹600"',
        'example2': '"Show me my cart"',
        'example3': '"Search for red dresses"',
        'example4': '"Remove the blue shirt"',
        'example5': '"Proceed to checkout"',
        'placeholder': 'Type your shopping command or click the mic...',
        'view_cart': 'View Cart', 'find_shirts': 'Find Shirts',
        'add_shirt': 'Add Shirt', 'checkout': 'Checkout',
        'clear_cart': 'Clear Cart', 'available_products': 'Available Products',
        'development_team': 'Development Team',
        'team_subtitle': 'Meet the minds behind this project',
        'shopping_cart': 'Shopping Cart', 'cart_empty': 'Your cart is empty',
        'total': 'Total', 'send': 'Send', 'processing': 'Processing your command...',
        'nlp_analysis': 'NLP Analysis', 'intent': 'Intent',
        'entities': 'Entities', 'confidence': 'Confidence',
        'cart_items': 'items in cart', 'select_language': 'Language',
        'add_to_cart': 'Add to Cart', 'quick_commands': 'Quick Commands',
        'voice_assistant': 'Voice Shopping Assistant',
        'voice_subtitle': 'Speak or type your shopping commands naturally',
        'listening': 'Listening... Speak now',
        'session_stats': 'Session Stats', 'commands': 'Commands',
        'accuracy': 'Accuracy', 'cart_total': 'Cart Total',
    },
    'hi': {
        'greeting': "नमस्ते! मैं आपका AI शॉपिंग असिस्टेंट हूं। कोशिश करें:",
        'example1': '"दो मध्यम नीली कॉटन शर्ट ₹600 से कम में जोड़ो"',
        'example2': '"मेरा कार्ट दिखाओ"',
        'example3': '"लाल ड्रेस खोजो"',
        'example4': '"नीली शर्ट हटाओ"',
        'example5': '"checkout karo"',
        'placeholder': 'शॉपिंग कमांड टाइप करें या माइक क्लिक करें...',
        'view_cart': 'कार्ट देखें', 'find_shirts': 'शर्ट खोजें',
        'add_shirt': 'शर्ट जोड़ें', 'checkout': 'चेकआउट',
        'clear_cart': 'कार्ट साफ करें', 'available_products': 'उपलब्ध उत्पाद',
        'development_team': 'डेवलपमेंट टीम',
        'team_subtitle': 'इस प्रोजेक्ट के पीछे की टीम',
        'shopping_cart': 'शॉपिंग कार्ट', 'cart_empty': 'आपका कार्ट खाली है',
        'total': 'कुल', 'send': 'भेजें', 'processing': 'कमांड प्रोसेस हो रहा है...',
        'nlp_analysis': 'NLP विश्लेषण', 'intent': 'इरादा',
        'entities': 'संस्थाएं', 'confidence': 'विश्वास',
        'cart_items': 'आइटम कार्ट में', 'select_language': 'भाषा',
        'add_to_cart': 'कार्ट में जोड़ें', 'quick_commands': 'त्वरित कमांड',
        'voice_assistant': 'वॉयस शॉपिंग असिस्टेंट',
        'voice_subtitle': 'स्वाभाविक रूप से बोलें या टाइप करें',
        'listening': 'सुन रहा हूं... बोलिए',
        'session_stats': 'सत्र आंकड़े', 'commands': 'कमांड',
        'accuracy': 'सटीकता', 'cart_total': 'कार्ट कुल',
    },
    'ta': {
        'greeting': "வணக்கம்! நான் உங்கள் AI ஷாப்பிங் உதவியாளர். இப்படி முயற்சிக்கவும்:",
        'example1': '"இரண்டு நீல பருத்தி சட்டைகள் ₹600க்கு கீழ் சேர்க்க"',
        'example2': '"என் cart காட்டு"',
        'example3': '"சிவப்பு உடைகள் தேடு"',
        'example4': '"நீல சட்டை நீக்க"',
        'example5': '"checkout செய்"',
        'placeholder': 'ஷாப்பிங் கமாண்ட் தட்டச்சு செய்யவும் அல்லது மைக் கிளிக் செய்யவும்...',
        'view_cart': 'Cart பார்', 'find_shirts': 'சட்டை தேடு',
        'add_shirt': 'சட்டை சேர்', 'checkout': 'Checkout',
        'clear_cart': 'Cart அழி', 'available_products': 'கிடைக்கும் பொருட்கள்',
        'development_team': 'டெவலப்மெண்ட் டீம்',
        'team_subtitle': 'இந்த திட்டத்தின் பின்னணியில் உள்ளவர்கள்',
        'shopping_cart': 'ஷாப்பிங் Cart', 'cart_empty': 'உங்கள் cart காலியாக உள்ளது',
        'total': 'மொத்தம்', 'send': 'அனுப்பு', 'processing': 'உங்கள் கமாண்ட் செயலாக்கப்படுகிறது...',
        'nlp_analysis': 'NLP பகுப்பாய்வு', 'intent': 'நோக்கம்',
        'entities': 'அட்டவணை', 'confidence': 'நம்பகத்தன்மை',
        'cart_items': 'cart இல் உள்ள பொருட்கள்', 'select_language': 'மொழி',
        'add_to_cart': 'Cart இல் சேர்', 'quick_commands': 'விரைவு கமாண்டுகள்',
        'voice_assistant': 'குரல் ஷாப்பிங் உதவியாளர்',
        'voice_subtitle': 'இயற்கையாக பேசவும் அல்லது தட்டச்சு செய்யவும்',
        'listening': 'கேட்கிறேன்... பேசுங்கள்',
        'session_stats': 'அமர்வு புள்ளிவிவரங்கள்', 'commands': 'கமாண்டுகள்',
        'accuracy': 'துல்லியம்', 'cart_total': 'Cart மொத்தம்',
    },
    'te': {
        'greeting': "నమస్కారం! నేను మీ AI షాపింగ్ అసిస్టెంట్. ఇలా ప్రయత్నించండి:",
        'example1': '"రెండు మీడియం నీలి కాటన్ చొక్కాలు ₹600 కంటే తక్కువకు చేర్చు"',
        'example2': '"నా cart చూపించు"',
        'example3': '"ఎర్ర దుస్తులు వెతుకు"',
        'example4': '"నీలి చొక్కా తీసివేయి"',
        'example5': '"checkout చేయి"',
        'placeholder': 'షాపింగ్ కమాండ్ టైప్ చేయండి లేదా మైక్ క్లిక్ చేయండి...',
        'view_cart': 'Cart చూడు', 'find_shirts': 'చొక్కాలు వెతుకు',
        'add_shirt': 'చొక్కా చేర్చు', 'checkout': 'Checkout',
        'clear_cart': 'Cart క్లియర్', 'available_products': 'అందుబాటులో ఉన్న ఉత్పత్తులు',
        'development_team': 'డెవలప్మెంట్ టీమ్',
        'team_subtitle': 'ఈ ప్రాజెక్ట్ వెనుక ఉన్న బృందం',
        'shopping_cart': 'షాపింగ్ Cart', 'cart_empty': 'మీ cart ఖాళీగా ఉంది',
        'total': 'మొత్తం', 'send': 'పంపు', 'processing': 'మీ కమాండ్ ప్రాసెస్ అవుతోంది...',
        'nlp_analysis': 'NLP విశ్లేషణ', 'intent': 'ఉద్దేశం',
        'entities': 'సంస్థలు', 'confidence': 'విశ్వాసం',
        'cart_items': 'cart లో వస్తువులు', 'select_language': 'భాష',
        'add_to_cart': 'Cart కి చేర్చు', 'quick_commands': 'త్వరిత కమాండ్లు',
        'voice_assistant': 'వాయిస్ షాపింగ్ అసిస్టెంట్',
        'voice_subtitle': 'సహజంగా మాట్లాడండి లేదా టైప్ చేయండి',
        'listening': 'వింటున్నాను... మాట్లాడండి',
        'session_stats': 'సెషన్ గణాంకాలు', 'commands': 'కమాండ్లు',
        'accuracy': 'ఖచ్చితత్వం', 'cart_total': 'Cart మొత్తం',
    },
    'es': {
        'greeting': "¡Hola! Soy tu asistente de compras AI. Prueba:",
        'example1': '"Agregar dos camisas azules medianas bajo ₹600"',
        'example2': '"Mostrar mi carrito"',
        'example3': '"Buscar vestidos rojos"',
        'example4': '"Quitar la camisa azul"',
        'example5': '"Proceder al pago"',
        'placeholder': 'Escribe tu comando o haz clic en el micrófono...',
        'view_cart': 'Ver Carrito', 'find_shirts': 'Buscar Camisas',
        'add_shirt': 'Agregar Camisa', 'checkout': 'Pagar',
        'clear_cart': 'Vaciar Carrito', 'available_products': 'Productos Disponibles',
        'development_team': 'Equipo de Desarrollo',
        'team_subtitle': 'El equipo detrás del proyecto',
        'shopping_cart': 'Carrito', 'cart_empty': 'Tu carrito está vacío',
        'total': 'Total', 'send': 'Enviar', 'processing': 'Procesando...',
        'nlp_analysis': 'Análisis NLP', 'intent': 'Intención',
        'entities': 'Entidades', 'confidence': 'Confianza',
        'cart_items': 'artículos', 'select_language': 'Idioma',
        'add_to_cart': 'Agregar', 'quick_commands': 'Comandos Rápidos',
        'voice_assistant': 'Asistente de Voz',
        'voice_subtitle': 'Habla o escribe tus comandos',
        'listening': 'Escuchando... Habla ahora',
        'session_stats': 'Estadísticas', 'commands': 'Comandos',
        'accuracy': 'Precisión', 'cart_total': 'Total',
    },
    'fr': {
        'greeting': "Bonjour! Je suis votre assistant IA. Essayez:",
        'example1': '"Ajouter deux chemises bleues en coton sous ₹600"',
        'example2': '"Afficher mon panier"',
        'example3': '"Chercher des robes rouges"',
        'example4': '"Retirer la chemise bleue"',
        'example5': '"Procéder au paiement"',
        'placeholder': 'Tapez votre commande ou cliquez sur le micro...',
        'view_cart': 'Voir Panier', 'find_shirts': 'Chercher Chemises',
        'add_shirt': 'Ajouter Chemise', 'checkout': 'Payer',
        'clear_cart': 'Vider Panier', 'available_products': 'Produits Disponibles',
        'development_team': 'Équipe de Développement',
        'team_subtitle': "L'équipe derrière le projet",
        'shopping_cart': 'Panier', 'cart_empty': 'Votre panier est vide',
        'total': 'Total', 'send': 'Envoyer', 'processing': 'Traitement...',
        'nlp_analysis': 'Analyse NLP', 'intent': 'Intention',
        'entities': 'Entités', 'confidence': 'Confiance',
        'cart_items': 'articles', 'select_language': 'Langue',
        'add_to_cart': 'Ajouter', 'quick_commands': 'Commandes Rapides',
        'voice_assistant': 'Assistant Vocal',
        'voice_subtitle': 'Parlez ou tapez vos commandes',
        'listening': 'Écoute... Parlez maintenant',
        'session_stats': 'Statistiques', 'commands': 'Commandes',
        'accuracy': 'Précision', 'cart_total': 'Total Panier',
    },
    'de': {
        'greeting': "Hallo! Ich bin Ihr KI-Assistent. Versuchen Sie:",
        'example1': '"Zwei blaue Baumwollhemden unter ₹600 hinzufügen"',
        'example2': '"Warenkorb anzeigen"',
        'example3': '"Rote Kleider suchen"',
        'example4': '"Blaues Hemd entfernen"',
        'example5': '"Zur Kasse gehen"',
        'placeholder': 'Befehl eingeben oder Mikrofon klicken...',
        'view_cart': 'Warenkorb', 'find_shirts': 'Hemden suchen',
        'add_shirt': 'Hemd hinzufügen', 'checkout': 'Kasse',
        'clear_cart': 'Warenkorb leeren', 'available_products': 'Produkte',
        'development_team': 'Entwicklungsteam',
        'team_subtitle': 'Das Team hinter dem Projekt',
        'shopping_cart': 'Warenkorb', 'cart_empty': 'Warenkorb ist leer',
        'total': 'Gesamt', 'send': 'Senden', 'processing': 'Verarbeitung...',
        'nlp_analysis': 'NLP-Analyse', 'intent': 'Absicht',
        'entities': 'Entitäten', 'confidence': 'Konfidenz',
        'cart_items': 'Artikel', 'select_language': 'Sprache',
        'add_to_cart': 'Hinzufügen', 'quick_commands': 'Schnellbefehle',
        'voice_assistant': 'Sprach-Assistent',
        'voice_subtitle': 'Sprechen oder tippen Sie Ihre Befehle',
        'listening': 'Höre zu... Sprechen Sie',
        'session_stats': 'Sitzungsstatistik', 'commands': 'Befehle',
        'accuracy': 'Genauigkeit', 'cart_total': 'Warenkorb Gesamt',
    },
}

LANGUAGE_PATTERNS: Dict[str, list] = {
    'hi': ['जोड़', 'हटा', 'खोज', 'दिखा', 'कार्ट', 'checkout karo', 'dalo', 'dikhao'],
    'ta': ['சேர்க்க', 'நீக்க', 'தேடு', 'காட்டு', 'cart', 'வேண்டும்', 'சட்டை'],
    'te': ['చేర్చు', 'తీసివేయి', 'వెతుకు', 'చూపించు', 'cart', 'కావాలి', 'చొక్కా'],
    'es': ['agregar', 'añadir', 'quitar', 'buscar', 'carrito', 'pagar', 'mostrar'],
    'fr': ['ajouter', 'retirer', 'chercher', 'panier', 'payer', 'afficher'],
    'de': ['hinzufügen', 'entfernen', 'suchen', 'warenkorb', 'bezahlen', 'zeigen'],
}

LANGUAGE_CODES: Dict[str, str] = {
    'en': 'en-US',
    'hi': 'hi-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
    'es': 'es-ES',
    'fr': 'fr-FR',
    'de': 'de-DE',
}

# Flag emojis for UI
LANGUAGE_FLAGS: Dict[str, str] = {
    'en': '🇺🇸', 'hi': '🇮🇳', 'ta': '🇮🇳', 'te': '🇮🇳',
    'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
}


class MultilingualProcessor:
    """Handles language detection and translation of shopping commands."""

    def __init__(self):
        self.current_language = 'en'

    def detect_language(self, text: str) -> str:
        for lang, patterns in LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text.lower():
                    return lang
        return 'en'

    def translate_to_english(self, text: str, lang: Optional[str] = None) -> Tuple[str, str]:
        if lang is None:
            lang = self.detect_language(text)
        if lang == 'en':
            return text, 'en'

        translated = text
        canon_map = {'add': 'add', 'remove': 'remove', 'search': 'search',
                     'view': 'show cart', 'checkout': 'checkout'}

        # Translate intent keywords
        for intent, keywords in INTENT_TRANSLATIONS.get(lang, {}).items():
            # longest keywords first to avoid partial replacements
            for kw in sorted(keywords, key=len, reverse=True):
                if kw.lower() in translated.lower():
                    translated = re.sub(re.escape(kw), canon_map[intent], translated, flags=re.IGNORECASE)

        # Translate colors
        for native, english in sorted(COLOR_TRANSLATIONS.get(lang, {}).items(), key=lambda x: len(x[0]), reverse=True):
            translated = re.sub(re.escape(native), english, translated, flags=re.IGNORECASE)

        # Translate product types (longest first — "ट्रैक पैंट" before "पैंट")
        for native, english in sorted(PRODUCT_TRANSLATIONS.get(lang, {}).items(), key=lambda x: len(x[0]), reverse=True):
            translated = re.sub(re.escape(native), english, translated, flags=re.IGNORECASE)

        # Translate sizes
        for native, english in sorted(SIZE_TRANSLATIONS.get(lang, {}).items(), key=lambda x: len(x[0]), reverse=True):
            translated = re.sub(re.escape(native), english, translated, flags=re.IGNORECASE)

        # Translate quantity words
        for native, english in sorted(QUANTITY_TRANSLATIONS.get(lang, {}).items(), key=lambda x: len(x[0]), reverse=True):
            translated = re.sub(r'\b' + re.escape(native) + r'\b', english, translated, flags=re.IGNORECASE)

        # Translate materials
        for native, english in sorted(MATERIAL_TRANSLATIONS.get(lang, {}).items(), key=lambda x: len(x[0]), reverse=True):
            translated = re.sub(re.escape(native), english, translated, flags=re.IGNORECASE)

        return translated, lang

    def localize_product_name(self, english_name: str, lang: str) -> str:
        """Return the localized display name for a product."""
        if lang == 'en':
            return english_name
        return PRODUCT_NAME_TRANSLATIONS.get(lang, {}).get(english_name, english_name)

    def get_ui_translations(self, lang: str) -> Dict[str, str]:
        return UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS['en'])

    def get_speech_lang_code(self, lang: str) -> str:
        return LANGUAGE_CODES.get(lang, 'en-US')
