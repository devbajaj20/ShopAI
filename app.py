"""
Flask API Backend — NLP Shopping Cart
Deploy on Render. Frontend is separate (Vercel).
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import VoiceShoppingAssistant
from nlp.multilingual import (
    MultilingualProcessor, SUPPORTED_LANGUAGES,
    UI_TRANSLATIONS, LANGUAGE_CODES, LANGUAGE_FLAGS
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nlp_shopping_cart_secret_key_2024')

# Allow requests from the Vercel frontend
FRONTEND_URL = os.environ.get('FRONTEND_URL', '*')
CORS(app, origins=FRONTEND_URL, supports_credentials=True)

user_sessions = {}
multilingual = MultilingualProcessor()


def get_or_create_assistant(session_id):
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'assistant': VoiceShoppingAssistant(use_voice=False),
            'language': 'en'
        }
    return user_sessions[session_id]


# ── Bootstrap endpoint — replaces Jinja2 template rendering ──────────────
@app.route('/api/bootstrap')
def bootstrap():
    """Return all data the frontend needs on first load."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    lang = session.get('language', 'en')
    return jsonify({
        'session_id':          session['session_id'],
        'current_lang':        lang,
        'speech_lang':         LANGUAGE_CODES.get(lang, 'en-US'),
        'translations':        UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS['en']),
        'supported_languages': SUPPORTED_LANGUAGES,
        'language_flags':      LANGUAGE_FLAGS,
    })


@app.route('/api/set_language', methods=['POST'])
def set_language():
    data = request.get_json()
    lang = data.get('language', 'en')
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({'success': False, 'message': 'Unsupported language'})

    session['language'] = lang
    session_id = session.get('session_id')
    if session_id and session_id in user_sessions:
        user_sessions[session_id]['language'] = lang

    return jsonify({
        'success':      True,
        'language':     lang,
        'translations': UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS['en']),
        'speech_lang':  LANGUAGE_CODES.get(lang, 'en-US')
    })


@app.route('/api/process_command', methods=['POST'])
def process_command():
    try:
        data    = request.get_json()
        command = data.get('command', '').strip()
        lang    = data.get('language', session.get('language', 'en'))
        sid     = data.get('session_id') or session.get('session_id')

        if not sid:
            sid = str(uuid.uuid4())
        session['session_id'] = sid

        if not command:
            return jsonify({'success': False, 'message': 'Please enter a command'})

        sess      = get_or_create_assistant(sid)
        assistant = sess['assistant']

        translated_command, detected_lang = multilingual.translate_to_english(command, lang)

        result      = assistant.process_command(translated_command)
        response    = assistant.format_response(result)
        cart_summary = assistant.shopping_cart.get_cart_summary()

        return jsonify({
            'success':            True,
            'command':            command,
            'translated_command': translated_command,
            'detected_language':  detected_lang,
            'intent':             result.get('intent', 'unknown'),
            'confidence':         result.get('confidence', 0),
            'response':           response,
            'cart_summary':       cart_summary,
            'entities':           result.get('entities').__dict__ if result.get('entities') else {}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/api/get_cart')
def get_cart():
    try:
        sid  = request.args.get('session_id') or session.get('session_id')
        sess = get_or_create_assistant(sid)
        return jsonify({'success': True, 'cart_summary': sess['assistant'].shopping_cart.get_cart_summary()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/get_products')
def get_products():
    try:
        sid  = request.args.get('session_id') or session.get('session_id')
        lang = request.args.get('lang', session.get('language', 'en'))
        sess = get_or_create_assistant(sid)
        products = [
            {
                'id':           p.id,
                'name':         p.name,
                'display_name': multilingual.localize_product_name(p.name, lang),
                'price':        p.price,
                'category':     p.category,
                'size':         p.size,
                'color':        p.color,
                'material':     p.material,
                'brand':        p.brand
            }
            for p in sess['assistant'].shopping_cart.catalog
        ]
        return jsonify({'success': True, 'products': products})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/clear_cart', methods=['POST'])
def clear_cart():
    try:
        data = request.get_json() or {}
        sid  = data.get('session_id') or session.get('session_id')
        sess = get_or_create_assistant(sid)
        sess['assistant'].shopping_cart.clear_cart()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        data   = request.get_json() or {}
        sid    = data.get('session_id') or session.get('session_id')
        sess   = get_or_create_assistant(sid)
        result = sess['assistant'].shopping_cart.checkout()
        return jsonify({'success': result['success'], 'checkout_result': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
