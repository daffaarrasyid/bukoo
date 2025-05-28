# File: Bukoo/main.py

# Impor modul-modul yang diperlukan
import pyfiglet # Untuk membuat teks ASCII art sebagai header
from rich.console import Console # Komponen utama Rich untuk output ke console
from rich.panel import Panel # Untuk membuat panel/box di UI
from rich.text import Text # Untuk teks dengan styling kaya
from rich.prompt import Prompt, Confirm # Untuk input pengguna yang interaktif

# Import fungsi dari modul-modul lokal dalam paket 'core'
from core.utils import simpan_semua_data, muat_semua_data
from core.auth import daftar, masuk, keluar
from core.buku import tambah_buku, edit_buku, hapus_buku, lihat_buku, cari_buku
from core.anggota import hapus_anggota, pinjam_buku, kembalikan_buku, daftar_buku_dipinjam
# Impor fungsi laporan, termasuk fungsi baru laporan_total_akumulasi_denda
from core.laporan import (
    tampilkan_riwayat_peminjaman, 
    laporan_peminjaman, 
    laporan_keterlambatan, 
    lihat_buku_populer,
    laporan_total_akumulasi_denda # Fungsi baru diimpor
)
from core.dashboard import tampilkan_dashboard_staff, tampilkan_dashboard_anggota

# Inisialisasi console Rich
console = Console()

class Bukoo:
    """Kelas utama untuk aplikasi perpustakaan Bukoo."""
    def __init__(self):
        """Inisialisasi semua atribut data aplikasi."""
        self.data_buku = {} # Dictionary untuk menyimpan data buku
        self.data_staff = {} # Dictionary untuk menyimpan data staff
        self.data_anggota = {} # Dictionary untuk menyimpan data anggota
        self.riwayat_peminjaman = [] # List untuk menyimpan riwayat peminjaman
        self.peminjaman_anggota = {} # Dictionary untuk melacak buku yang sedang dipinjam per anggota
        self.keterlambatan = {} # Dictionary untuk menyimpan akumulasi denda per anggota
        self.antrian_buku = {} # Dictionary untuk antrian peminjaman buku
        self.stack_transaksi = [] # List untuk log transaksi (bisa dikembangkan untuk undo/audit)
        self.pengguna_saat_ini = None # Menyimpan ID pengguna yang sedang login
        self.kategori_saat_ini = None # Menyimpan kategori pengguna (staff/anggota)
        self.muatan_data() # Memuat semua data dari file JSON saat aplikasi dimulai

    def simpan_data(self):
        """Menyimpan semua data aplikasi ke file JSON."""
        simpan_semua_data(self) # Panggil fungsi utilitas untuk menyimpan data

    def muatan_data(self):
        """Memuat semua data aplikasi dari file JSON."""
        muat_semua_data(self) # Panggil fungsi utilitas untuk memuat data

    def tampilkan_header(self):
        """Menampilkan header aplikasi menggunakan pyfiglet dan Rich."""
        # Pilih font untuk header, contoh 'doom' (bisa diganti sesuai selera)
        font_pilihan = "doom" 
        try:
            # Buat ASCII art dengan font yang dipilih
            ascii_art = pyfiglet.figlet_format("BUKOO", font=font_pilihan)
        except pyfiglet.FontNotFound:
            # Fallback jika font pilihan tidak ditemukan, gunakan font standar
            console.print(f"[italic yellow]Font '{font_pilihan}' tidak ditemukan, menggunakan font default 'standard'.[/italic yellow]")
            ascii_art = pyfiglet.figlet_format("BUKOO", font="standard")

        # Styling header dengan Rich Text
        header_text = Text(ascii_art, justify="center", style="bold bright_magenta")
        # Tampilkan header
        console.print(header_text)
        # Garis pemisah opsional atau subtitle bisa ditambahkan di sini
        # console.print(Text("--- Sistem Perpustakaan Terminal Modern ---", justify="center", style="italic cyan"))
        # console.rule(style="dim blue") 
        console.line(1) # Beri jarak setelah header

    def menu(self):
        """Menampilkan menu utama aplikasi dan menghandle navigasi pengguna."""
        while True: # Loop utama aplikasi, akan terus berjalan hingga pengguna memilih keluar
            console.line(1) # Beri jarak visual antar menu
            
            # Cek apakah ada pengguna yang sedang login
            if not self.pengguna_saat_ini:
                # Jika tidak ada pengguna login, tampilkan menu awal
                console.print(Panel("[bold white on blue] Selamat Datang di BUKOO! [/bold white on blue]", title="📚 Menu Awal 📚", border_style="bright_blue", expand=False, padding=(1,2)))
                console.print("[cyan]1.[/cyan] 📝 Daftar Akun Baru")
                console.print("[cyan]2.[/cyan] 🔑 Masuk ke Akun")
                console.print("[cyan]3.[/cyan] 🚪 Keluar Aplikasi")
                # Minta pilihan menu dari pengguna
                pilihan = Prompt.ask("[bold yellow]▶️  Pilih menu[/bold yellow]", choices=["1","2","3"], show_choices=False)
                console.line(1)
                console.print("─" * 60, style="dim blue") # Garis pemisah visual

                # Proses pilihan menu awal
                if pilihan == '1':
                    daftar(self) # Panggil fungsi pendaftaran dari modul auth
                elif pilihan == '2':
                    masuk(self) # Panggil fungsi login dari modul auth
                elif pilihan == '3':
                    # --- KONFIRMASI KELUAR APLIKASI ---
                    if Confirm.ask("[bold orange_red1]❓ Anda yakin ingin keluar dari aplikasi Bukoo?[/bold orange_red1]", default=False):
                        console.print(Panel("👋 Terima kasih telah menggunakan BUKOO! Sampai jumpa lagi! 👋", style="bold green", padding=(1, 3), border_style="green", expand=False))
                        break # Keluar dari loop utama, mengakhiri aplikasi
                    else:
                        console.print("[italic yellow]ℹ️  Keluar dari aplikasi dibatalkan.[/italic yellow]")
                        continue # Kembali ke awal loop menu awal
            else: # Jika ada pengguna yang login
                # Cek kategori pengguna (staff atau anggota)
                if self.kategori_saat_ini == 'staff':
                    # Tampilkan dashboard dan menu untuk staff
                    tampilkan_dashboard_staff(self) # Panggil dashboard staff
                    console.print(Panel("[bold white on green] Menu Utama (Staff) [/bold white on green]", border_style="bright_green", expand=False, padding=(1,2)))
                    console.print("[cyan]1.[/cyan] 📖 Manajemen Data (Buku & Anggota)")
                    console.print("[cyan]2.[/cyan] 🔎 Pencarian Buku")
                    console.print("[cyan]3.[/cyan] 📊 Laporan & Statistik")
                    console.print("[cyan]4.[/cyan] 🚪 Logout Akun")
                    pilihan_staff = Prompt.ask("[bold yellow]▶️  Pilih menu staff[/bold yellow]", choices=[str(i) for i in range(1,5)], show_choices=False)
                    console.line(1)
                    console.print("─" * 60, style="dim green")
                    
                    # Proses pilihan menu staff
                    if pilihan_staff == '1': # Opsi Manajemen Data
                        console.print(Panel("[bold white on blue] Sub-Menu: Manajemen Data [/bold white on blue]", title="📋 Opsi Manajemen 📋", border_style="bright_blue", expand=False, padding=(1,2)))
                        console.print("[cyan]1.[/cyan] ✨ Tambah Buku Baru")
                        console.print("[cyan]2.[/cyan] ✏️  Edit Informasi Buku")
                        console.print("[cyan]3.[/cyan] 🗑️  Hapus Buku dari Sistem")
                        console.print("[cyan]4.[/cyan] 📚 Lihat Daftar Semua Buku")
                        console.print("[cyan]5.[/cyan] 👤 Hapus Akun Anggota")
                        console.print("[cyan]6.[/cyan] ⬅️  Kembali ke Menu Utama")
                        pilihan_manajemen = Prompt.ask("[bold yellow]▶️  Pilih opsi manajemen[/bold yellow]", choices=[str(i) for i in range(1,7)], show_choices=False)
                        console.line(1)
                        console.print("─" * 60, style="dim blue")
                        # Panggil fungsi sesuai pilihan manajemen
                        if pilihan_manajemen == '1': tambah_buku(self)
                        elif pilihan_manajemen == '2': edit_buku(self)
                        elif pilihan_manajemen == '3': hapus_buku(self)
                        elif pilihan_manajemen == '4': lihat_buku(self)
                        elif pilihan_manajemen == '5': hapus_anggota(self)
                        elif pilihan_manajemen == '6':
                            # --- KONFIRMASI KEMBALI KE MENU UTAMA (OPSIONAL) ---
                            if Confirm.ask("[bold yellow]❓ Kembali ke Menu Utama Staff?[/bold yellow]", default=True): # Default Ya karena ini aksi umum
                                continue # Kembali ke menu utama staff
                            else:
                                # Tetap di sub-menu manajemen jika dibatalkan (perlu sedikit penyesuaian loop sub-menu)
                                # Agar tetap di sub-menu, loop sub-menu mungkin perlu dibuat terpisah
                                # Untuk kesederhanaan saat ini, jika batal, anggap saja kembali juga
                                console.print("[italic red]Membatalkan kembali ke menu utama... (tetap di menu utama staff)[/italic red]")
                                continue
                    
                    elif pilihan_staff == '2': # Opsi Pencarian Buku
                        cari_buku(self)
                    
                    elif pilihan_staff == '3': # Opsi Laporan & Statistik
                        console.print(Panel("[bold white on sea_green3] Sub-Menu: Laporan & Statistik [/bold white on sea_green3]", title="📈 Opsi Laporan 📈", border_style="sea_green3", expand=False, padding=(1,2)))
                        console.print("[cyan]1.[/cyan] 📜 Riwayat Seluruh Peminjaman")
                        console.print("[cyan]2.[/cyan] 📊 Laporan Peminjaman Aktif")
                        console.print("[cyan]3.[/cyan] 🏆 Lihat Buku Terpopuler")
                        console.print("[cyan]4.[/cyan] ⏰ Laporan Keterlambatan per Anggota")
                        console.print("[cyan]5.[/cyan] 💰 Laporan Total Akumulasi Denda (Global)") # OPSI BARU untuk total denda
                        console.print("[cyan]6.[/cyan] ⬅️  Kembali ke Menu Utama") # Nomor disesuaikan karena ada opsi baru
                        pilihan_laporan = Prompt.ask("[bold yellow]▶️  Pilih opsi laporan[/bold yellow]", choices=[str(i) for i in range(1,7)], show_choices=False) # Range pilihan disesuaikan
                        console.line(1)
                        console.print("─" * 60, style="dim sea_green3")
                        # Panggil fungsi laporan sesuai pilihan
                        if pilihan_laporan == '1': tampilkan_riwayat_peminjaman(self)
                        elif pilihan_laporan == '2': laporan_peminjaman(self)
                        elif pilihan_laporan == '3': lihat_buku_populer(self)
                        elif pilihan_laporan == '4': laporan_keterlambatan(self)
                        elif pilihan_laporan == '5': laporan_total_akumulasi_denda(self) # Panggil fungsi laporan total denda
                        elif pilihan_laporan == '6': 
                            # --- KONFIRMASI KEMBALI KE MENU UTAMA (OPSIONAL) ---
                            if Confirm.ask("[bold yellow]❓ Kembali ke Menu Utama Staff?[/bold yellow]", default=True): # Default Ya karena ini aksi umum
                                continue # Kembali ke menu utama staff
                            else:
                                # Tetap di sub-menu manajemen jika dibatalkan (perlu sedikit penyesuaian loop sub-menu)
                                # Agar tetap di sub-menu, loop sub-menu mungkin perlu dibuat terpisah
                                # Untuk kesederhanaan saat ini, jika batal, anggap saja kembali juga
                                console.print("[italic red]Membatalkan kembali ke menu utama... (tetap di menu utama staff)[/italic red]")
                                continue
                        
                    elif pilihan_staff == '4': # Opsi Logout
                        keluar(self) # Panggil fungsi logout dari modul auth
                
                else: # Jika kategori adalah Anggota
                    # Tampilkan dashboard dan menu untuk anggota
                    tampilkan_dashboard_anggota(self) # Panggil dashboard anggota
                    console.print(Panel("[bold white on dodger_blue2] Menu Utama (Anggota) [/bold white on dodger_blue2]", border_style="dodger_blue2", expand=False, padding=(1,2)))
                    console.print("[cyan]1.[/cyan] 📖 Lihat Daftar Buku Tersedia")
                    console.print("[cyan]2.[/cyan] 🔎 Cari Judul Buku")
                    console.print("[cyan]3.[/cyan] 🛒 Pinjam Buku")
                    console.print("[cyan]4.[/cyan] ↩️  Kembalikan Buku")
                    console.print("[cyan]5.[/cyan] 📘 Daftar Buku yang Saya Pinjam")
                    console.print("[cyan]6.[/cyan] 🚪 Logout Akun")
                    pilihan_anggota = Prompt.ask("[bold yellow]▶️  Pilih menu anggota[/bold yellow]", choices=[str(i) for i in range(1,7)], show_choices=False)
                    console.line(1)
                    console.print("─" * 60, style="dim dodger_blue2")
                    # Proses pilihan menu anggota
                    if pilihan_anggota == '1': lihat_buku(self)
                    elif pilihan_anggota == '2': cari_buku(self)
                    elif pilihan_anggota == '3': pinjam_buku(self)
                    elif pilihan_anggota == '4': kembalikan_buku(self)
                    elif pilihan_anggota == '5': daftar_buku_dipinjam(self)
                    elif pilihan_anggota == '6': keluar(self) # Panggil fungsi logout

# Blok utama yang akan dieksekusi saat skrip Python dijalankan secara langsung
if __name__ == "__main__":
    aplikasi = Bukoo() # Buat instance dari kelas Bukoo
    aplikasi.tampilkan_header() # Tampilkan header aplikasi
    aplikasi.menu() # Jalankan menu utama aplikasi untuk memulai interaksi