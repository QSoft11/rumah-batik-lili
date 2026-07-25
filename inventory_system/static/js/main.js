

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', (e) => {
            const term = e.target.value.toLowerCase();
            const targetTableId = input.getAttribute('data-table-search');
            const table = document.getElementById(targetTableId);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(term) ? '' : 'none';
                });
            }
        });
    });

    window.formatRupiah = function(number) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(number);
    };

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

class POSManager {
    constructor() {
        this.cart = [];
        this.cartContainer = document.getElementById('cartItems');
        this.totalElement = document.getElementById('cartTotal');
        this.subtotalElement = document.getElementById('cartSubtotal');
        this.btnCheckout = document.getElementById('btnProcessCheckout');
        
        if (this.cartContainer) {
            this.init();
        }
    }

    init() {
        document.querySelectorAll('.product-card-box').forEach(card => {
            card.addEventListener('click', () => {
                const id = parseInt(card.dataset.id);
                const name = card.dataset.name;
                const price = parseFloat(card.dataset.price);
                const maxStok = parseInt(card.dataset.stok);
                
                this.addItem(id, name, price, maxStok);
            });
        });

        const searchProduct = document.getElementById('searchProduct');
        if (searchProduct) {
            searchProduct.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                document.querySelectorAll('.product-card-box').forEach(card => {
                    const name = card.dataset.name.toLowerCase();
                    const code = card.dataset.code.toLowerCase();
                    if (name.includes(query) || code.includes(query)) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        }

        if (this.btnCheckout) {
            this.btnCheckout.addEventListener('click', () => this.processCheckout());
        }
    }

    addItem(id, name, price, maxStok) {
        const existing = this.cart.find(item => item.id === id);
        
        if (existing) {
            if (existing.jumlah + 1 > maxStok) {
                alert(`Stok produk "${name}" hanya tersisa ${maxStok} unit.`);
                return;
            }
            existing.jumlah += 1;
        } else {
            this.cart.push({
                id: id,
                nama: name,
                harga: price,
                jumlah: 1,
                maxStok: maxStok
            });
        }
        
        this.renderCart();
    }

    updateQty(id, delta) {
        const item = this.cart.find(i => i.id === id);
        if (!item) return;

        const newQty = item.jumlah + delta;
        if (newQty <= 0) {
            this.cart = this.cart.filter(i => i.id !== id);
        } else if (newQty > item.maxStok) {
            alert(`Stok maksimal adalah ${item.maxStok}`);
            return;
        } else {
            item.jumlah = newQty;
        }
        
        this.renderCart();
    }

    removeItem(id) {
        this.cart = this.cart.filter(i => i.id !== id);
        this.renderCart();
    }

    calculateTotal() {
        return this.cart.reduce((sum, item) => sum + (item.harga * item.jumlah), 0);
    }

    renderCart() {
        if (!this.cartContainer) return;

        if (this.cart.length === 0) {
            this.cartContainer.innerHTML = `
                <div style="text-align: center; color: var(--text-muted); padding: 30px 10px;">
                    <i class="ri-shopping-cart-2-line" style="font-size: 2.5rem; opacity: 0.4;"></i>
                    <p style="margin-top: 8px; font-size: 0.85rem;">Keranjang belanja masih kosong.</p>
                    <small>Klik produk di sebelah kiri untuk menambahkan</small>
                </div>
            `;
            if (this.btnCheckout) this.btnCheckout.disabled = true;
        } else {
            this.cartContainer.innerHTML = this.cart.map(item => `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <div class="cart-item-name">${item.nama}</div>
                        <div class="cart-item-price">${window.formatRupiah(item.harga)} x ${item.jumlah}</div>
                    </div>
                    <div class="cart-item-qty">
                        <button class="qty-btn" onclick="posApp.updateQty(${item.id}, -1)">-</button>
                        <span style="font-size: 0.85rem; font-weight: 600; min-width: 20px; text-align: center;">${item.jumlah}</span>
                        <button class="qty-btn" onclick="posApp.updateQty(${item.id}, 1)">+</button>
                        <button class="btn btn-icon btn-sm" style="color: var(--status-danger);" onclick="posApp.removeItem(${item.id})">
                            <i class="ri-delete-bin-line"></i>
                        </button>
                    </div>
                </div>
            `).join('');
            if (this.btnCheckout) this.btnCheckout.disabled = false;
        }

        const total = this.calculateTotal();
        if (this.totalElement) this.totalElement.textContent = window.formatRupiah(total);
        if (this.subtotalElement) this.subtotalElement.textContent = window.formatRupiah(total);
    }

    async processCheckout() {
        if (this.cart.length === 0) return;

        const kodeTransaksi = document.getElementById('kodeTransaksi').value;
        const namaPembeli = document.getElementById('namaPembeli').value.trim() || 'Umum';

        this.btnCheckout.disabled = true;
        this.btnCheckout.innerHTML = `<i class="ri-loader-4-line ri-spin"></i> Memproses...`;

        try {
            const response = await fetch('/transaksi/proses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    kode_transaksi: kodeTransaksi,
                    nama_pembeli: namaPembeli,
                    items: this.cart.map(i => ({ id: i.id, jumlah: i.jumlah }))
                })
            });

            const result = await response.json();

            if (result.success) {
                alert(`Transaksi Sukses! Kode: ${result.kode_transaksi}`);
                window.location.href = `/transaksi/detail/${result.transaksi_id}`;
            } else {
                alert(`Gagal: ${result.message}`);
                this.btnCheckout.disabled = false;
                this.btnCheckout.innerHTML = `<i class="ri-check-double-line"></i> Selesaikan Transaksi`;
            }
        } catch (err) {
            alert(`Terjadi kesalahan jaringan: ${err.message}`);
            this.btnCheckout.disabled = false;
            this.btnCheckout.innerHTML = `<i class="ri-check-double-line"></i> Selesaikan Transaksi`;
        }
    }
}

let posApp;
document.addEventListener('DOMContentLoaded', () => {
    posApp = new POSManager();
});