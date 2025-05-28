# File: Bukoo/core/auth.py

# Impor modul-modul yang diperlukan dari Rich dan utilitas lokal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm # Untuk input pengguna yang interaktif
from pwinput import pwinput # Untuk maskking password jadi tanda *
from .utils import generate_id, simpan_semua_data # Fungsi utilitas dari modul lokal

# Inisialisasi console Rich untuk output yang lebih baik
console = Console()

def username_sudah_ada(app, username, kategori):
    """
    Memeriksa apakah username yang diberikan sudah ada dalam data staff atau anggota.

    Args:
        app (Bukoo): Instance aplikasi utama.
        username (str): Username yang akan diperiksa.
        kategori (str): Kategori pengguna ('staff' atau 'anggota').

    Returns:
        bool: True jika username sudah ada, False jika belum.
    """
    # Tentukan dictionary data yang akan diperiksa berdasarkan kategori
    target_data = app.data_staff if kategori == 'staff' else app.data_anggota
    # Iterasi melalui nilai-nilai dalam dictionary data (info pengguna)
    for user_info in target_data.values():
        # Jika username cocok, kembalikan True
        if user_info['username'] == username:
            return True
    # Jika loop selesai tanpa menemukan username yang cocok, kembalikan False
    return False

def daftar(app):
    """Fungsi untuk menangani proses pendaftaran pengguna baru (staff atau anggota)."""
    # Tampilkan panel header untuk formulir pendaftaran
    console.print(Panel("📝 Formulir Pendaftaran Akun Baru 📝", style="bold steel_blue", border_style="steel_blue", expand=False, padding=1))
    console.line() # Tambahkan baris kosong untuk spasi

    # Persiapan teks prompt untuk pemilihan kategori dengan styling Rich
    kategori_prompt_text = Text.assemble(
        ("Daftar sebagai: ", "bold default"),
        ("S", "bold green"), ("taff (", "default"), ("1", "bold green"), (") / ", "bold default"),
        ("A", "bold dodger_blue2"), ("nggota (", "default"), ("2", "bold dodger_blue2"), (")", "default") 
    )
    # Minta input kategori dari pengguna dengan pilihan yang sudah ditentukan
    kategori_choice = Prompt.ask(kategori_prompt_text, choices=["1", "2"], show_choices=False)
    # Tentukan string kategori berdasarkan pilihan pengguna
    kategori = "staff" if kategori_choice == '1' else "anggota"
    console.print(f"Anda mendaftar sebagai: [bold {'green' if kategori == 'staff' else 'dodger_blue2'}]{kategori.capitalize()}[/bold {'green' if kategori == 'staff' else 'dodger_blue2'}]")
    console.line()

    # Minta input nama lengkap pengguna
    nama = Prompt.ask("[bold yellow]👤 Masukkan Nama Lengkap Anda[/bold yellow]")
    
    # Loop untuk meminta input username hingga valid (tidak kosong dan belum ada)
    while True:
        username = Prompt.ask("[bold yellow]🆔 Masukkan Username Pilihan[/bold yellow]")
        # Validasi username tidak boleh kosong atau hanya spasi
        if not username.strip(): 
            console.print(Panel.fit("[bold red]❌ Username tidak boleh kosong atau hanya spasi.[/bold red]", title="⚠️ Peringatan", border_style="red"))
            continue # Ulangi permintaan input username
        # Cek apakah username sudah digunakan
        if username_sudah_ada(app, username, kategori):
            console.print(Panel.fit(f"[bold red]❌ Username '{username}' sudah digunakan sebagai {kategori}. Silakan pilih username lain.[/bold red]", title="⚠️ Peringatan", border_style="red"))
        else:
            break # Username valid, keluar dari loop

    # Loop untuk meminta input kata sandi hingga valid (minimal 8 karakter dan terkonfirmasi)
    while True:
        kata_sandi = Prompt.ask("[bold yellow]🔒 Masukkan Kata Sandi (minimal 8 karakter)[/bold yellow]") 
        # Validasi panjang kata sandi
        if len(kata_sandi) < 8:
            console.print(Panel.fit("[bold red]❌ Kata sandi minimal harus 8 karakter. Ulangi lagi.[/bold red]", title="⚠️ Peringatan", border_style="red"))
        else:
            # Minta konfirmasi kata sandi
            kata_sandi_konfirmasi = Prompt.ask("[bold yellow]🔑 Konfirmasi Kata Sandi Anda[/bold yellow]")
            # Cek apakah kata sandi dan konfirmasinya cocok
            if kata_sandi == kata_sandi_konfirmasi:
                break # Kata sandi cocok, keluar dari loop
            else:
                console.print(Panel.fit("[bold red]❌ Kata sandi dan konfirmasi kata sandi tidak cocok. Ulangi lagi.[/bold red]", title="⚠️ Peringatan", border_style="red"))

    # Siapkan dictionary data untuk pengguna baru
    data_baru = {
        'nama': nama,
        'username': username,
        'kata_sandi': kata_sandi, # Catatan: Idealnya kata sandi di-hash sebelum disimpan
        'kategori': kategori
    }

    # Simpan data pengguna baru ke dictionary yang sesuai (staff atau anggota) dan generate ID
    if kategori == 'staff':
        id_baru = generate_id(app.data_staff) # Generate ID unik untuk staff
        app.data_staff[id_baru] = data_baru # Tambahkan ke data staff
    else:
        id_baru = generate_id(app.data_anggota) # Generate ID unik untuk anggota
        app.data_anggota[id_baru] = data_baru # Tambahkan ke data anggota

    # Simpan semua perubahan data ke file JSON
    simpan_semua_data(app)
    # Tampilkan pesan sukses pendaftaran
    console.print(Panel.fit(f"[bold green]🎉 Pendaftaran Berhasil! 🎉\nSelamat bergabung, {nama}!\nAnda terdaftar sebagai {kategori.capitalize()} dengan ID: {id_baru}[/bold green]", title="✅ Sukses", border_style="green"))

def masuk(app):
    """Fungsi untuk menangani proses login pengguna."""
    # Tampilkan panel header untuk formulir login
    console.print(Panel("🔑 Formulir Login Akun 🔑", style="bold steel_blue", border_style="steel_blue", expand=False, padding=1))
    console.line()
    # Minta input username dan kata sandi
    username = Prompt.ask("[bold yellow]🆔 Masukkan Username Anda[/bold yellow]")
    console.print("[bold yellow]🔒 Masukkan Kata Sandi Anda[/bold yellow]:", end="") # password=True untuk masking
    kata_sandi = pwinput(" ")

    # Cek kredensial di data staff
    for id_staff, data in app.data_staff.items():
        if data['username'] == username and data['kata_sandi'] == kata_sandi:
            # Jika cocok, set pengguna saat ini dan kategori, lalu tampilkan pesan sukses
            app.pengguna_saat_ini = id_staff
            app.kategori_saat_ini = 'staff'
            console.print(Panel.fit(f"[bold green]✅ Login berhasil! Selamat datang kembali, {data['nama']} (Staff).[/bold green]", title="🎉 Sukses Login", border_style="green"))
            return # Keluar dari fungsi setelah login berhasil

    # Jika tidak ditemukan di staff, cek di data anggota
    for id_anggota, data in app.data_anggota.items():
        if data['username'] == username and data['kata_sandi'] == kata_sandi:
            # Jika cocok, set pengguna saat ini dan kategori, lalu tampilkan pesan sukses
            app.pengguna_saat_ini = id_anggota
            app.kategori_saat_ini = 'anggota'
            console.print(Panel.fit(f"[bold green]✅ Login berhasil! Selamat datang kembali, {data['nama']} (Anggota).[/bold green]", title="🎉 Sukses Login", border_style="green"))
            return # Keluar dari fungsi setelah login berhasil

    # Jika tidak ditemukan di kedua data, tampilkan pesan gagal login
    console.print(Panel.fit("[bold red]❌ Username atau kata sandi salah. Silakan periksa kembali data Anda.[/bold red]", title="🚫 Gagal Login", border_style="red"))

def keluar(app):
    """Fungsi untuk menangani proses logout pengguna."""

    # --- KONFIRMASI LOGOUT ---
    nama_pengguna_display = ""
    if app.pengguna_saat_ini and app.kategori_saat_ini:
        data_pengguna = app.data_staff if app.kategori_saat_ini == 'staff' else app.data_anggota
        nama_pengguna_display = data_pengguna.get(app.pengguna_saat_ini, {}).get('nama', app.pengguna_saat_ini)
    
    prompt_logout = Text.assemble(
        ("❓ Anda yakin ingin logout dari akun '", "bold orange_red1"),
        (str(nama_pengguna_display), "bold white"),
        ("'?", "bold orange_red1")
    )

    if Confirm.ask(prompt_logout, default=False):
        simpan_semua_data(app) # Simpan data sebelum benar-benar logout
        
        app.pengguna_saat_ini = None # Reset pengguna saat ini
        app.kategori_saat_ini = None # Reset kategori saat ini
        
        console.print(Panel.fit(f"👋 Anda ({nama_pengguna_display}) telah berhasil logout. Sesi diakhiri.", title="🚪 Logout Berhasil", style="bold yellow", border_style="yellow"))
        # Setelah logout, pengguna akan kembali ke menu awal secara otomatis karena loop di main.py
    else:
        console.print(Panel.fit("[italic yellow]ℹ️  Logout dibatalkan.[/italic yellow]", title="Operasi Dibatalkan", border_style="yellow"))
        # Jika logout dibatalkan, pengguna tetap berada di menu saat ini (tidak ada perubahan state)