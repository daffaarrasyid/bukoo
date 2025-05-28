# File: Bukoo/core/anggota.py

# Impor modul-modul yang diperlukan
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime, timedelta
from collections import deque
from .utils import simpan_semua_data
from .buku import lihat_buku
# Fungsi lihat_buku tidak diimpor langsung, tapi dipanggil via instance app

# Inisialisasi console Rich
console = Console()

# --- Fungsi hapus_anggota ---
# Tidak ada perubahan logika pada fungsi ini dari revisi sebelumnya.
# Komentar ditambahkan untuk menjelaskan fungsinya.
def hapus_anggota(app): 
    """
    Menghapus akun anggota dari sistem. Hanya dapat diakses oleh Staff.
    Memeriksa apakah anggota masih memiliki buku yang dipinjam sebelum menghapus.
    """
    console.print(Panel("👤➖ Hapus Akun Anggota dari Sistem ➖👤", style="bold indian_red", border_style="indian_red", expand=False, padding=1))
    if not app.data_anggota:
        console.print(Panel.fit("[italic yellow]Belum ada data anggota untuk dihapus.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return

    if Confirm.ask("[bold yellow]❓ Tampilkan daftar anggota terlebih dahulu untuk memilih ID?[/bold yellow]", default=False):
        temp_table = Table(title="👥 Daftar Anggota Terdaftar 👥", show_lines=True, header_style="bold deep_sky_blue1", border_style="dim deep_sky_blue1")
        temp_table.add_column("ID Anggota", style="cyan")
        temp_table.add_column("Nama Anggota", style="white")
        temp_table.add_column("Username", style="dim")
        for id_a, data_a in app.data_anggota.items():
            temp_table.add_row(id_a, data_a['nama'], data_a['username'])
        console.print(temp_table)
        console.line()

    id_hapus = Prompt.ask("[bold yellow]🆔 Masukkan ID Anggota yang ingin dihapus[/bold yellow]")

    if id_hapus not in app.data_anggota:
        console.print(Panel.fit(f"[bold red]❌ Anggota dengan ID '{id_hapus}' tidak ditemukan.[/bold red]", title="⚠️ Gagal", border_style="red"))
        return

    anggota = app.data_anggota[id_hapus]
    if id_hapus in app.peminjaman_anggota and app.peminjaman_anggota[id_hapus]: 
        console.print(Panel.fit(f"[bold orange_red1]❌ Anggota '{anggota['nama']}' (ID: {id_hapus}) masih memiliki buku yang dipinjam!\nTidak dapat dihapus hingga semua buku dikembalikan.[/bold orange_red1]", title="⚠️ Operasi Dibatalkan", border_style="red"))
        return

    konfirmasi_hapus_text = Text.assemble(
        ("❓ Anda YAKIN ingin menghapus anggota '", "bold orange_red1"),
        (anggota['nama'], "bold white"),
        ("' (ID: ", "bold orange_red1"),
        (id_hapus, "bold white"),
        (")? Tindakan ini ", "bold orange_red1"),
        ("TIDAK DAPAT DIURUNGKAN", "bold white on red"),
        ("!", "bold orange_red1")
    )
    if Confirm.ask(konfirmasi_hapus_text, default=False):
        del app.data_anggota[id_hapus]
        if id_hapus in app.keterlambatan: 
            del app.keterlambatan[id_hapus]
        for id_buku_antri in list(app.antrian_buku.keys()): 
            if id_hapus in app.antrian_buku[id_buku_antri]:
                app.antrian_buku[id_buku_antri].remove(id_hapus)
                if not app.antrian_buku[id_buku_antri]: 
                    del app.antrian_buku[id_buku_antri]

        simpan_semua_data(app)
        console.print(Panel.fit(f"[bold green]✅ Akun anggota '{anggota['nama']}' (ID: {id_hapus}) berhasil dihapus![/bold green]", title="🎉 Sukses", border_style="green"))
    else:
        console.print(Panel.fit("[italic yellow]ℹ️  Penghapusan akun anggota dibatalkan oleh pengguna.[/italic yellow]", title="Operasi Dibatalkan", border_style="yellow"))


# --- Fungsi pinjam_buku ---
def pinjam_buku(app):
    """
    Memproses peminjaman buku oleh anggota.
    Struktur data riwayat peminjaman DIUPDATE untuk mencakup deadline, tanggal aktual kembali, dan denda.
    """
    if app.kategori_saat_ini != "anggota": # Hanya anggota yang boleh meminjam
        console.print(Panel.fit("[bold red]❌ Fitur ini hanya bisa digunakan oleh Anggota![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    console.print(Panel("🛒 Proses Peminjaman Buku 🛒", style="bold spring_green2", border_style="spring_green2", expand=False, padding=1))
    
    lihat_buku(app) # Tampilkan daftar buku yang tersedia
    console.line()

    id_buku = Prompt.ask("[bold yellow]📚 Masukkan ID Buku yang ingin Anda pinjam[/bold yellow]")

    # Validasi input ID Buku
    if not id_buku.strip():
        console.print(Panel.fit("[bold red]❌ ID Buku tidak boleh kosong.[/bold red]", title="⚠️ Gagal", border_style="red"))
        return
    if id_buku not in app.data_buku:
        console.print(Panel.fit(f"[bold red]❌ ID Buku '{id_buku}' tidak ditemukan di perpustakaan.[/bold red]", title="⚠️ Gagal", border_style="red"))
        return

    buku_dipilih = app.data_buku[id_buku] # Ambil detail buku

    # Inisialisasi data peminjaman untuk anggota jika belum ada
    if app.pengguna_saat_ini not in app.peminjaman_anggota:
        app.peminjaman_anggota[app.pengguna_saat_ini] = {}

    # Cek apakah buku sudah pernah dipinjam dan belum dikembalikan
    if id_buku in app.peminjaman_anggota[app.pengguna_saat_ini]:
        console.print(Panel.fit(f"[bold orange_red1]❌ Anda sudah meminjam buku '[italic]{buku_dipilih['judul']}[/italic]' ini sebelumnya.[/bold orange_red1]", title="⚠️ Info", border_style="yellow"))
        return

    # Cek batas maksimal peminjaman
    if len(app.peminjaman_anggota[app.pengguna_saat_ini]) >= 3:
        console.print(Panel.fit("[bold orange_red1]❌ Anda sudah mencapai batas maksimal peminjaman (3 buku)! Kembalikan buku lain terlebih dahulu.[/bold orange_red1]", title="⚠️ Batas Peminjaman", border_style="yellow"))
        return
    
    # Cek ketersediaan stok
    if buku_dipilih['stok'] <= 0:
        antri_text = Text.assemble(
            (f"Stok buku '[italic]{buku_dipilih['judul']}[/italic]' sedang habis. ", "italic yellow"),
            ("Anda ingin masuk ke dalam antrian untuk buku ini?", "bold yellow")
        )
        if Confirm.ask(antri_text, default=True): # Tawarkan antrian
            if id_buku not in app.antrian_buku:
                app.antrian_buku[id_buku] = deque()
            if app.pengguna_saat_ini not in app.antrian_buku[id_buku]: 
                app.antrian_buku[id_buku].append(app.pengguna_saat_ini)
                simpan_semua_data(app)
                console.print(Panel.fit(f"[bold sky_blue1]Anda telah berhasil ditambahkan ke antrian untuk buku '[italic]{buku_dipilih['judul']}[/italic]'.[/bold sky_blue1]", title="ℹ️  Antrian Ditambahkan", border_style="sky_blue1"))
            else:
                console.print(Panel.fit(f"[bold sky_blue1]Anda sudah berada dalam antrian untuk buku '[italic]{buku_dipilih['judul']}[/italic]'. Harap tunggu giliran.[/bold sky_blue1]", title="ℹ️  Info Antrian", border_style="sky_blue1"))
        else:
            console.print(Panel.fit(f"[italic yellow]Anda memilih untuk tidak masuk antrian buku '[italic]{buku_dipilih['judul']}[/italic]'.[/italic yellow]", title="ℹ️  Info", border_style="yellow"))
        return # Selesai setelah proses antrian

    # Input durasi peminjaman
    while True:
        durasi_str = Prompt.ask(f"[bold yellow]🗓️  Berapa hari Anda ingin meminjam '[italic]{buku_dipilih['judul']}[/italic]'? (1–5 hari)[/bold yellow]")
        if durasi_str.isdigit() and 1 <= int(durasi_str) <= 5:
            durasi = int(durasi_str)
            break
        else:
            console.print(Panel.fit("[bold red]Masukkan angka antara 1 hingga 5 untuk durasi peminjaman.[/bold red]", title="⚠️ Input Salah", border_style="red"))

    tanggal_pinjam = datetime.now() # Tanggal peminjaman adalah hari ini
    tanggal_kembali_deadline = tanggal_pinjam + timedelta(days=durasi) # Hitung deadline

    # Catat peminjaman di data peminjaman_anggota (untuk buku aktif)
    app.peminjaman_anggota[app.pengguna_saat_ini][id_buku] = {
        "tanggal_pinjam": tanggal_pinjam.strftime("%Y-%m-%d"),
        "tanggal_kembali": tanggal_kembali_deadline.strftime("%Y-%m-%d") # Ini adalah deadline
    }
    # Kurangi stok buku
    app.data_buku[id_buku]['stok'] -= 1
    
    # Tambahkan ke riwayat peminjaman dengan struktur data yang KONSISTEN dan LENGKAP (PERBAIKAN UTAMA)
    app.riwayat_peminjaman.append({
        "id_buku": id_buku,
        "id_anggota": app.pengguna_saat_ini,
        "tanggal_pinjam": tanggal_pinjam.strftime("%Y-%m-%d"),
        "tanggal_kembali_deadline": tanggal_kembali_deadline.strftime("%Y-%m-%d"), # Field untuk deadline
        "tanggal_kembali_aktual": None,  # Field untuk tanggal aktual pengembalian, diisi saat buku kembali
        "denda_dibayar": 0 # Field untuk denda yang dibayar pada transaksi ini, diisi saat kembali
    })
    
    # Tambahkan ke log transaksi
    app.stack_transaksi.append(f"PINJAM: {app.pengguna_saat_ini} pinjam '{buku_dipilih['judul']}' (ID:{id_buku}) | {durasi} hari | Pinjam: {tanggal_pinjam.strftime('%d-%m-%Y')} | Deadline: {tanggal_kembali_deadline.strftime('%d-%m-%Y')}")
    simpan_semua_data(app) # Simpan semua perubahan
    console.print(Panel.fit(
        f"[bold green]✅ Buku '[italic]{buku_dipilih['judul']}[/italic]' berhasil dipinjam selama {durasi} hari!\n"
        f"⏳ Harap dikembalikan sebelum atau pada: {tanggal_kembali_deadline.strftime('%A, %d %B %Y')}.[/bold green]",
        title="🎉 Peminjaman Sukses!", border_style="green"
    ))

# --- Fungsi kembalikan_buku ---
def kembalikan_buku(app):
    """
    Memproses pengembalian buku oleh anggota.
    Struktur data riwayat peminjaman DIUPDATE dengan benar.
    """
    if app.kategori_saat_ini != 'anggota': # Cek otorisasi
        console.print(Panel.fit("[bold red]❌ Hanya Anggota yang bisa mengembalikan buku![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    if app.pengguna_saat_ini not in app.peminjaman_anggota or not app.peminjaman_anggota[app.pengguna_saat_ini]:
        console.print(Panel.fit("[italic yellow]Anda tidak memiliki buku yang sedang dipinjam saat ini.[/italic yellow]", title="ℹ️  Info", border_style="yellow"))
        return

    console.print(Panel("↩️  Proses Pengembalian Buku ↩️", style="bold deep_sky_blue1", border_style="deep_sky_blue1", expand=False, padding=1))
    
    table = Table(title=f"📖 Daftar Buku yang Anda Pinjam ({app.data_anggota[app.pengguna_saat_ini]['nama']}) 📖", show_header=True, header_style="bold deep_pink2", border_style="dim deep_sky_blue1", show_lines=True)
    table.add_column("No.", style="dim", width=5, justify="center")
    table.add_column("Judul Buku 📜", min_width=25, style="light_goldenrod1")
    table.add_column("ID Buku 🔢", justify="center", style="dim cyan")
    table.add_column("Deadline Kembali 🗓️", justify="center", style="light_salmon1")

    daftar_buku_obj = app.peminjaman_anggota[app.pengguna_saat_ini] 
    list_id_buku_dipinjam = list(daftar_buku_obj.keys()) 

    for i, id_buku_item in enumerate(list_id_buku_dipinjam, 1):
        buku_info_item = app.data_buku.get(id_buku_item, {})
        deadline_str_item = daftar_buku_obj[id_buku_item].get('tanggal_kembali', 'N/A') 
        deadline_formatted_item = deadline_str_item
        try:
            deadline_dt_item = datetime.strptime(deadline_str_item, "%Y-%m-%d")
            deadline_formatted_item = deadline_dt_item.strftime('%A, %d %b %Y')
            if datetime.now().date() > deadline_dt_item.date():
                 deadline_formatted_item = f"[bold red]{deadline_formatted_item} (Telat!)[/bold red]"
        except ValueError:
            pass
        table.add_row(str(i), buku_info_item.get('judul', 'N/A'), id_buku_item, deadline_formatted_item)
    console.print(table)
    console.line()

    if not list_id_buku_dipinjam:
        return

    pilihan_nomor_buku = Prompt.ask("[bold yellow]▶️  Pilih nomor urut buku yang ingin dikembalikan[/bold yellow]", choices=[str(i) for i in range(1, len(list_id_buku_dipinjam) + 1)], show_choices=False)
    
    id_buku_dikembalikan = list_id_buku_dipinjam[int(pilihan_nomor_buku) - 1] 
    buku_dikembalikan_info = app.data_buku.get(id_buku_dikembalikan, {}) 
    
    tanggal_pengembalian_aktual = datetime.now() 
    app.data_buku[id_buku_dikembalikan]['stok'] += 1 

    # Cari entri riwayat yang relevan untuk mendapatkan deadline dan update tanggal kembali aktual
    deadline_dt_buku = None
    log_peminjaman_untuk_update = None 

    for log_item in app.riwayat_peminjaman:
        # Cari log yang cocok: ID buku, ID anggota, dan BELUM ADA tanggal kembali aktual
        if log_item.get("id_buku") == id_buku_dikembalikan and \
           log_item.get("id_anggota") == app.pengguna_saat_ini and \
           log_item.get("tanggal_kembali_aktual") is None: # KUNCI PENTING: hanya update yang belum kembali
            log_peminjaman_untuk_update = log_item 
            # Ambil deadline dari field 'tanggal_kembali_deadline' yang sudah disimpan saat pinjam
            if log_item.get("tanggal_kembali_deadline"):
                try:
                    deadline_dt_buku = datetime.strptime(log_item["tanggal_kembali_deadline"], "%Y-%m-%d")
                except ValueError:
                    # Jika format salah (seharusnya tidak terjadi untuk data baru)
                    console.print(f"[italic orange_red1]Peringatan: Format tanggal deadline di riwayat untuk buku ID {id_buku_dikembalikan} tidak valid.[/italic orange_red1]")
                    pass 
            else:
                # Fallback jika 'tanggal_kembali_deadline' tidak ada di log riwayat (misal data lama)
                # Coba ambil dari app.peminjaman_anggota (yang menyimpan deadline di field 'tanggal_kembali')
                # Ini hanya sebagai jaring pengaman untuk data yang mungkin tidak konsisten
                detail_peminjaman_aktif = app.peminjaman_anggota.get(app.pengguna_saat_ini, {}).get(id_buku_dikembalikan, {})
                deadline_str_aktif = detail_peminjaman_aktif.get("tanggal_kembali")
                if deadline_str_aktif:
                    try:
                        deadline_dt_buku = datetime.strptime(deadline_str_aktif, "%Y-%m-%d")
                        # Update juga log riwayat dengan deadline ini jika belum ada
                        log_peminjaman_untuk_update["tanggal_kembali_deadline"] = deadline_str_aktif
                    except ValueError:
                        pass
            break # Asumsikan satu buku hanya bisa dipinjam sekali pada satu waktu oleh anggota yang sama dan belum dikembalikan

    denda = 0 # Inisialisasi denda
    # Hitung denda jika deadline ditemukan dan terlambat
    if deadline_dt_buku and tanggal_pengembalian_aktual.date() > deadline_dt_buku.date(): 
        hari_telat = (tanggal_pengembalian_aktual.date() - deadline_dt_buku.date()).days
        denda = hari_telat * 5000 
        app.keterlambatan[app.pengguna_saat_ini] = app.keterlambatan.get(app.pengguna_saat_ini, 0) + denda
        console.print(Panel.fit(
            f"[bold red]❗ ANDA TERLAMBAT MENGEMBALIKAN SELAMA {hari_telat} HARI ❗\n"
            f"Total Denda untuk buku ini: Rp {denda:,}\n"
            f"Mohon selesaikan pembayaran denda kepada petugas.[/bold red]",
            title="🚨 KETERLAMBATAN PENGEMBALIAN", border_style="red"
        ))
    elif not deadline_dt_buku: 
        console.print(Panel.fit("[bold orange_red1]⚠️ Tidak dapat memverifikasi deadline pengembalian dari riwayat. Denda tidak dapat dihitung secara otomatis untuk transaksi ini.[/bold orange_red1]", title="Peringatan Data", border_style="yellow"))
    else: # Jika tidak terlambat
        console.print(Panel.fit("[bold green]✅ Buku dikembalikan tepat waktu. Terima kasih![/bold green]", title="👍 Tepat Waktu", border_style="green"))

    # Update entri riwayat yang sudah ditemukan tadi (JIKA DITEMUKAN)
    if log_peminjaman_untuk_update:
        log_peminjaman_untuk_update["tanggal_kembali_aktual"] = tanggal_pengembalian_aktual.strftime("%Y-%m-%d")
        log_peminjaman_untuk_update["denda_dibayar"] = denda 
    else:
        # Jika tidak ada log yang cocok untuk diupdate. Ini bisa terjadi jika:
        # 1. Buku tidak pernah dipinjam oleh anggota ini (seharusnya sudah dicegah di awal).
        # 2. Entri riwayat saat peminjaman tidak dibuat dengan benar.
        # 3. Buku sudah dikembalikan sebelumnya dan log sudah diupdate.
        console.print(Panel.fit("[bold orange_red1]⚠️ Tidak menemukan entri riwayat peminjaman yang aktif untuk buku ini. Pengembalian mungkin sudah diproses atau ada inkonsistensi data.[/bold orange_red1]", title="Peringatan Data Riwayat", border_style="yellow"))


    # Hapus buku dari daftar peminjaman aktif anggota (setelah semua proses di atas)
    if app.pengguna_saat_ini in app.peminjaman_anggota and id_buku_dikembalikan in app.peminjaman_anggota[app.pengguna_saat_ini]:
        del app.peminjaman_anggota[app.pengguna_saat_ini][id_buku_dikembalikan]
        if not app.peminjaman_anggota[app.pengguna_saat_ini]: 
            del app.peminjaman_anggota[app.pengguna_saat_ini]
    else:
        # Ini tidak seharusnya terjadi jika alurnya benar
        console.print(f"[italic orange_red1]Peringatan: Buku ID {id_buku_dikembalikan} tidak ditemukan dalam daftar peminjaman aktif anggota {app.pengguna_saat_ini} untuk dihapus.[/italic orange_red1]")


    app.stack_transaksi.append(f"KEMBALI: {app.pengguna_saat_ini} kembali '{buku_dikembalikan_info.get('judul','N/A')}' (ID:{id_buku_dikembalikan}) | Tgl Kembali: {tanggal_pengembalian_aktual.strftime('%d-%m-%Y')} | Denda: Rp{denda:,}")
    console.print(Panel.fit(f"[bold green]✅ Buku '[italic]{buku_dikembalikan_info.get('judul', 'N/A')}[/italic]' berhasil diproses pengembaliannya![/bold green]", title="👍 Pengembalian Diproses", border_style="green"))

    # Cek antrian untuk buku yang baru dikembalikan
    if id_buku_dikembalikan in app.antrian_buku and app.antrian_buku[id_buku_dikembalikan]:
        id_anggota_berikutnya = app.antrian_buku[id_buku_dikembalikan].popleft() 
        if not app.antrian_buku[id_buku_dikembalikan]: 
            del app.antrian_buku[id_buku_dikembalikan]
        
        nama_anggota_berikutnya = app.data_anggota.get(id_anggota_berikutnya, {}).get('nama', f"Anggota ID {id_anggota_berikutnya}")
        console.print(Panel.fit(
            f"[bold sky_blue1]🔔 INFO ANTRIAN: Buku '[italic]{buku_dikembalikan_info.get('judul','N/A')}[/italic]' sekarang tersedia!\n"
            f"Otomatis akan dipinjamkan kepada {nama_anggota_berikutnya} (dari antrian).[/bold sky_blue1]",
            title="📢 Notifikasi Antrian", border_style="sky_blue1"
        ))

        durasi_otomatis = 3 
        tanggal_pinjam_otomatis = datetime.now()
        tanggal_kembali_otomatis_deadline = tanggal_pinjam_otomatis + timedelta(days=durasi_otomatis)

        if id_anggota_berikutnya not in app.peminjaman_anggota:
            app.peminjaman_anggota[id_anggota_berikutnya] = {}
        
        app.peminjaman_anggota[id_anggota_berikutnya][id_buku_dikembalikan] = {
            "tanggal_pinjam": tanggal_pinjam_otomatis.strftime("%Y-%m-%d"),
            "tanggal_kembali": tanggal_kembali_otomatis_deadline.strftime("%Y-%m-%d")
        }
        app.data_buku[id_buku_dikembalikan]['stok'] -= 1 
        # Tambahkan ke riwayat peminjaman untuk anggota berikutnya dengan struktur data yang benar
        app.riwayat_peminjaman.append({
            "id_buku": id_buku_dikembalikan,
            "id_anggota": id_anggota_berikutnya,
            "tanggal_pinjam": tanggal_pinjam_otomatis.strftime("%Y-%m-%d"),
            "tanggal_kembali_deadline": tanggal_kembali_otomatis_deadline.strftime("%Y-%m-%d"), 
            "tanggal_kembali_aktual": None, 
            "denda_dibayar": 0 
        })
        app.stack_transaksi.append(f"PINJAM (ANTRIAN): {id_anggota_berikutnya} pinjam '{buku_dikembalikan_info.get('judul','N/A')}' | {durasi_otomatis} hari | Deadline: {tanggal_kembali_otomatis_deadline.strftime('%d-%m-%Y')}")
        console.print(Panel.fit(f"[bold green]Buku '[italic]{buku_dikembalikan_info.get('judul','N/A')}[/italic]' telah otomatis dipinjamkan kepada {nama_anggota_berikutnya} selama {durasi_otomatis} hari.[/bold green]", title="✅ Peminjaman Otomatis Sukses", border_style="green"))

    simpan_semua_data(app) 


# --- Fungsi daftar_buku_dipinjam ---
# Tidak ada perubahan logika signifikan pada fungsi ini dari revisi sebelumnya.
# Komentar ditambahkan untuk menjelaskan fungsinya.
def daftar_buku_dipinjam(app):
    """Menampilkan daftar buku yang sedang dipinjam oleh anggota yang login."""
    if app.kategori_saat_ini != 'anggota':
        console.print(Panel.fit("[bold red]❌ Hanya Anggota yang bisa melihat daftar buku yang dipinjam![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    nama_anggota_info = app.data_anggota.get(app.pengguna_saat_ini, {}).get('nama', 'Anggota')
    console.print(Panel(f"📘 Daftar Buku yang Sedang Anda Pinjam ({nama_anggota_info}) 📘", style="bold deep_sky_blue1", border_style="deep_sky_blue1", expand=False, padding=1))

    if app.pengguna_saat_ini not in app.peminjaman_anggota or not app.peminjaman_anggota[app.pengguna_saat_ini]:
        console.print(Panel.fit("[italic yellow]Anda tidak memiliki buku yang sedang dipinjam saat ini.[/italic yellow]", title="ℹ️  Info", border_style="yellow"))
        return

    table = Table(title=f"⏳ Buku Pinjaman Milik {nama_anggota_info} (ID: {app.pengguna_saat_ini}) ⏳", show_header=True, header_style="bold deep_pink2", border_style="dim deep_sky_blue1", show_lines=True)
    table.add_column("No.", style="dim", width=5, justify="center")
    table.add_column("Judul Buku 📜", min_width=25, style="light_goldenrod1")
    table.add_column("ID Buku 🔢", justify="center", style="dim cyan")
    table.add_column("Dipinjam Sejak 🗓️", justify="center", style="pale_green1")
    table.add_column("Deadline Kembali ⏰", justify="center", style="light_salmon1")

    buku_dipinjam_obj_info = app.peminjaman_anggota[app.pengguna_saat_ini]
    ada_yang_telat_info = False 
    estimasi_denda_aktif = 0 

    for i, (id_buku_info, detail_pinjaman_info) in enumerate(buku_dipinjam_obj_info.items(), 1):
        buku_master_info_detail = app.data_buku.get(id_buku_info, {}) 
        tgl_pinjam_str_info = detail_pinjaman_info.get("tanggal_pinjam", "N/A")
        tgl_deadline_str_info = detail_pinjaman_info.get("tanggal_kembali", "N/A") 

        tgl_pinjam_formatted_info = tgl_pinjam_str_info
        try:
            if tgl_pinjam_str_info != 'N/A':
                tgl_pinjam_dt_info = datetime.strptime(tgl_pinjam_str_info, "%Y-%m-%d")
                tgl_pinjam_formatted_info = tgl_pinjam_dt_info.strftime('%d %b %Y')
        except ValueError: pass
        
        tgl_deadline_formatted_info = tgl_deadline_str_info
        try:
            if tgl_deadline_str_info != 'N/A':
                tgl_deadline_dt_info = datetime.strptime(tgl_deadline_str_info, "%Y-%m-%d")
                tgl_deadline_formatted_info = tgl_deadline_dt_info.strftime('%A, %d %b %Y')
                if datetime.now().date() > tgl_deadline_dt_info.date():
                    selisih_hari_info = (datetime.now().date() - tgl_deadline_dt_info.date()).days
                    tgl_deadline_formatted_info = f"[bold red]{tgl_deadline_formatted_info} (Terlambat {selisih_hari_info} hari!)[/bold red]"
                    ada_yang_telat_info = True
                    estimasi_denda_aktif += selisih_hari_info * 5000
        except ValueError: pass
            
        table.add_row(str(i), buku_master_info_detail.get('judul', 'N/A'), id_buku_info, tgl_pinjam_formatted_info, tgl_deadline_formatted_info)
    
    console.print(table)

    if ada_yang_telat_info:
        console.line()
        console.print(Panel.fit(
            f"[bold red]⚠️ PERINGATAN: Anda memiliki buku yang TERLAMBAT dikembalikan! ⚠️\n"
            f"Estimasi total denda untuk buku yang terlambat saat ini: Rp {estimasi_denda_aktif:,}\n"
            f"Segera kembalikan buku yang terlambat untuk menghindari denda lebih lanjut.",
            title="🚨 Notifikasi Keterlambatan Aktif", border_style="red"
        ))