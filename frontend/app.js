
'use strict';

/*
 * ShopAI frontend
 * Requires config.js to define API_BASE before this file loads.
 *
 * IMPORTANT:
 * Confirm the API paths in API below against your Flask backend.
 */


const API = {
    bootstrap: '/api/bootstrap',
    setLanguage: '/api/set_language',
    products: '/api/get_products',
    cart: '/api/get_cart',
    command: '/api/process_command',
    clearCart: '/api/clear_cart',
    checkout: '/api/checkout'
};


class ShoppingAssistant {
    constructor() {
        this.lang = 'en';
        this.speechLang = 'en-US';
        this.t = {};
        this.allLangs = {};
        this.langFlags = {};
        this.sessionId = localStorage.getItem('shopai_session') || null;
        this.recognition = null;
        this.isRecording = false;
        this.cartOpen = false;
        this.allProducts = [];
        this.cartItems = [];
        this.commandCount = 0;
        this.totalConfidence = 0;
        this.busy = false;

        this._boot();
    }

    async _request(path, options = {}) {
        if (typeof API_BASE === 'undefined') {
            throw new Error('API_BASE is missing from config.js');
        }

        const headers = {
            ...(options.body ? { 'Content-Type': 'application/json' } : {}),
            ...(options.headers || {})
        };

        const response = await fetch(`${API_BASE}${path}`, {
            credentials: 'include',
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(`Request failed: HTTP ${response.status}`);
        }

        return response.json();
    }

    // --------------------------------------------------
    // Bootstrap
    // --------------------------------------------------

    async _boot() {
        try {
            const data = await this._request(API.bootstrap);

            this.sessionId = data.session_id || this.sessionId;
            this.lang = data.current_lang || 'en';
            this.speechLang = data.speech_lang || 'en-US';
            this.t = data.translations || {};
            this.allLangs = data.supported_languages || {};
            this.langFlags = data.language_flags || {};

            if (this.sessionId) {
                localStorage.setItem('shopai_session', this.sessionId);
            }

            this._buildLangGrid();
            this._applyTranslations(this.t);
            this._setGreeting();
            this._initSpeech();

            await this.loadProducts();
            await this.updateCart();

            this._setStatus('Ready');
        } catch (error) {
            console.error('ShopAI bootstrap failed:', error);
            this._setStatus('Offline');

            const greeting = document.getElementById('greeting-text');
            if (greeting) {
                greeting.textContent =
                    'Unable to connect to ShopAI. Check your backend URL and API routes.';
            }

            this._toast('Could not connect to the backend.', 'error');
        }
    }

    // --------------------------------------------------
    // Languages and translations
    // --------------------------------------------------

    _buildLangGrid() {
        const grid = document.getElementById('lang-grid');
        if (!grid) return;

        grid.replaceChildren();

        Object.entries(this.allLangs).forEach(([code, name]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className =
                `lang-btn${code === this.lang ? ' active' : ''}`;
            button.dataset.lang = code;
            button.title = name;
            button.textContent =
                `${this.langFlags[code] || ''} ${code.toUpperCase()}`;

            button.addEventListener('click', () => this.setLanguage(code));
            grid.appendChild(button);
        });
    }

    async setLanguage(lang) {
        try {
            const data = await this._request(API.setLanguage, {
                method: 'POST',
                body: JSON.stringify({ language: lang })
            });

            if (data.success === false) {
                throw new Error(data.message || 'Language change failed');
            }

            this.lang = data.current_lang || lang;
            this.speechLang = data.speech_lang || this.speechLang;
            this.t = data.translations || this.t;

            this._buildLangGrid();
            this._applyTranslations(this.t);
            this._setGreeting();
            this._initSpeech();

            this._toast(`Language changed to ${this.allLangs[lang] || lang}`);
        } catch (error) {
            console.error('Language change failed:', error);
            this._toast('Could not change language.', 'error');
        }
    }

    _applyTranslations(translations) {
        document.querySelectorAll('[data-t]').forEach(element => {
            const key = element.dataset.t;
            if (translations[key] !== undefined) {
                element.textContent = translations[key];
            }
        });
    }

    _setGreeting() {
        const greeting = document.getElementById('greeting-text');
        const examples = document.getElementById('greeting-examples');

        if (greeting) {
            greeting.textContent =
                this.t.greeting ||
                'Hello! I am ShopAI. What would you like to shop for today?';
        }

        if (examples) {
            examples.replaceChildren();

            const items = this.t.examples || [
                'Find shirts',
                'Show my cart',
                'Add a shirt to my cart',
                'Checkout'
            ];

            if (Array.isArray(items)) {
                items.forEach(example => {
                    const li = document.createElement('li');
                    li.textContent = example;
                    examples.appendChild(li);
                });
            }
        }
    }

    // --------------------------------------------------
    // Speech recognition
    // --------------------------------------------------

    _initSpeech() {
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        this.recognition = null;

        if (!SpeechRecognition) {
            const button = document.getElementById('voice-btn');
            if (button) {
                button.title = 'Speech recognition is not supported in this browser';
            }
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = this.speechLang;
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            this.isRecording = true;
            this._setStatus('Listening');
            const button = document.getElementById('voice-btn');
            if (button) button.classList.add('recording');
        };

        recognition.onresult = event => {
            const transcript = event.results[0][0].transcript;
            const input = document.getElementById('command-input');

            if (input) input.value = transcript;
            this.sendCommand(transcript);
        };

        recognition.onerror = event => {
            console.error('Speech recognition error:', event.error);
            this._toast('Voice recognition failed. You can type your command instead.', 'error');
        };

        recognition.onend = () => {
            this.isRecording = false;
            this._setStatus('Ready');

            const button = document.getElementById('voice-btn');
            if (button) button.classList.remove('recording');
        };

        this.recognition = recognition;
    }

    toggleVoice() {
        if (!this.recognition) {
            this._toast('Voice recognition is unavailable. Try Chrome or type your command.', 'error');
            return;
        }

        if (this.isRecording) {
            this.recognition.stop();
        } else {
            try {
                this.recognition.start();
            } catch (error) {
                console.error(error);
                this._toast('Could not start voice recognition.', 'error');
            }
        }
    }

    // --------------------------------------------------
    // Chat and shopping commands
    // --------------------------------------------------

    async sendQuick(command) {
        const input = document.getElementById('command-input');
        if (input) input.value = command;
        await this.sendCommand(command);
    }

    async sendCommand(text) {
        const input = document.getElementById('command-input');
        const command = (text || (input && input.value) || '').trim();

        if (!command || this.busy) return;

        if (input) input.value = '';

        this._addMessage(command, 'user');
        this.commandCount++;
        this._updateStats();
        this._setStatus('Processing');

        this.busy = true;
        this._showLoading(true);

        try {
            const payload = {
                command,
                message: command,
                language: this.lang,
                session_id: this.sessionId
            };

            const data = await this._request(API.command, {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (data.success === false) {
    throw new Error(data.message || 'Command processing failed');
}


            const reply =
                data.response ||
                data.reply ||
                data.message ||
                data.text ||
                'Your command was processed.';

            this._addMessage(String(reply), 'bot');

            const confidence = Number(data.confidence);
            if (Number.isFinite(confidence)) {
                this.totalConfidence += confidence;
                this._updateStats();
            }

            if (data.intent || data.entities || data.confidence !== undefined) {
                this._showNlpDetails(data);
            }

            // Refresh server-backed state after a command.
            

if (data.session_id) {
    this.sessionId = data.session_id;
    localStorage.setItem('shopai_session', data.session_id);
}

if (data.cart_summary) {
    await this.updateCart(data);
} else {
    await this.updateCart();
}


            if (data.products || data.results) {
                this._renderProducts(data.products || data.results);
            } else if (/shirt|shoe|product|search|show/i.test(command)) {
                await this.loadProducts();
            }

        } catch (error) {
            console.error('Command failed:', error);
            this._addMessage(
                'I could not process that command. Please check the backend API and try again.',
                'bot'
            );
        } finally {
            this.busy = false;
            this._showLoading(false);
            this._setStatus('Ready');
        }
    }

    _addMessage(message, sender) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const wrapper = document.createElement('div');
        wrapper.className = `msg msg-${sender === 'user' ? 'user' : 'bot'}`;

        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        const icon = document.createElement('i');
        icon.className = sender === 'user'
            ? 'fas fa-user'
            : 'fas fa-robot';
        avatar.appendChild(icon);

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';

        const paragraph = document.createElement('p');
        paragraph.textContent = message;
        bubble.appendChild(paragraph);

        wrapper.append(avatar, bubble);
        container.appendChild(wrapper);
        container.scrollTop = container.scrollHeight;
    }

    _showNlpDetails(data) {
        const strip = document.getElementById('nlp-strip');
        const content = document.getElementById('nlp-strip-content');

        if (!strip || !content) return;

        const details = [];
        if (data.intent) details.push(`Intent: ${data.intent}`);
        if (data.confidence !== undefined) {
            details.push(`Confidence: ${data.confidence}`);
        }
        if (data.entities) {
            details.push(`Entities: ${JSON.stringify(data.entities)}`);
        }

        content.textContent = details.join(' · ');
        strip.classList.add('visible');
    }

    // --------------------------------------------------
    // Products and filters
    // --------------------------------------------------


async loadProducts() {
    const list = document.getElementById('products-list');

    try {
        if (list) list.textContent = 'Loading products...';

        const params = new URLSearchParams({
            session_id: this.sessionId || '',
            lang: this.lang || 'en'
        });

        const data = await this._request(
            `${API.products}?${params.toString()}`
        );

        if (data.success === false) {
            throw new Error(data.message || 'Could not load products');
        }

        this.allProducts = data.products || [];
        this.applyFilters();

    } catch (error) {
        console.error('Product loading failed:', error);

        if (list) {
            list.textContent = 'Unable to load products.';
        }
    }
}

    applyFilters() {
        const search = (
            document.getElementById('product-search')?.value || ''
        ).trim().toLowerCase();

        const category =
            document.getElementById('filter-category')?.value || '';

        const maxPrice = Number(
            document.getElementById('filter-price')?.value || 0
        );

        const sort =
            document.getElementById('filter-sort')?.value || '';

        let products = this.allProducts.filter(product => {
            const name = String(product.name || product.title || '').toLowerCase();
            const description = String(product.description || '').toLowerCase();
            const productCategory = String(
                product.category || product.category_name || ''
            ).toLowerCase();

            const price = Number(product.price ?? product.amount ?? 0);

            return (
                (!search || name.includes(search) || description.includes(search)) &&
                (!category || productCategory === category) &&
                (!maxPrice || price < maxPrice)
            );
        });

        if (sort === 'price-asc') {
            products.sort((a, b) => Number(a.price || 0) - Number(b.price || 0));
        } else if (sort === 'price-desc') {
            products.sort((a, b) => Number(b.price || 0) - Number(a.price || 0));
        } else if (sort === 'name-asc') {
            products.sort((a, b) =>
                String(a.name || a.title || '').localeCompare(String(b.name || b.title || ''))
            );
        } else if (sort === 'name-desc') {
            products.sort((a, b) =>
                String(b.name || b.title || '').localeCompare(String(a.name || a.title || ''))
            );
        }

        this._renderProducts(products);
        this._renderActiveFilters({ search, category, maxPrice, sort });
    }


_renderProducts(products) {
    const list = document.getElementById('products-list');
    const count = document.getElementById('products-count');

    if (!list) return;

    list.replaceChildren();

    if (count) {
        count.textContent = `${products.length} product(s)`;
    }

    if (!products.length) {
        const empty = document.createElement('div');
        empty.className = 'no-products';
        empty.textContent = 'No products found.';
        list.appendChild(empty);
        return;
    }

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';

        const header = document.createElement('div');
        header.className = 'pc-header';

        const icon = document.createElement('div');
        const category = String(product.category || '').toLowerCase();

        let iconClass = 'pi-default';
        let iconSymbol = 'fa-shirt';

        if (category.includes('shoe') || category.includes('footwear')) {
            iconClass = 'pi-shoes';
            iconSymbol = 'fa-shoe-prints';
        } else if (category.includes('jean')) {
            iconClass = 'pi-jeans';
            iconSymbol = 'fa-person';
        } else if (category.includes('dress')) {
            iconClass = 'pi-dress';
            iconSymbol = 'fa-person-dress';
        } else if (category.includes('jacket')) {
            iconClass = 'pi-jacket';
            iconSymbol = 'fa-shirt';
        } else if (category.includes('bag')) {
            iconClass = 'pi-bag';
            iconSymbol = 'fa-bag-shopping';
        } else if (category.includes('shirt') || category.includes('clothing')) {
            iconClass = 'pi-shirt';
            iconSymbol = 'fa-shirt';
        }

        icon.className = `pc-icon ${iconClass}`;
        icon.innerHTML = `<i class="fas ${iconSymbol}"></i>`;

        const info = document.createElement('div');
        info.style.flex = '1';
        info.style.minWidth = '0';

        const title = document.createElement('div');
        title.className = 'pc-name';
        title.textContent =
            product.display_name || product.name || product.title || 'Product';

        info.appendChild(title);

        if (product.brand) {
            const brand = document.createElement('div');
            brand.className = 'pc-brand';
            brand.textContent = product.brand;
            info.appendChild(brand);
        }

        header.append(icon, info);

        const meta = document.createElement('div');
        meta.className = 'pc-meta';

        ['size', 'color', 'material'].forEach(key => {
            if (product[key]) {
                const tag = document.createElement('span');
                tag.className = 'pc-tag';
                tag.textContent = product[key];
                meta.appendChild(tag);
            }
        });

        const footer = document.createElement('div');
        footer.className = 'pc-footer';

        const price = document.createElement('div');
        price.className = 'pc-price';
        price.textContent =
            `₹${Number(product.price || product.amount || 0).toFixed(2)}`;

        const addButton = document.createElement('button');
        addButton.type = 'button';
        addButton.className = 'pc-add';
        addButton.title = 'Add to cart';
        addButton.setAttribute('aria-label', 'Add to cart');
        addButton.innerHTML = '<i class="fas fa-plus"></i>';

        const productName =
            product.display_name || product.name || product.title || 'product';

        addButton.addEventListener('click', event => {
            event.stopPropagation();
            this.sendCommand(`Add ${productName} to cart`);
        });

        footer.append(price, addButton);
        card.append(header);

        if (meta.children.length) {
            card.appendChild(meta);
        }

        card.appendChild(footer);
        list.appendChild(card);
    });
}

    _renderActiveFilters(filters) {
        const container = document.getElementById('active-filters');
        if (!container) return;

        const active = [];

        if (filters.search) active.push(`Search: ${filters.search}`);
        if (filters.category) active.push(`Category: ${filters.category}`);
        if (filters.maxPrice) active.push(`Under ₹${filters.maxPrice}`);
        if (filters.sort) active.push(`Sort: ${filters.sort}`);

        container.textContent = active.join(' · ');
    }

    // --------------------------------------------------
    // Cart
    // --------------------------------------------------

    
async updateCart(responseData = null) {
    try {
        let data = responseData;

        if (!data || !data.cart_summary) {
            const params = new URLSearchParams({
                session_id: this.sessionId || ''
            });

            data = await this._request(
                `${API.cart}?${params.toString()}`
            );
        }

        if (data.success === false) {
            throw new Error(data.message || 'Could not load cart');
        }

        const summary = data.cart_summary || data;
        this.cartItems = summary.items || [];

        this._renderCart(summary);

    } catch (error) {
        console.error('Cart loading failed:', error);
        this._renderCart({ items: this.cartItems });
    }
}

_renderCart(summary = {}) {
    const items = summary.items || [];
    const body = document.getElementById('cart-body');
    const footer = document.getElementById('cart-footer');
    const count = document.getElementById('cart-count');

    const totalItems = Number(
        summary.total_items ??
        items.reduce((sum, item) =>
            sum + Number(item.quantity ?? item.qty ?? 1), 0
        )
    );

    const total = Number(
        summary.total_price ??
        items.reduce((sum, item) =>
            sum +
            Number(item.unit_price ?? item.price ?? 0) *
            Number(item.quantity ?? item.qty ?? 1), 0
        )
    );

    if (count) count.textContent = String(totalItems);

    const statItems = document.getElementById('stat-items');
    const statTotal = document.getElementById('stat-total');
    const cartTotal = document.getElementById('cart-total');

    if (statItems) statItems.textContent = String(totalItems);
    if (statTotal) statTotal.textContent = `₹${total.toFixed(2)}`;
    if (cartTotal) cartTotal.textContent = total.toFixed(2);

    if (footer) {
        footer.style.display = items.length ? '' : 'none';
    }

    if (!body) return;

    body.replaceChildren();

    if (!items.length) {
        const empty = document.createElement('p');
        empty.className = 'empty-state';
        empty.textContent = 'Your cart is empty.';
        body.appendChild(empty);
        return;
    }

    items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'cart-item';

        const name = document.createElement('span');
        name.textContent =
            item.product_name || item.name || item.title || 'Product';

        const quantity = Number(item.quantity ?? item.qty ?? 1);
        const price = Number(item.unit_price ?? item.price ?? 0);

        const details = document.createElement('span');
        details.textContent =
            `${quantity} × ₹${price.toFixed(2)}`;

        row.append(name, details);
        body.appendChild(row);
    });
}

    toggleCart() {
        const drawer = document.getElementById('cart-drawer');
        const overlay = document.getElementById('cart-overlay');

        this.cartOpen = !this.cartOpen;

        if (drawer) drawer.classList.toggle('open', this.cartOpen);
        if (overlay) overlay.classList.toggle('visible', this.cartOpen);
    }


async clearCartConfirm() {
    if (!confirm('Are you sure you want to clear your cart?')) {
        return;
    }

    try {
        const data = await this._request(API.clearCart, {
            method: 'POST',
            body: JSON.stringify({
                session_id: this.sessionId
            })
        });

        if (!data.success) {
            throw new Error(data.message || 'Could not clear cart');
        }

        await this.updateCart();
        this._toast('Cart cleared.');

    } catch (error) {
        console.error('Clear cart failed:', error);
        this._toast('Could not clear the cart.', 'error');
    }
}


    
async processCheckout() {
    if (!this.cartItems.length) {
        this._toast('Your cart is empty.', 'error');
        return;
    }

    if (!confirm('Proceed with checkout?')) return;

    try {
        const data = await this._request(API.checkout, {
            method: 'POST',
            body: JSON.stringify({
                session_id: this.sessionId
            })
        });

        if (data.success === false) {
            throw new Error(
                data.message ||
                data.checkout_result?.message ||
                'Checkout failed'
            );
        }

        const result = data.checkout_result || {};

        this._addMessage(
            result.message ||
            data.message ||
            data.response ||
            'Checkout request completed.',
            'bot'
        );

        await this.updateCart();
        this._toast('Checkout request completed.');

    } catch (error) {
        console.error('Checkout failed:', error);
        this._toast(
            error.message || 'Checkout failed. Check the backend checkout endpoint.',
            'error'
        );
    }
}


    // --------------------------------------------------
    // Statistics and interface helpers
    // --------------------------------------------------

    _updateStats() {
        const commands = document.getElementById('stat-commands');
        const accuracy = document.getElementById('stat-accuracy');

        if (commands) commands.textContent = String(this.commandCount);

        if (accuracy) {
            accuracy.textContent = this.commandCount
                ? `${(this.totalConfidence / this.commandCount * 100).toFixed(1)}%`
                : '—';
        }
    }

    _setStatus(text) {
        const pill = document.getElementById('status-pill');
        if (!pill) return;

        const label = pill.querySelector('.status-text');
        if (label) label.textContent = text;

        pill.dataset.status = text.toLowerCase();
    }

    _showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.toggle('visible', show);
    }

    _toast(message, type = 'success') {
        const stack = document.getElementById('toast-stack');
        if (!stack) {
            console.log(message);
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        stack.appendChild(toast);

        window.setTimeout(() => toast.remove(), 3500);
    }
}

// --------------------------------------------------
// Global functions used by inline HTML onclick handlers
// --------------------------------------------------

function toggleSidebar() {
    document.getElementById('sidebar')?.classList.toggle('open');
}

function toggleProductPanel() {
    document.getElementById('product-panel')?.classList.toggle('collapsed');
}

// Expose the assistant for the HTML's inline event handlers.
window.app = null;

function initializeShopAI() {
    if (typeof API_BASE === 'undefined') {
        console.error('API_BASE is missing. Check config.js.');
        return;
    }

    window.app = new ShoppingAssistant();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeShopAI);
} else {
    initializeShopAI();
}
