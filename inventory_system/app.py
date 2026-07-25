import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, g, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'rumah_batik_lili_secret_key_prod_2026'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 900
DB_PATH = os.path.join(app.root_path, 'database.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_barang TEXT UNIQUE NOT NULL,
                nama_barang TEXT NOT NULL,
                kategori TEXT NOT NULL,
                ukuran TEXT DEFAULT 'All Size',
                harga_jual REAL NOT NULL,
                stok INTEGER NOT NULL DEFAULT 0,
                stok_minimum INTEGER NOT NULL DEFAULT 5,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("PRAGMA table_info(barang)")
        existing_cols = [col['name'] for col in cursor.fetchall()]
        if 'ukuran' not in existing_cols:
            cursor.execute("ALTER TABLE barang ADD COLUMN ukuran TEXT DEFAULT 'All Size'")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_transaksi TEXT UNIQUE NOT NULL,
                tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_harga REAL NOT NULL,
                nama_pembeli TEXT DEFAULT 'Umum'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detail_transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaksi_id INTEGER NOT NULL,
                barang_id INTEGER NOT NULL,
                jumlah INTEGER NOT NULL,
                harga_satuan REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (transaksi_id) REFERENCES transaksi (id) ON DELETE CASCADE,
                FOREIGN KEY (barang_id) REFERENCES barang (id)
            )
        ''')
        
        cursor.execute('SELECT * FROM admin WHERE username = ?', ('natadi11',))
        if not cursor.fetchone():
            hashed_pwd = generate_password_hash('natadi11', method='pbkdf2:sha256')
            cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)', ('natadi11', hashed_pwd))

        db.commit()

@app.template_filter('format_wib')
def format_wib_filter(dt_val):
    if not dt_val:
        return ""
    months_id = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    if isinstance(dt_val, str):
        try:
            dt = datetime.strptime(dt_val, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                dt = datetime.strptime(dt_val, '%Y-%m-%d')
                return f"{dt.day} {months_id[dt.month]} {dt.year}"
            except ValueError:
                return dt_val
    elif isinstance(dt_val, datetime):
        dt = dt_val
    else:
        return str(dt_val)

    from datetime import timedelta
    sys_now = datetime.now()
    if (sys_now.hour - dt.hour) % 24 == 7:
        dt = dt + timedelta(hours=7)

    return f"{dt.day} {months_id[dt.month]} {dt.year} — {dt.strftime('%H:%M:%S')} WIB"

@app.context_processor
def inject_notifications():
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM barang WHERE stok <= stok_minimum')
        low_stock_count = cursor.fetchone()['count']
        return dict(low_stock_count=low_stock_count)
    return dict(low_stock_count=0)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses sistem.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def check_session_security():
    session.permanent = False
    
    if not request.endpoint or request.endpoint in ['static', 'login', 'logout']:
        return

    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu untuk mengakses sistem.', 'warning')
        return redirect(url_for('login'))

    now_ts = datetime.now().timestamp()
    last_active = session.get('last_active')
    
    if last_active and (now_ts - last_active > 900):
        session.clear()
        flash('Sesi Anda telah berakhir demi keamanan. Silakan login kembali.', 'warning')
        return redirect(url_for('login'))
        
    just_logged_in = session.pop('just_logged_in', False)
    referrer = request.referrer
    
    if not just_logged_in:
        if not referrer or not referrer.startswith(request.host_url):
            session.clear()
            flash('Demi keamanan, akses via link langsung harus melalui verifikasi login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
            
    session['last_active'] = now_ts

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['last_active'] = datetime.now().timestamp()
            session['just_logged_in'] = True
            flash('Selamat datang kembali, Administrator Rumah Batik Lili!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password yang Anda masukkan salah.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM barang')
    total_barang = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM barang WHERE stok <= stok_minimum')
    total_stok_kritis = cursor.fetchone()['total']
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_harga), 0) as total_omset 
        FROM transaksi 
        WHERE date(tanggal) = ?
    ''', (today_str,))
    transaksi_hari_ini = cursor.fetchone()
    
    cursor.execute('SELECT COALESCE(SUM(harga_jual * stok), 0) as total_aset FROM barang')
    total_aset_stok = cursor.fetchone()['total_aset']
    
    from datetime import timedelta
    chart_dates = []
    chart_omsets = []
    for i in range(6, -1, -1):
        dt = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        chart_dates.append((datetime.now() - timedelta(days=i)).strftime('%d %b'))
        cursor.execute('SELECT COALESCE(SUM(total_harga), 0) as omset FROM transaksi WHERE date(tanggal) = ?', (dt,))
        chart_omsets.append(cursor.fetchone()['omset'])
        
    cursor.execute('SELECT kategori, COUNT(*) as count FROM barang GROUP BY kategori')
    cat_rows = cursor.fetchall()
    cat_labels = [r['kategori'] for r in cat_rows]
    cat_counts = [r['count'] for r in cat_rows]
    
    cursor.execute('''
        SELECT * FROM barang 
        WHERE stok <= stok_minimum 
        ORDER BY stok ASC 
        LIMIT 5
    ''')
    barang_kritis = cursor.fetchall()
    
    cursor.execute('''
        SELECT * FROM transaksi 
        ORDER BY tanggal DESC 
        LIMIT 5
    ''')
    transaksi_terbaru = cursor.fetchall()
    
    return render_template('dashboard.html',
                           total_barang=total_barang,
                           total_stok_kritis=total_stok_kritis,
                           transaksi_hari_ini_count=transaksi_hari_ini['count'],
                           omset_hari_ini=transaksi_hari_ini['total_omset'],
                           total_aset_stok=total_aset_stok,
                           chart_dates=chart_dates,
                           chart_omsets=chart_omsets,
                           cat_labels=cat_labels,
                           cat_counts=cat_counts,
                           barang_kritis=barang_kritis,
                           transaksi_terbaru=transaksi_terbaru)


@app.route('/barang')
@login_required
def data_barang():
    kategori_filter = request.args.get('kategori', '').strip()
    search_query = request.args.get('q', '').strip()
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT DISTINCT kategori FROM barang ORDER BY kategori ASC')
    kategori_list = [row['kategori'] for row in cursor.fetchall()]
    
    sql = 'SELECT * FROM barang WHERE 1=1'
    params = []
    
    if kategori_filter:
        sql += ' AND kategori = ?'
        params.append(kategori_filter)
        
    if search_query:
        sql += ' AND (nama_barang LIKE ? OR kode_barang LIKE ?)'
        params.append(f'%{search_query}%')
        params.append(f'%{search_query}%')
        
    sql += ' ORDER BY created_at DESC'
    cursor.execute(sql, params)
    barang_items = cursor.fetchall()
    
    return render_template('barang.html', 
                           barang_items=barang_items, 
                           kategori_list=kategori_list,
                           selected_kategori=kategori_filter,
                           search_query=search_query)

@app.route('/barang/tambah', methods=['GET', 'POST'])
@login_required
def tambah_barang():
    if request.method == 'POST':
        kode_barang = request.form.get('kode_barang', '').strip().upper()
        nama_barang = request.form.get('nama_barang', '').strip()
        kategori = request.form.get('kategori', '').strip()
        kategori_baru = request.form.get('kategori_baru', '').strip()
        ukuran = request.form.get('ukuran', 'All Size').strip()
        harga_jual = request.form.get('harga_jual', 0, type=float)
        stok = request.form.get('stok', 0, type=int)
        stok_minimum = request.form.get('stok_minimum', 5, type=int)
        
        if kategori_baru:
            kategori = kategori_baru
            
        if not kode_barang or not nama_barang or not kategori or harga_jual <= 0:
            flash('Mohon lengkapi seluruh field formulir dengan benar.', 'danger')
            return redirect(url_for('tambah_barang'))
            
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT id FROM barang WHERE kode_barang = ?', (kode_barang,))
        if cursor.fetchone():
            flash(f'Kode barang "{kode_barang}" sudah digunakan oleh produk lain.', 'danger')
            return redirect(url_for('tambah_barang'))
            
        cursor.execute('''
            INSERT INTO barang (kode_barang, nama_barang, kategori, ukuran, harga_jual, stok, stok_minimum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (kode_barang, nama_barang, kategori, ukuran, harga_jual, stok, stok_minimum))
        db.commit()
        
        flash(f'Barang "{nama_barang}" (Ukuran: {ukuran}) berhasil ditambahkan.', 'success')
        return redirect(url_for('data_barang'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT kategori FROM barang ORDER BY kategori ASC')
    kategori_list = [row['kategori'] for row in cursor.fetchall()]
    
    cursor.execute('SELECT COUNT(*) as count FROM barang')
    next_num = cursor.fetchone()['count'] + 1
    suggested_code = f"BTK-{next_num:03d}"
    
    return render_template('tambah_barang.html', kategori_list=kategori_list, suggested_code=suggested_code)

@app.route('/barang/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_barang(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM barang WHERE id = ?', (id,))
    item = cursor.fetchone()
    
    if not item:
        flash('Data barang tidak ditemukan.', 'danger')
        return redirect(url_for('data_barang'))
        
    if request.method == 'POST':
        kode_barang = request.form.get('kode_barang', '').strip().upper()
        nama_barang = request.form.get('nama_barang', '').strip()
        kategori = request.form.get('kategori', '').strip()
        kategori_baru = request.form.get('kategori_baru', '').strip()
        ukuran = request.form.get('ukuran', 'All Size').strip()
        harga_jual = request.form.get('harga_jual', 0, type=float)
        stok_minimum = request.form.get('stok_minimum', 5, type=int)
        
        if kategori_baru:
            kategori = kategori_baru
            
        cursor.execute('SELECT id FROM barang WHERE kode_barang = ? AND id != ?', (kode_barang, id))
        if cursor.fetchone():
            flash(f'Kode barang "{kode_barang}" sudah digunakan.', 'danger')
            return redirect(url_for('edit_barang', id=id))
            
        cursor.execute('''
            UPDATE barang 
            SET kode_barang = ?, nama_barang = ?, kategori = ?, ukuran = ?, harga_jual = ?, stok_minimum = ?
            WHERE id = ?
        ''', (kode_barang, nama_barang, kategori, ukuran, harga_jual, stok_minimum, id))
        db.commit()
        
        flash(f'Data barang "{nama_barang}" berhasil diperbarui.', 'success')
        return redirect(url_for('data_barang'))
        
    cursor.execute('SELECT DISTINCT kategori FROM barang ORDER BY kategori ASC')
    kategori_list = [row['kategori'] for row in cursor.fetchall()]
    
    return render_template('edit_barang.html', item=item, kategori_list=kategori_list)

@app.route('/barang/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_barang(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT nama_barang FROM barang WHERE id = ?', (id,))
    item = cursor.fetchone()
    
    if item:
        cursor.execute('DELETE FROM barang WHERE id = ?', (id,))
        db.commit()
        flash(f'Barang "{item["nama_barang"]}" berhasil dihapus.', 'success')
    else:
        flash('Barang tidak ditemukan.', 'danger')
        
    return redirect(url_for('data_barang'))


@app.route('/stok')
@login_required
def data_stok():
    filter_status = request.args.get('status', 'semua')
    
    db = get_db()
    cursor = db.cursor()
    
    if filter_status == 'habis':
        cursor.execute('SELECT * FROM barang WHERE stok = 0 ORDER BY nama_barang ASC')
    elif filter_status == 'menipis':
        cursor.execute('SELECT * FROM barang WHERE stok > 0 AND stok <= stok_minimum ORDER BY stok ASC')
    else:
        cursor.execute('SELECT * FROM barang ORDER BY stok ASC')
        
    barang_stok = cursor.fetchall()
    return render_template('stok.html', barang_stok=barang_stok, current_filter=filter_status)

@app.route('/stok/tambah/<int:id>', methods=['GET', 'POST'])
@login_required
def tambah_stok(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM barang WHERE id = ?', (id,))
    item = cursor.fetchone()
    
    if not item:
        flash('Barang tidak ditemukan.', 'danger')
        return redirect(url_for('data_stok'))
        
    if request.method == 'POST':
        jumlah_tambah = request.form.get('jumlah', 0, type=int)
        catatan = request.form.get('catatan', '').strip()
        
        if jumlah_tambah <= 0:
            flash('Jumlah stok yang ditambahkan harus lebih besar dari 0.', 'danger')
            return redirect(url_for('tambah_stok', id=id))
            
        stok_baru = item['stok'] + jumlah_tambah
        cursor.execute('UPDATE barang SET stok = ? WHERE id = ?', (stok_baru, id))
        db.commit()
        
        flash(f'Berhasil menambahkan {jumlah_tambah} unit stok untuk "{item["nama_barang"]}". Total stok sekarang: {stok_baru}.', 'success')
        return redirect(url_for('data_stok'))
        
    return render_template('tambah_stok.html', item=item)


@app.route('/transaksi')
@login_required
def transaksi():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM barang WHERE stok > 0 ORDER BY nama_barang ASC')
    barang_tersedia = cursor.fetchall()
    
    date_prefix = datetime.now().strftime('%Y%m%d')
    cursor.execute("SELECT COUNT(*) as total FROM transaksi WHERE kode_transaksi LIKE ?", (f'TRX-{date_prefix}-%',))
    sequence = cursor.fetchone()['total'] + 1
    kode_transaksi_saran = f"TRX-{date_prefix}-{sequence:04d}"
    
    return render_template('transaksi.html', barang_list=barang_tersedia, kode_transaksi=kode_transaksi_saran)

@app.route('/transaksi/proses', methods=['POST'])
@login_required
def proses_transaksi():
    data = request.get_json()
    if not data or 'items' not in data or len(data['items']) == 0:
        return jsonify({'success': False, 'message': 'Keranjang belanja kosong.'}), 400
        
    kode_transaksi = data.get('kode_transaksi')
    nama_pembeli = data.get('nama_pembeli', 'Umum').strip() or 'Umum'
    items = data['items']
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        db.execute('BEGIN TRANSACTION')
        
        total_harga = 0
        detail_insert = []
        
        for item in items:
            barang_id = int(item['id'])
            jumlah = int(item['jumlah'])
            
            cursor.execute('SELECT stok, harga_jual, nama_barang FROM barang WHERE id = ?', (barang_id,))
            barang = cursor.fetchone()
            
            if not barang:
                db.rollback()
                return jsonify({'success': False, 'message': f'Barang ID {barang_id} tidak ditemukan.'}), 400
                
            if barang['stok'] < jumlah:
                db.rollback()
                return jsonify({
                    'success': False, 
                    'message': f'Stok "{barang["nama_barang"]}" tidak mencukupi. Sisa stok: {barang["stok"]}.'
                }), 400
                
            harga_satuan = float(barang['harga_jual'])
            subtotal = harga_satuan * jumlah
            total_harga += subtotal
            
            detail_insert.append((barang_id, jumlah, harga_satuan, subtotal))
            
            stok_baru = barang['stok'] - jumlah
            cursor.execute('UPDATE barang SET stok = ? WHERE id = ?', (stok_baru, barang_id))
            
        wib_tanggal = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO transaksi (kode_transaksi, tanggal, total_harga, nama_pembeli)
            VALUES (?, ?, ?, ?)
        ''', (kode_transaksi, wib_tanggal, total_harga, nama_pembeli))
        transaksi_id = cursor.lastrowid
        
        for d in detail_insert:
            cursor.execute('''
                INSERT INTO detail_transaksi (transaksi_id, barang_id, jumlah, harga_satuan, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (transaksi_id, d[0], d[1], d[2], d[3]))
            
        db.commit()
        return jsonify({
            'success': True, 
            'message': 'Transaksi berhasil diproses.',
            'transaksi_id': transaksi_id,
            'kode_transaksi': kode_transaksi
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Terjadi kesalahan server: {str(e)}'}), 500

@app.route('/transaksi/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_transaksi(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT kode_transaksi FROM transaksi WHERE id = ?', (id,))
    trx = cursor.fetchone()
    if not trx:
        flash('Data transaksi tidak ditemukan.', 'danger')
        return redirect(url_for('laporan'))
        
    kode = trx['kode_transaksi']
    cursor.execute('DELETE FROM detail_transaksi WHERE transaksi_id = ?', (id,))
    cursor.execute('DELETE FROM transaksi WHERE id = ?', (id,))
    db.commit()
    
    flash(f'Transaksi "{kode}" berhasil dihapus.', 'success')
    return redirect(url_for('laporan'))

@app.route('/transaksi/reset', methods=['POST'])
@login_required
def reset_transaksi():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM detail_transaksi')
    cursor.execute('DELETE FROM transaksi')
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('transaksi', 'detail_transaksi')")
    except Exception:
        pass
    db.commit()
    
    flash('Seluruh data transaksi berhasil di-reset / dikosongkan.', 'success')
    return redirect(url_for('laporan'))


@app.route('/laporan')
@login_required
def laporan():
    tgl_mulai = request.args.get('tgl_mulai', '')
    tgl_selesai = request.args.get('tgl_selesai', '')
    preset = request.args.get('preset', '')
    
    now = datetime.now()
    if preset == 'today':
        tgl_mulai = now.strftime('%Y-%m-%d')
        tgl_selesai = now.strftime('%Y-%m-%d')
    elif preset == '7days':
        from datetime import timedelta
        tgl_mulai = (now - timedelta(days=6)).strftime('%Y-%m-%d')
        tgl_selesai = now.strftime('%Y-%m-%d')
    elif preset == 'this_month':
        tgl_mulai = now.strftime('%Y-%m-01')
        tgl_selesai = now.strftime('%Y-%m-%d')
    
    db = get_db()
    cursor = db.cursor()
    
    sql = 'SELECT * FROM transaksi WHERE 1=1'
    params = []
    
    if tgl_mulai:
        sql += ' AND date(tanggal) >= ?'
        params.append(tgl_mulai)
    if tgl_selesai:
        sql += ' AND date(tanggal) <= ?'
        params.append(tgl_selesai)
        
    sql += ' ORDER BY tanggal DESC'
    cursor.execute(sql, params)
    daftar_transaksi = cursor.fetchall()
    
    total_pendapatan = sum(row['total_harga'] for row in daftar_transaksi)
    total_transaksi = len(daftar_transaksi)
    
    return render_template('laporan.html', 
                           daftar_transaksi=daftar_transaksi,
                           tgl_mulai=tgl_mulai,
                           tgl_selesai=tgl_selesai,
                           total_pendapatan=total_pendapatan,
                           total_transaksi=total_transaksi)

@app.route('/laporan/export/csv')
@login_required
def export_laporan_csv():
    import io, csv
    from flask import Response
    
    tgl_mulai = request.args.get('tgl_mulai', '')
    tgl_selesai = request.args.get('tgl_selesai', '')
    
    db = get_db()
    cursor = db.cursor()
    
    sql = 'SELECT * FROM transaksi WHERE 1=1'
    params = []
    if tgl_mulai:
        sql += ' AND date(tanggal) >= ?'
        params.append(tgl_mulai)
    if tgl_selesai:
        sql += ' AND date(tanggal) <= ?'
        params.append(tgl_selesai)
        
    sql += ' ORDER BY tanggal DESC'
    cursor.execute(sql, params)
    daftar_transaksi = cursor.fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['No', 'Kode Transaksi', 'Tanggal & Waktu', 'Nama Pembeli', 'Total Harga (Rp)'])
    
    for idx, t in enumerate(daftar_transaksi, 1):
        writer.writerow([idx, t['kode_transaksi'], t['tanggal'], t['nama_pembeli'], t['total_harga']])
        
    output.seek(0)
    filename = f"Laporan_Penjualan_Batik_Lili_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route('/transaksi/detail/<int:id>')
@login_required
def detail_transaksi(id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM transaksi WHERE id = ?', (id,))
    transaksi_data = cursor.fetchone()
    
    if not transaksi_data:
        flash('Transaksi tidak ditemukan.', 'danger')
        return redirect(url_for('laporan'))
        
    cursor.execute('''
        SELECT dt.*, b.nama_barang, b.kode_barang 
        FROM detail_transaksi dt
        JOIN barang b ON dt.barang_id = b.id
        WHERE dt.transaksi_id = ?
    ''', (id,))
    items = cursor.fetchall()
    
    return render_template('detail_transaksi.html', transaksi=transaksi_data, items=items)


@app.route('/notifikasi')
@login_required
def notifikasi():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM barang WHERE stok = 0 ORDER BY nama_barang ASC')
    stok_habis = cursor.fetchall()
    
    cursor.execute('SELECT * FROM barang WHERE stok > 0 AND stok <= stok_minimum ORDER BY stok ASC')
    stok_menipis = cursor.fetchall()
    
    return render_template('notifikasi.html', stok_habis=stok_habis, stok_menipis=stok_menipis)

init_db()

if __name__ == '__main__':
    print("Mulai menjalankan Sistem Inventori & Penjualan Rumah Batik Lili...")
    print("Akses lokal: http://localhost:5000")
    print("Login default: natadi11 / natadi11")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)