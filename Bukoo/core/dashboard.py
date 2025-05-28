# File: Bukoo/core/dashboard.py

# Impor modul-modul yang diperlukan dari Rich dan datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text # Pastikan Text diimpor dengan benar
from datetime import datetime, timedelta

# Inisialisasi console Rich
console = Console()

def tampilkan_dashboard_staff(app):
    """Menampilkan dashboard untuk pengguna dengan kategori staff."""
    # --- Pengambilan Data (Tidak berubah signifikan, hanya memastikan .get() digunakan) ---
    nama_staff_dash = app.data_staff.get(app.pengguna_saat_ini, {}).get('nama', 'Staff')
    total_judul_buku_dash = len(app.data_buku)
    total_stok_buku_dash = sum(buku.get('stok', 0) for buku in app.data_buku.values())
    total_anggota_aktif_dash = len(app.data_anggota)
    
    total_buku_sedang_dipinjam_dash = 0
    for daftar_pinjaman in app.peminjaman_anggota.values():
        total_buku_sedang_dipinjam_dash += len(daftar_pinjaman)

    jumlah_peminjaman_telat_dash = 0
    if app.peminjaman_anggota:
        for daftar_pinjaman_telat in app.peminjaman_anggota.values():
            for detail_telat in daftar_pinjaman_telat.values():
                try:
                    deadline_dt_telat = datetime.strptime(detail_telat['tanggal_kembali'], "%Y-%m-%d")
                    if datetime.now().date() > deadline_dt_telat.date():
                        jumlah_peminjaman_telat_dash +=1
                except ValueError: 
                    pass # Abaikan jika format tanggal salah
    
    # Default value untuk buku populer (string dengan markup)
    buku_populer_markup_str = "[italic dim](Belum ada data peminjaman)[/italic dim]" 
    if app.riwayat_peminjaman:
        count_peminjaman_buku_dash = {}
        for log_dash in app.riwayat_peminjaman:
            id_buku_log_dash = log_dash.get('id_buku')
            if id_buku_log_dash: # Pastikan ID buku ada
                count_peminjaman_buku_dash[id_buku_log_dash] = count_peminjaman_buku_dash.get(id_buku_log_dash, 0) + 1
        
        if count_peminjaman_buku_dash: 
            try:
                id_buku_populer_dash = max(count_peminjaman_buku_dash, key=count_peminjaman_buku_dash.get)
                # Hasilnya bisa string biasa atau string dengan markup default jika tidak ketemu
                buku_populer_markup_str = app.data_buku.get(str(id_buku_populer_dash), {}).get('judul', '[italic dim](Data buku populer tidak tersedia)[/italic dim]')
            except ValueError: 
                 pass # Biarkan default value jika max() gagal

    # PERBAIKAN KUNCI: Ubah string yang MUNGKIN mengandung markup menjadi objek Text
    # Jika buku_populer_markup_str adalah judul buku biasa (tanpa markup), from_markup() akan menanganinya.
    # Jika sudah berisi markup, from_markup() akan mem-parse-nya.
    buku_populer_text_obj = Text.from_markup(buku_populer_markup_str)

    tanggal_hari_ini = datetime.now()
    tanggal_hari_ini_str = tanggal_hari_ini.strftime("%A, %d %B %Y")

    # Susun konten dashboard menggunakan Text.assemble
    # Saat memasukkan objek Text (seperti buku_populer_text_obj), jangan berikan style tambahan padanya di tuple assemble.
    dashboard_content_staff = Text.assemble(
        (f"👋 Halo, ", "default"), (nama_staff_dash, "bold spring_green2"), (f"! (ID Staff: {app.pengguna_saat_ini})\n\n", "default"),
        (f"📅 Hari ini: ", "default"), (f"{tanggal_hari_ini_str}\n\n"),
        (" Ringkasan Perpustakaan:\n", "dim italic"),
        ("📚 Total Judul Buku      : ", "default"), (str(total_judul_buku_dash), "bold white"), (" judul\n", "default"),
        ("📦 Total Stok Tersedia   : ", "default"), (str(total_stok_buku_dash), "bold white"), (" unit\n", "default"),
        ("👥 Total Anggota Aktif   : ", "default"), (str(total_anggota_aktif_dash), "bold white"), (" anggota\n\n", "default"),
        (" Aktivitas Saat Ini:\n", "dim italic"),
        ("📤 Buku Sedang Dipinjam  : ", "default"), (str(total_buku_sedang_dipinjam_dash), "bold white"), (" unit\n", "default"),
        ("🚨 Jml. Pinjaman Telat*  : ", "default"), (str(jumlah_peminjaman_telat_dash), "bold red" if jumlah_peminjaman_telat_dash > 0 else "bold white"), (" unit\n", "default"),
        ("🌟 Buku Terpopuler       : ", "default"), buku_populer_text_obj, ("\n\n", "default"), # Masukkan objek Text yang sudah diparsing
        ("*Berdasarkan buku yang masih aktif dipinjam & melewati deadline.", "dim italic")
    )
    # Tampilkan Panel yang berisi objek Text yang sudah dirakit
    console.print(Panel(dashboard_content_staff, title="👑 DASHBOARD STAFF PERPUSTAKAAN BUKOO 👑", style="bold green_yellow", border_style="green_yellow", width=75, padding=(1,2)))

def tampilkan_dashboard_anggota(app):
    """Menampilkan dashboard untuk pengguna dengan kategori anggota."""
    nama_anggota_dash_user = app.data_anggota.get(app.pengguna_saat_ini, {}).get('nama', 'Anggota')
    
    buku_dipinjam_saat_ini_user = app.peminjaman_anggota.get(app.pengguna_saat_ini, {})
    jumlah_buku_dipinjam_user = len(buku_dipinjam_saat_ini_user)
    
    total_denda_tercatat_user = app.keterlambatan.get(app.pengguna_saat_ini, 0) 

    # Default value untuk deadline terdekat (string dengan markup)
    deadline_terdekat_markup_str = "[italic dim]Tidak ada buku dipinjam[/italic dim]" 
    if buku_dipinjam_saat_ini_user: 
        try:
            deadlines_user = [datetime.strptime(b_info['tanggal_kembali'], "%Y-%m-%d") for b_info in buku_dipinjam_saat_ini_user.values()]
            if deadlines_user:
                deadline_terdekat_dt_user = min(deadlines_user)
                deadline_terdekat_plain_str = deadline_terdekat_dt_user.strftime('%A, %d %B %Y') # Versi string biasa
                if datetime.now().date() > deadline_terdekat_dt_user.date(): 
                    selisih_hari_user = (datetime.now().date() - deadline_terdekat_dt_user.date()).days
                    # Buat string dengan markup jika terlambat
                    deadline_terdekat_markup_str = f"[bold red]{deadline_terdekat_plain_str} (TERLAMBAT {selisih_hari_user} hari!)[/bold red]"
                else:
                    deadline_terdekat_markup_str = deadline_terdekat_plain_str # Gunakan string biasa jika tidak telat
        except ValueError: 
            deadline_terdekat_markup_str = "[italic red]Error data tanggal pinjaman[/italic red]"

    # PERBAIKAN KUNCI: Ubah string yang MUNGKIN mengandung markup menjadi objek Text
    deadline_terdekat_text_obj = Text.from_markup(deadline_terdekat_markup_str)

    # Default value untuk buku populer umum (string dengan markup)
    buku_populer_umum_markup_str = "[italic dim](Belum ada data peminjaman)[/italic dim]"
    if app.riwayat_peminjaman: 
        count_peminjaman_buku_global_user = {}
        for log_user in app.riwayat_peminjaman:
            id_buku_log_user = log_user.get('id_buku') 
            if id_buku_log_user: 
                count_peminjaman_buku_global_user[id_buku_log_user] = count_peminjaman_buku_global_user.get(id_buku_log_user, 0) + 1
        if count_peminjaman_buku_global_user:
            try:
                id_buku_populer_global_user = max(count_peminjaman_buku_global_user, key=count_peminjaman_buku_global_user.get)
                buku_populer_umum_markup_str = app.data_buku.get(str(id_buku_populer_global_user), {}).get('judul', '[italic dim](Data buku populer tidak tersedia)[/italic dim]')
            except ValueError:
                 pass 
    
    # PERBAIKAN KUNCI: Ubah string yang MUNGKIN mengandung markup menjadi objek Text
    buku_populer_umum_text_obj = Text.from_markup(buku_populer_umum_markup_str)

    tanggal_hari_ini = datetime.now()
    tanggal_hari_ini_str = tanggal_hari_ini.strftime("%A, %d %B %Y")

    # Susun konten dashboard anggota
    dashboard_content_anggota = Text.assemble(
        (f"👋 Halo, ", "default"), (nama_anggota_dash_user, "bold dodger_blue1"), (f"! (ID Anggota: {app.pengguna_saat_ini})\n\n", "default"),
        (f"📅 Hari ini: ", "default"), (f"{tanggal_hari_ini_str}\n\n", "cyan"),
        (" Aktivitas Peminjaman Anda:\n", "dim italic"),
        ("📖 Jml. Buku Dipinjam  : ", "default"), (str(jumlah_buku_dipinjam_user), "bold white"), (" buku\n", "default"),
        ("🗓️  Deadline Terdekat   : ", "default"), deadline_terdekat_text_obj, ("\n", "default"), # Masukkan objek Text
        ("💸 Akumulasi Denda     : ", "default"), (f"Rp {total_denda_tercatat_user:,}", "bold red" if total_denda_tercatat_user > 0 else "bold white"), (" (Total denda tercatat)\n\n", "default"),
        (" Info Perpustakaan:\n", "dim italic"),
        ("🌟 Buku Populer Umum   : ", "default"), buku_populer_umum_text_obj, ("\n", "default") # Masukkan objek Text
    )
    # Tampilkan Panel yang berisi objek Text yang sudah dirakit
    console.print(Panel(dashboard_content_anggota, title="🧑 DASHBOARD ANGGOTA PERPUSTAKAAN BUKOO 🧑", style="bold deep_sky_blue2", border_style="deep_sky_blue2", width=75, padding=(1,2)))