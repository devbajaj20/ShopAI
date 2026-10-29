'use strict';

// ============================================================
//  ShopAI — Frontend Application
// ============================================================

// Read bootstrap data injected by Flask/Jinja2
const _appData    = JSON.parse(document.getElementById('app-data').textContent);
const INITIAL_LANG = _appData.initial_lang;
const SPEECH_LANG  = _appData.speech_lang;
const TRANSLATIONS = _appData.translations;
const ALL_LANGS    = _appData.all_langs;
const LANG_FLAGS   = _appData.lang_flags;

class ShoppingAssistant {
    constructor() {
        this.lang         = INITIAL_LANG || 'en';
        this.speechLang   = SPEECH_LANG  || 'en-US';
        this.t            = TRANSLATIONS || {};
        this.recognition  = null;
        this.isRecording  = false;
        this.cartOpen     = false;
        this.allProducts  = [];
        this.commandCount = 0;
        this.totalConfidence = 0;

        this._initSpeech();
        this._applyTranslations(this.t);
        this._setGreeting();
        this._setupLangButtons();
        this.loadProducts();
        this.updateCart();
    }

    // ── Language ──────────────────────────────────────────
    _setupLangButtons() {
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => this.setLanguage(btn.dataset.lang));
        });
    }

    async setLanguage(lang) {
        try {
            const res  = await fetch('/api/set_language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: lang })
            });
            const data = await res.json();
            if (!data.success) return;

            this.lang       = lang;
            this.speechLang = data.speech_lang;
            this.t          = data.translations;

            // Update recognition language
            if (this.recognition) this.recognition.lang = this.speechLang;

            // UI updates
            document.querySelectorAll('.lang-btn').forEach(b => {
                b.classList.toggle('active', b.dataset.lang === lang);
            });
            document.documentElement.lang = lang;
            this._applyTranslations(this.t);
            this._setGreeting();

            // Update input placeholder
            const input = document.getElementById('command-input');
            if (input && this.t.placeholder) input.placeholder = this.t.placeholder;

            // Reload products with new language
            await this.loadProducts();

            this._toast(LANG_FLAGS[lang] + ' Language changed', 'success');
        } catch (e) {
            this._toast('Language switch failed', 'error');
        }
    }

    _applyTranslations(t) {
        document.querySelectorAll('[data-t]').forEach(el => {
            const key = el.dataset.t;
            if (t[key] !== undefined) el.textContent = t[key];
        });
        const input = document.getElementById('command-input');
        if (input && t.placeholder) input.placeholder = t.placeholder;

        // Loading overlay text
        const loadP = document.querySelector('.loading-box p');
        if (loadP && t.processing) loadP.textContent = t.processing;
    }

    _setGreeting() {
        const gt = document.getElementById('greeting-text');
        const ge = document.getElementById('greeting-examples');
        if (gt) gt.textContent = this.t.greeting || '';
        if (ge) {
            ge.innerHTML = '';
            ['example1','example2','example3','example4','example5'].forEach(k => {
                if (this.t[k]) {
                    const li = document.createElement('li');
                    li.textContent = this.t[k];
                    ge.appendChild(li);
                }
            });
        }
    }

    // ── Speech ────────────────────────────────────────────
    _initSpeech() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { document.getElementById('voice-btn').style.display = 'none'; return; }

        this.recognition = new SR();
        this.recognition.continuous     = false;
        this.recognition.interimResults = false;
        this.recognition.lang           = this.speechLang;

        this.recognition.onresult = (e) => {
            let text = '';
            for (let i = 0; i < e.results.length; i++) {
                if (e.results[i].isFinal) text += e.results[i][0].transcript;
            }
            if (text.trim()) {
                document.getElementById('command-input').value = text.trim();
                this.sendCommand();
            }
        };
        this.recognition.onerror = (e) => {
            if (e.error !== 'no-speech') this._toast('Voice error: ' + e.error, 'error');
            this._stopRecording();
        };
        this.recognition.onend = () => this._stopRecording();
    }

    toggleVoice() {
        if (!this.recognition) { this._toast('Voice not supported', 'error'); return; }
        this.isRecording ? this._stopRecording() : this._startRecording();
    }

    _startRecording() {
        this.isRecording = true;
        const btn = document.getElementById('voice-btn');
        btn.classList.add('recording');
        btn.innerHTML = '<i class="fas fa-stop"></i>';
        try {
            this.recognition.lang = this.speechLang;
            this.recognition.start();
            this._toast((this.t.listening || 'Listening...'), 'success');
            this._recTimeout = setTimeout(() => {
                if (this.isRecording) this._stopRecording();
            }, 12000);
        } catch (err) {
            this._toast('Could not start voice', 'error');
            this._stopRecording();
        }
    }

    _stopRecording() {
        this.isRecording = false;
        const btn = document.getElementById('voice-btn');
        btn.classList.remove('recording');
        btn.innerHTML = '<i class="fas fa-microphone"></i>';
        clearTimeout(this._recTimeout);
        try { this.recognition.stop(); } catch (_) {}
    }

    // ── Commands ──────────────────────────────────────────
    async sendCommand() {
        const input = document.getElementById('command-input');
        const cmd   = input.value.trim();
        if (!cmd) { this._toast('Please enter a command', 'warn'); return; }

        this._addMsg(cmd, 'user');
        input.value = '';

        // Check for filter/sort voice commands first
        const filterResult = this._handleVoiceFilterSort(cmd);
        if (filterResult) {
            this._addMsg(filterResult, 'bot', 'filter', 1);
            this._toast(filterResult, 'success');
            this.commandCount++;
            this.totalConfidence += 1;
            this._updateStats(null);
            return;
        }

        this._showLoading(true);

        try {
            const res  = await fetch('/api/process_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd, language: this.lang })
            });
            const data = await res.json();

            if (data.success) {
                this.commandCount++;
                this.totalConfidence += (data.confidence || 0);

                this._addMsg(data.response, 'bot', data.intent, data.confidence);
                this._showNlpStrip(data);
                this._updateCartDisplay(data.cart_summary);
                this._updateStats(data.cart_summary);
                this._toast('Done!', 'success');
            } else {
                this._addMsg(data.message || 'Something went wrong', 'bot');
                this._toast(data.message || 'Error', 'error');
            }
        } catch (err) {
            this._addMsg('Network error — please try again.', 'bot');
            this._toast('Network error', 'error');
        } finally {
            this._showLoading(false);
        }
    }

    // Quick commands — mapped per language to native phrasing
    _quickCmdMap() {
        const m = {
            'en': { view: 'show me my cart',        shirts: 'search for shirts',   add: 'add a blue shirt',   checkout: 'proceed to checkout' },
            'hi': { view: 'cart dikhao',             shirts: 'शर्ट खोजो',          add: 'नीली शर्ट जोड़ो',    checkout: 'checkout karo' },
            'ta': { view: 'cart காட்டு',             shirts: 'சட்டை தேடு',         add: 'நீல சட்டை சேர்',     checkout: 'checkout செய்' },
            'te': { view: 'cart చూపించు',            shirts: 'చొక్కాలు వెతుకు',    add: 'నీలి చొక్కా చేర్చు', checkout: 'checkout చేయి' },
            'es': { view: 'mostrar mi carrito',      shirts: 'buscar camisas',      add: 'agregar camisa azul', checkout: 'proceder al pago' },
            'fr': { view: 'afficher mon panier',     shirts: 'chercher des chemises',add: 'ajouter chemise bleue',checkout: 'procéder au paiement' },
            'de': { view: 'warenkorb anzeigen',      shirts: 'hemden suchen',       add: 'blaues hemd hinzufügen',checkout: 'zur kasse gehen' },
        };
        return m[this.lang] || m['en'];
    }

    sendQuick(cmdKey) {
        const map = this._quickCmdMap();
        const cmd = map[cmdKey] || cmdKey;
        document.getElementById('command-input').value = cmd;
        this.sendCommand();
    }

    // ── Messages ──────────────────────────────────────────
    _addMsg(content, role, intent, confidence) {
        const wrap = document.getElementById('chat-messages');
        const div  = document.createElement('div');
        div.className = `msg msg-${role === 'user' ? 'user' : 'bot'}`;

        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.innerHTML = role === 'user'
            ? '<i class="fas fa-user"></i>'
            : '<i class="fas fa-robot"></i>';

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';
        bubble.innerHTML = `<p>${this._escapeHtml(content).replace(/\n/g, '<br>')}</p>`;

        if (intent && role !== 'user') {
            const chip = document.createElement('div');
            chip.className = `intent-chip intent-${intent}`;
            chip.innerHTML = `<i class="fas fa-tag"></i>${intent}`;
            if (confidence !== undefined) {
                chip.innerHTML += ` <span style="opacity:.7;margin-left:4px">${(confidence*100).toFixed(0)}%</span>`;
            }
            bubble.appendChild(chip);
        }

        div.appendChild(avatar);
        div.appendChild(bubble);
        wrap.appendChild(div);
        wrap.scrollTop = wrap.scrollHeight;
    }

    _escapeHtml(str) {
        return String(str)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // ── NLP Strip ────────────────────────────────────────
    _showNlpStrip(data) {
        const strip   = document.getElementById('nlp-strip');
        const content = document.getElementById('nlp-strip-content');
        if (!strip || !content) return;

        const tags = [];
        tags.push(`<span class="nlp-tag"><strong>${this.t.intent || 'Intent'}:</strong>${data.intent}</span>`);
        if (data.confidence !== undefined) {
            tags.push(`<span class="nlp-tag"><strong>${this.t.confidence || 'Conf'}:</strong>${(data.confidence*100).toFixed(1)}%</span>`);
        }
        if (data.detected_language && data.detected_language !== 'en') {
            tags.push(`<span class="nlp-tag"><strong>Lang:</strong>${data.detected_language.toUpperCase()}</span>`);
        }
        if (data.entities) {
            const e = data.entities;
            if (e.product_type) tags.push(`<span class="nlp-tag"><strong>Product:</strong>${e.product_type}</span>`);
            if (e.color)        tags.push(`<span class="nlp-tag"><strong>Color:</strong>${e.color}</span>`);
            if (e.size)         tags.push(`<span class="nlp-tag"><strong>Size:</strong>${e.size}</span>`);
            if (e.material)     tags.push(`<span class="nlp-tag"><strong>Material:</strong>${e.material}</span>`);
            if (e.quantity && e.quantity > 1) tags.push(`<span class="nlp-tag"><strong>Qty:</strong>${e.quantity}</span>`);
            if (e.price_range)  tags.push(`<span class="nlp-tag"><strong>Max:</strong>₹${e.price_range.max}</span>`);
        }

        content.innerHTML = tags.join('');
        strip.classList.add('visible');
        clearTimeout(this._stripTimeout);
        this._stripTimeout = setTimeout(() => strip.classList.remove('visible'), 6000);
    }

    // ── Stats ────────────────────────────────────────────
    _updateStats(cartSummary) {
        const avg = this.commandCount ? (this.totalConfidence / this.commandCount * 100).toFixed(0) + '%' : '—';
        const el  = id => document.getElementById(id);
        if (el('stat-commands')) el('stat-commands').textContent = this.commandCount;
        if (el('stat-items'))    el('stat-items').textContent    = cartSummary ? cartSummary.total_items : 0;
        if (el('stat-accuracy')) el('stat-accuracy').textContent = avg;
        if (el('stat-total'))    el('stat-total').textContent    = cartSummary ? '₹' + cartSummary.total_price.toFixed(0) : '₹0';
    }

    // ── Cart ─────────────────────────────────────────────
    async updateCart() {
        try {
            const res  = await fetch('/api/get_cart');
            const data = await res.json();
            if (data.success) {
                this._updateCartDisplay(data.cart_summary);
                this._updateStats(data.cart_summary);
            }
        } catch (_) {}
    }

    _updateCartDisplay(summary) {
        if (!summary) return;
        const count  = document.getElementById('cart-count');
        const body   = document.getElementById('cart-body');
        const footer = document.getElementById('cart-footer');
        const total  = document.getElementById('cart-total');

        if (count) count.textContent = summary.total_items;

        if (summary.total_items === 0) {
            body.innerHTML = `<div class="empty-state">
                <div class="empty-icon"><i class="fas fa-cart-shopping"></i></div>
                <p>${this.t.cart_empty || 'Your cart is empty'}</p>
            </div>`;
            if (footer) footer.style.display = 'none';
        } else {
            body.innerHTML = summary.items.map(item => {
                const icon = this._productIcon(item.product_name);
                return `<div class="cart-item">
                    <div class="ci-icon ${icon.cls}"><i class="${icon.fa}"></i></div>
                    <div class="ci-info">
                        <div class="ci-name">${this._escapeHtml(item.product_name)}</div>
                        <div class="ci-meta">Qty: ${item.quantity}${item.size ? ' · ' + item.size : ''}${item.color ? ' · ' + item.color : ''}</div>
                    </div>
                    <div class="ci-price">₹${item.total_price.toFixed(0)}</div>
                </div>`;
            }).join('');
            if (footer) footer.style.display = 'block';
            if (total)  total.textContent = summary.total_price.toFixed(2);
        }
    }

    toggleCart() {
        this.cartOpen = !this.cartOpen;
        document.getElementById('cart-drawer').classList.toggle('open', this.cartOpen);
        document.getElementById('cart-overlay').classList.toggle('visible', this.cartOpen);
        if (this.cartOpen) this.updateCart();
    }

    async clearCartConfirm() {
        if (!confirm('Clear your cart?')) return;
        try {
            const res  = await fetch('/api/clear_cart', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.updateCart();
                this._toast('Cart cleared', 'success');
            }
        } catch (_) { this._toast('Error clearing cart', 'error'); }
    }

    async processCheckout() {
        try {
            const res  = await fetch('/api/checkout', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                const r = data.checkout_result;
                this._addMsg(`🎉 Order placed! ID: ${r.order_id} · Total: ₹${r.total_amount.toFixed(2)}`, 'bot', 'checkout', 1);
                this.updateCart();
                this.toggleCart();
                this._toast('Order placed!', 'success');
            } else {
                this._toast(data.message || 'Cart is empty', 'warn');
            }
        } catch (_) { this._toast('Checkout error', 'error'); }
    }

    // ── Products ─────────────────────────────────────────
    async loadProducts() {
        try {
            const res  = await fetch('/api/get_products');
            const data = await res.json();
            if (data.success) {
                this.allProducts = data.products;
                this.applyFilters();
            }
        } catch (_) {}
    }

    // Master filter + sort method — called by UI controls AND voice commands
    applyFilters() {
        const query    = (document.getElementById('product-search')?.value || '').toLowerCase();
        const category = document.getElementById('filter-category')?.value || '';
        const maxPrice = parseInt(document.getElementById('filter-price')?.value || '0');
        const sort     = document.getElementById('filter-sort')?.value || '';

        let filtered = this.allProducts.filter(p => {
            const name = (p.display_name || p.name).toLowerCase();
            if (query && !name.includes(query) &&
                !(p.color     || '').toLowerCase().includes(query) &&
                !(p.material  || '').toLowerCase().includes(query) &&
                !(p.brand     || '').toLowerCase().includes(query)) return false;
            if (category && p.category !== category) return false;
            if (maxPrice  && p.price > maxPrice) return false;
            return true;
        });

        // Sort
        if (sort === 'price-asc')  filtered.sort((a,b) => a.price - b.price);
        if (sort === 'price-desc') filtered.sort((a,b) => b.price - a.price);
        if (sort === 'name-asc')   filtered.sort((a,b) => (a.display_name||a.name).localeCompare(b.display_name||b.name));
        if (sort === 'name-desc')  filtered.sort((a,b) => (b.display_name||b.name).localeCompare(a.display_name||a.name));

        this._renderProducts(filtered);
        this._renderActiveFilters(query, category, maxPrice, sort);

        const cnt = document.getElementById('products-count');
        if (cnt) cnt.textContent = `${filtered.length} of ${this.allProducts.length} products`;
    }

    // Set filter/sort programmatically (from voice)
    setFilter(type, value) {
        if (type === 'category') {
            const el = document.getElementById('filter-category');
            if (el) el.value = value;
        } else if (type === 'price') {
            const el = document.getElementById('filter-price');
            if (el) {
                // Find closest option
                const opts = [...el.options].map(o => parseInt(o.value)||0);
                const closest = opts.filter(v => v >= value && v > 0).sort((a,b)=>a-b)[0] || '';
                el.value = closest ? String(closest) : '';
            }
        } else if (type === 'sort') {
            const el = document.getElementById('filter-sort');
            if (el) el.value = value;
        } else if (type === 'search') {
            const el = document.getElementById('product-search');
            if (el) el.value = value;
        }
        this.applyFilters();
    }

    clearFilters() {
        ['filter-category','filter-price','filter-sort'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        const s = document.getElementById('product-search');
        if (s) s.value = '';
        this.applyFilters();
    }

    _renderActiveFilters(query, category, maxPrice, sort) {
        const wrap = document.getElementById('active-filters');
        if (!wrap) return;
        const chips = [];
        if (query)    chips.push({ label: `"${query}"`, clear: () => { document.getElementById('product-search').value=''; this.applyFilters(); }});
        if (category) chips.push({ label: category,     clear: () => { document.getElementById('filter-category').value=''; this.applyFilters(); }});
        if (maxPrice) chips.push({ label: `≤₹${maxPrice}`, clear: () => { document.getElementById('filter-price').value=''; this.applyFilters(); }});
        if (sort)     chips.push({ label: sort.replace('-',' '), clear: () => { document.getElementById('filter-sort').value=''; this.applyFilters(); }});

        wrap.innerHTML = chips.map((c,i) =>
            `<span class="filter-chip" data-chip="${i}"><i class="fas fa-xmark"></i>${c.label}</span>`
        ).join('');
        wrap.querySelectorAll('.filter-chip').forEach((el,i) => {
            el.addEventListener('click', chips[i].clear);
        });
    }

    // Parse voice commands for filter/sort intents
    _handleVoiceFilterSort(command) {
        const c = command.toLowerCase();
        // Sort commands
        if (/price.*(low|cheap|asc|ascending)/.test(c) || /sort.*cheap/.test(c) || /low to high/.test(c)) {
            this.setFilter('sort','price-asc');
            return `Sorted by price: Low to High`;
        }
        if (/price.*(high|expensive|desc)/.test(c) || /high to low/.test(c)) {
            this.setFilter('sort','price-desc');
            return `Sorted by price: High to Low`;
        }
        if (/name.*(a.*z|asc)/.test(c) || /alphabetical/.test(c)) {
            this.setFilter('sort','name-asc');
            return `Sorted A to Z`;
        }
        if (/name.*(z.*a|desc)/.test(c)) {
            this.setFilter('sort','name-desc');
            return `Sorted Z to A`;
        }
        // Category filter
        if (/show.*(shirt|t-shirt|jeans|dress|jacket|clothing|clothes)/.test(c) || /filter.*cloth/.test(c)) {
            this.setFilter('category','clothing');
            return `Showing clothing only`;
        }
        if (/show.*shoe|filter.*foot|footwear/.test(c)) {
            this.setFilter('category','footwear');
            return `Showing footwear only`;
        }
        if (/show.*bag|filter.*access/.test(c)) {
            this.setFilter('category','accessories');
            return `Showing accessories only`;
        }
        // Price filter
        const pm = c.match(/under\s*(?:rs\.?|₹)?\s*(\d+)/);
        if (pm) {
            this.setFilter('price', parseInt(pm[1]));
            return `Showing products under ₹${pm[1]}`;
        }
        const bm = c.match(/below\s*(?:rs\.?|₹)?\s*(\d+)/);
        if (bm) {
            this.setFilter('price', parseInt(bm[1]));
            return `Showing products under ₹${bm[1]}`;
        }
        // Clear filters
        if (/clear.*(filter|sort)|show all|reset/.test(c)) {
            this.clearFilters();
            return `Filters cleared — showing all products`;
        }
        return null;
    }

    _renderProducts(products) {
        const list = document.getElementById('products-list');
        if (!products.length) {
            list.innerHTML = '<div class="products-loading">No products found</div>';
            return;
        }
        list.innerHTML = products.map((p, i) => {
            const icon = this._productIcon(p.name);
            // use display_name for UI, name (English) for commands
            const shown = p.display_name || p.name;
            const tags = [
                p.color    ? `<span class="pc-tag">${p.color}</span>` : '',
                p.size     ? `<span class="pc-tag">${p.size}</span>` : '',
                p.material ? `<span class="pc-tag">${p.material}</span>` : '',
            ].filter(Boolean).join('');
            return `<div class="product-card" style="animation-delay:${i*0.04}s"
                        onclick="app._addToCart('${this._escapeHtml(p.name)}')">
                <div class="pc-header">
                    <div class="pc-icon ${icon.cls}"><i class="${icon.fa}"></i></div>
                    <div>
                        <div class="pc-name">${this._escapeHtml(shown)}</div>
                        <div class="pc-brand">${p.brand || p.category}</div>
                    </div>
                </div>
                <div class="pc-meta">${tags}</div>
                <div class="pc-footer">
                    <span class="pc-price">₹${p.price}</span>
                    <button class="pc-add" onclick="event.stopPropagation();app._addToCart('${this._escapeHtml(p.name)}')">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>`;
        }).join('');
    }

    _addToCart(name) {
        document.getElementById('command-input').value = `add ${name.toLowerCase()}`;
        this.sendCommand();
    }

    _productIcon(name) {
        const n = (name || '').toLowerCase();
        if (n.includes('t-shirt') || n.includes('shirt')) return { fa:'fas fa-shirt',      cls:'pi-shirt'  };
        if (n.includes('jean')    || n.includes('pant'))  return { fa:'fas fa-person',      cls:'pi-jeans'  };
        if (n.includes('dress'))                          return { fa:'fas fa-person-dress', cls:'pi-dress'  };
        if (n.includes('jacket')  || n.includes('coat'))  return { fa:'fas fa-vest',         cls:'pi-jacket' };
        if (n.includes('shoe')    || n.includes('sneak')
                                  || n.includes('boot'))  return { fa:'fas fa-shoe-prints',  cls:'pi-shoes'  };
        if (n.includes('bag')     || n.includes('pack'))  return { fa:'fas fa-bag-shopping', cls:'pi-bag'    };
        if (n.includes('sweater') || n.includes('wool'))  return { fa:'fas fa-mitten',       cls:'pi-sweater'};
        return { fa:'fas fa-tag', cls:'pi-default' };
    }

    // ── Utilities ────────────────────────────────────────
    _showLoading(show) {
        document.getElementById('loading-overlay').classList.toggle('show', show);
        const pill = document.getElementById('status-pill');
        if (pill) {
            const dot  = pill.querySelector('.status-dot-inner');
            const text = pill.querySelector('.status-text');
            if (show) {
                dot.style.background  = 'var(--warning)';
                dot.style.boxShadow   = '0 0 8px var(--warning)';
                if (text) text.textContent = 'Working';
            } else {
                dot.style.background  = 'var(--success)';
                dot.style.boxShadow   = '0 0 8px var(--success)';
                if (text) text.textContent = 'Ready';
            }
        }
    }

    _toast(msg, type = 'success') {
        const stack = document.getElementById('toast-stack');
        const icons = { success:'fa-circle-check', error:'fa-circle-xmark', warn:'fa-triangle-exclamation' };
        const el = document.createElement('div');
        el.className = `toast-item toast-${type}`;
        el.innerHTML = `<i class="fas ${icons[type] || icons.success}"></i><span>${this._escapeHtml(msg)}</span>`;
        stack.appendChild(el);
        setTimeout(() => {
            el.classList.add('fading');
            el.addEventListener('animationend', () => el.remove(), { once: true });
        }, 3200);
    }
}

// ── Global helpers called from HTML ──────────────────────
function toggleSidebar() {
    const s = document.getElementById('sidebar');
    if (window.innerWidth <= 900) {
        s.classList.toggle('mobile-open');
        document.body.classList.toggle('sidebar-open', s.classList.contains('mobile-open'));
    } else {
        s.classList.toggle('collapsed');
    }
}

function toggleProductPanel() {
    const p    = document.getElementById('product-panel');
    const icon = document.getElementById('pp-toggle').querySelector('i');
    p.classList.toggle('collapsed-p');
    if (icon) icon.className = p.classList.contains('collapsed-p')
        ? 'fas fa-chevron-left'
        : 'fas fa-chevron-right';
}

// ── Boot ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ShoppingAssistant();
});
