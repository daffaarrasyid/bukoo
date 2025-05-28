# File: Bukoo/core/laporan.py

# Impor modul dari Rich dan datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm 
from datetime import datetime

# Inisialisasi console Rich
console = Console()

def tampilkan_riwayat_peminjaman(app):
    """
    Menampilkan seluruh riwayat peminjaman dan pengembalian buku.
    Disesuaikan untuk menangani struktur data riwayat lama dan baru secara lebih robust.
    """
    console.print(Panel("📜 Riwayat Seluruh Transaksi Peminjaman & Pengembalian 📜", style="bold steel_blue", border_style="steel_blue", expand=False, padding=1))
    if not app.riwayat_peminjaman: # Jika tidak ada riwayat
        console.print(Panel.fit("[italic yellow]Belum ada riwayat peminjaman buku di sistem.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return

    table = Table(title="🗂️ Arsip Lengkap Transaksi Perpustakaan 🗂️", show_header=True, header_style="bold dark_sea_green4", border_style="dim steel_blue", min_width=110, show_lines=True)
    table.add_column("Nama Anggota 👤", min_width=15, style="light_slate_grey")
    table.add_column("ID Anggota 🆔", justify="center", style="dim")
    table.add_column("Judul Buku 📖", min_width=25, style="light_goldenrod1")
    table.add_column("ID Buku 🔢", justify="center", style="dim")
    table.add_column("Tgl. Pinjam 🗓️", justify="center", style="pale_green1")
    table.add_column("Deadline Kembali ⏰", justify="center", style="light_salmon1") # Field baru
    table.add_column("Tgl. Kembali Aktual ✅", justify="center", style="medium_spring_green") # Field baru
    table.add_column("Denda Dibayar (Rp) 💸", justify="right", style="orange_red1") # Field baru

    # Urutkan riwayat berdasarkan tanggal pinjam terbaru
    sorted_riwayat = sorted(app.riwayat_peminjaman, key=lambda x: datetime.strptime(x.get("tanggal_pinjam", "1900-01-01"), "%Y-%m-%d"), reverse=True)

    for log in sorted_riwayat:
        # Ambil data dengan .get() untuk menghindari KeyError jika field tidak ada (terutama untuk data lama)
        id_buku_log = log.get("id_buku")
        id_anggota_log = log.get("id_anggota")
        judul_buku_log = app.data_buku.get(str(id_buku_log), {}).get("judul", "[italic dim](Buku Dihapus)[/italic dim]")
        nama_anggota_log = app.data_anggota.get(str(id_anggota_log), {}).get("nama", "[italic dim](Anggota Dihapus)[/italic dim]")
        
        tgl_pinjam_log_str = log.get("tanggal_pinjam", "-")
        
        # Penanganan untuk 'tanggal_kembali_deadline' (field baru)
        tgl_deadline_log_str = log.get("tanggal_kembali_deadline")
        # Penanganan untuk 'tanggal_kembali_aktual' (field baru)
        tgl_kembali_aktual_log_str = log.get("tanggal_kembali_aktual")
        # Denda yang dibayar saat transaksi pengembalian itu
        denda_log = log.get("denda_dibayar", 0) 
        denda_log_str = f"{denda_log:,}" if denda_log > 0 else "-"

        # Untuk data lama yang hanya punya 'tanggal_kembali':
        # Jika 'tanggal_kembali_aktual' tidak ada DAN 'tanggal_kembali' (field lama) ada,
        # maka 'tanggal_kembali' (lama) bisa jadi adalah tanggal kembali aktualnya.
        if tgl_kembali_aktual_log_str is None and "tanggal_kembali" in log and log["tanggal_kembali"] is not None:
            tgl_kembali_aktual_log_str = log.get("tanggal_kembali") 
            # Jika data lama ini adalah tanggal kembali aktual, maka deadline nya tidak tercatat secara eksplisit
            # Kita bisa biarkan tgl_deadline_log_str menjadi None/ "-" atau coba inferensi jika ada aturan durasi pinjam lama.
            # Untuk sekarang, jika 'tanggal_kembali_deadline' tidak ada, akan jadi "-"
            if tgl_deadline_log_str is None:
                 tgl_deadline_log_str = "[italic dim](Tidak tercatat)[/italic dim]"


        # Format tanggal pinjam
        tgl_pinjam_log_formatted = tgl_pinjam_log_str
        try:
            if tgl_pinjam_log_str != "-":
                tgl_pinjam_log_dt = datetime.strptime(tgl_pinjam_log_str, "%Y-%m-%d")
                tgl_pinjam_log_formatted = tgl_pinjam_log_dt.strftime('%d %b %Y')
        except ValueError: pass 
        
        # Format tanggal deadline
        tgl_deadline_log_formatted = tgl_deadline_log_str if tgl_deadline_log_str else "-"
        deadline_dt_for_check = None 
        try:
            if tgl_deadline_log_str and tgl_deadline_log_str != "-" and tgl_deadline_log_str != "[italic dim](Tidak tercatat)[/italic dim]":
                deadline_dt_for_check = datetime.strptime(tgl_deadline_log_str, "%Y-%m-%d")
                tgl_deadline_log_formatted = deadline_dt_for_check.strftime('%d %b %Y')
        except ValueError: pass

        # Format tanggal kembali aktual
        tgl_kembali_aktual_log_formatted = "[italic dim]Belum Kembali[/italic dim]"
        if tgl_kembali_aktual_log_str and tgl_kembali_aktual_log_str != "-": 
            try:
                tgl_kembali_aktual_log_dt = datetime.strptime(tgl_kembali_aktual_log_str, "%Y-%m-%d")
                tgl_kembali_aktual_log_formatted = tgl_kembali_aktual_log_dt.strftime('%d %b %Y')
                # Cek apakah pengembalian aktual melewati deadline (jika deadline ada)
                if deadline_dt_for_check and tgl_kembali_aktual_log_dt.date() > deadline_dt_for_check.date():
                    tgl_kembali_aktual_log_formatted = f"[bold red]{tgl_kembali_aktual_log_formatted} (Telat)[/bold red]" 
            except ValueError: 
                # Jika format tgl_kembali_aktual_log_str salah (misal dari data lama yang "null" jadi string)
                 tgl_kembali_aktual_log_formatted = "[italic dim]Belum Kembali[/italic dim]" if tgl_kembali_aktual_log_str.lower() == "null" else tgl_kembali_aktual_log_str


        table.add_row(
            nama_anggota_log, str(id_anggota_log), judul_buku_log, str(id_buku_log), 
            tgl_pinjam_log_formatted, tgl_deadline_log_formatted, 
            tgl_kembali_aktual_log_formatted, denda_log_str
        )
    console.print(table)

# ... (sisa fungsi laporan_peminjaman, laporan_keterlambatan, lihat_buku_populer, laporan_total_akumulasi_denda tetap sama seperti revisi sebelumnya)
# Pastikan untuk me-review dan menambahkan komentar pada fungsi-fungsi tersebut juga dengan pola yang sama jika belum.
def laporan_peminjaman(app): 
    """Menampilkan laporan buku yang sedang aktif dipinjam oleh semua anggota."""
    console.print(Panel("📊 Laporan Buku yang Sedang Dipinjam (Global) 📊", style="bold steel_blue", border_style="steel_blue", expand=False, padding=1))
    
    if not app.peminjaman_anggota: 
        console.print(Panel.fit("[italic yellow]Saat ini tidak ada buku yang sedang dipinjam oleh anggota manapun.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return
    
    table = Table(title="📚 Daftar Buku yang Sedang Aktif Dipinjam 📚", show_header=True, header_style="bold dark_sea_green4", border_style="dim steel_blue", min_width=90, show_lines=True)
    table.add_column("Nama Peminjam 👤", min_width=20, style="light_slate_grey")
    table.add_column("ID Anggota 🆔", justify="center", style="dim")
    table.add_column("Judul Buku 📖", min_width=25, style="light_goldenrod1")
    table.add_column("ID Buku 🔢", justify="center", style="dim")
    table.add_column("Dipinjam Sejak 🗓️", justify="center", style="pale_green1")
    table.add_column("Deadline Kembali ⏰", justify="center", style="light_salmon1")
    
    ada_peminjaman_aktif_laporan = False
    for id_anggota_lap, daftar_pinjaman_lap in app.peminjaman_anggota.items():
        nama_peminjam_lap = app.data_anggota.get(id_anggota_lap, {}).get("nama", "[italic dim](Anggota Dihapus)[/italic dim]")
        for id_buku_lap, detail_pinjaman_lap in daftar_pinjaman_lap.items():
            ada_peminjaman_aktif_laporan = True
            judul_buku_lap = app.data_buku.get(id_buku_lap, {}).get("judul", "[italic dim](Buku Dihapus)[/italic dim]")
            
            tgl_pinjam_lap_str = detail_pinjaman_lap.get('tanggal_pinjam', 'N/A')
            deadline_lap_str = detail_pinjaman_lap.get('tanggal_kembali', 'N/A') # 'tanggal_kembali' di peminjaman_anggota adalah deadline
            
            tgl_pinjam_lap_formatted = tgl_pinjam_lap_str
            try:
                if tgl_pinjam_lap_str != 'N/A':
                    tgl_pinjam_lap_dt = datetime.strptime(tgl_pinjam_lap_str, "%Y-%m-%d")
                    tgl_pinjam_lap_formatted = tgl_pinjam_lap_dt.strftime('%d %b %Y')
            except: pass

            deadline_lap_formatted = deadline_lap_str
            try:
                if deadline_lap_str != 'N/A':
                    deadline_lap_dt = datetime.strptime(deadline_lap_str, "%Y-%m-%d")
                    deadline_lap_formatted = deadline_lap_dt.strftime('%A, %d %b %Y')
                    if datetime.now().date() > deadline_lap_dt.date():
                        selisih_hari_lap = (datetime.now().date() - deadline_lap_dt.date()).days
                        deadline_lap_formatted = f"[bold red]{deadline_lap_formatted} (Telat {selisih_hari_lap} hr!)[/bold red]"
            except: pass

            table.add_row(nama_peminjam_lap, str(id_anggota_lap), judul_buku_lap, str(id_buku_lap), tgl_pinjam_lap_formatted, deadline_lap_formatted)
            
    if not ada_peminjaman_aktif_laporan:
         console.print(Panel.fit("[italic yellow]Tidak ada buku yang aktif dipinjam saat ini untuk dilaporkan.[/italic yellow]", title="ℹ️  Info", border_style="yellow"))
         return
    
    console.print(table)

def laporan_keterlambatan(app): 
    """Menampilkan laporan akumulasi denda keterlambatan per anggota."""
    console.print(Panel("⏰ Laporan Akumulasi Denda Keterlambatan per Anggota ⏰", style="bold indian_red", border_style="indian_red", expand=False, padding=1))
    
    if not app.keterlambatan: 
        console.print(Panel.fit("[italic yellow]Belum ada catatan denda keterlambatan untuk anggota manapun.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return

    table = Table(title="💸 Rekapitulasi Total Denda Anggota (Tercatat) 💸", show_header=True, header_style="bold red3", border_style="dim indian_red", min_width=60, show_lines=True)
    table.add_column("Nama Anggota 👤", min_width=20, style="light_slate_grey")
    table.add_column("ID Anggota 🆔", justify="center", style="dim")
    table.add_column("Total Akumulasi Denda (Rp) 💰", justify="right", style="bold gold3")

    ada_data_keterlambatan_laporan = False
    for id_anggota_denda, total_denda_denda in app.keterlambatan.items():
        if total_denda_denda > 0: 
            ada_data_keterlambatan_laporan = True
            nama_anggota_denda = app.data_anggota.get(id_anggota_denda, {}).get("nama", "[italic dim](Anggota Dihapus)[/italic dim]")
            table.add_row(nama_anggota_denda, str(id_anggota_denda), f"{total_denda_denda:,}") 
    
    if not ada_data_keterlambatan_laporan:
        console.print(Panel.fit("[italic yellow]Tidak ada anggota dengan catatan denda aktif saat ini.[/italic yellow]", title="✅ Bersih", border_style="green"))
        return
        
    console.print(table)
    console.print(Panel.fit("[italic dim]Catatan: Denda di atas adalah total denda yang pernah tercatat untuk setiap anggota.\nStatus pelunasan perlu diverifikasi secara manual oleh petugas perpustakaan.[/italic dim]", title="ℹ️  Disclaimer Pembayaran", border_style="dim"))

def lihat_buku_populer(app):
    """Menampilkan 5 buku terpopuler berdasarkan frekuensi peminjaman."""
    if app.kategori_saat_ini != 'staff':
        console.print(Panel.fit("[bold red]❌ Hanya Staff yang dapat mengakses fitur ini![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    console.print(Panel("🏆 Top 5 Buku Terpopuler di BUKOO (Berdasarkan Jumlah Peminjaman) 🏆", style="bold dark_goldenrod", border_style="dark_goldenrod", expand=False, padding=1))
    
    if not app.riwayat_peminjaman:
        console.print(Panel.fit("[italic yellow]Belum ada data peminjaman buku untuk menentukan popularitas.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return

    frekuensi_buku_pop = {}
    for peminjaman_pop in app.riwayat_peminjaman:
        id_buku_pop = peminjaman_pop.get("id_buku") # Gunakan .get() untuk keamanan
        if id_buku_pop: # Pastikan id_buku tidak None
            frekuensi_buku_pop[id_buku_pop] = frekuensi_buku_pop.get(id_buku_pop, 0) + 1

    if not frekuensi_buku_pop:
        console.print(Panel.fit("[italic yellow]Tidak ada buku yang pernah dipinjam, popularitas belum bisa ditentukan.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return

    buku_populer_sorted_list = sorted(frekuensi_buku_pop.items(), key=lambda x: x[1], reverse=True)
    top_5_buku_list = buku_populer_sorted_list[:5]

    table = Table(title="🌟 Lima Buku Paling Sering Dipinjam di Perpustakaan 🌟", show_header=True, header_style="bold gold1", border_style="dim dark_goldenrod", min_width=70, show_lines=True)
    table.add_column("Peringkat 🏅", style="dim", width=10, justify="center")
    table.add_column("Judul Buku (ID) 📖", min_width=35, style="light_goldenrod1")
    table.add_column("Total Kali Dipinjam 📈", justify="center", style="bold green3")

    if not top_5_buku_list: 
        console.print(Panel.fit("[italic yellow]Tidak cukup data untuk menampilkan buku populer.[/italic yellow]", title="ℹ️  Info", border_style="yellow"))
        return

    for rank, (id_buku_rank, jumlah_dipinjam_rank) in enumerate(top_5_buku_list, start=1):
        buku_info_rank = app.data_buku.get(str(id_buku_rank), {}) # Pastikan ID adalah string jika keys di data_buku string
        judul_rank = buku_info_rank.get("judul", "[italic dim](Buku Dihapus)[/italic dim]")
        table.add_row(f"#{rank}", f"{judul_rank} (ID: {id_buku_rank})", f"{jumlah_dipinjam_rank} kali")

    console.print(table)

def laporan_total_akumulasi_denda(app):
    """Menampilkan total akumulasi denda dari semua anggota yang tercatat oleh Staff."""
    if app.kategori_saat_ini != 'staff':
        console.print(Panel.fit("[bold red]❌ Fitur ini hanya untuk Staff![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    console.print(Panel("💰 Laporan Total Akumulasi Denda Seluruh Anggota 💰", style="bold gold1", border_style="gold1", expand=False, padding=1))

    if not app.keterlambatan:
        console.print(Panel.fit("[italic yellow]Belum ada catatan denda keterlambatan dari anggota manapun.[/italic yellow]", title="ℹ️  Info Kosong", border_style="yellow"))
        return

    total_semua_denda = sum(app.keterlambatan.values())

    table = Table(title="💸 Rekapitulasi Total Semua Denda Anggota (Tercatat) 💸", show_header=False, border_style="dim gold1", width=70, show_lines=True)
    table.add_column("Deskripsi", style="light_slate_grey", min_width=35) 
    table.add_column("Jumlah (Rp)", style="bold yellow", justify="right", min_width=25) 

    table.add_row("Total Akumulasi Denda dari Semua Anggota Tercatat", f"Rp {total_semua_denda:,}") 
    
    console.print(table)
    console.print(Panel.fit("[italic dim]Catatan: Ini adalah total dari semua denda yang pernah tercatat di sistem untuk semua anggota.\nStatus pelunasan aktual untuk setiap denda perlu diverifikasi secara manual oleh petugas.[/italic dim]", title="ℹ️  Disclaimer Global", border_style="dim"))