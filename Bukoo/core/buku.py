# File: Bukoo/core/buku.py

# Impor modul-modul yang diperlukan dari Rich dan utilitas lokal
from rich.console import Console
from rich.prompt import Prompt, Confirm # Untuk input dan konfirmasi interaktif
from rich.table import Table # Untuk menampilkan data dalam bentuk tabel
from rich.panel import Panel # Untuk membuat panel/box di UI
from rich.text import Text # Untuk teks dengan styling kaya
from .utils import generate_id, simpan_semua_data # Fungsi utilitas

# Inisialisasi console Rich
console = Console()

# --- Fungsi CRUD (Create, Read, Update, Delete) Buku ---
# Catatan: Fungsi Tambah, Edit, Hapus biasanya hanya untuk Staff

def tambah_buku(app):
    """Fungsi untuk menambahkan buku baru ke dalam sistem oleh staff."""
    # Cek apakah pengguna saat ini adalah staff
    if app.kategori_saat_ini != 'staff':
        console.print(Panel.fit("[bold red]❌ Fitur ini hanya untuk Staff![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    # Tampilkan panel judul untuk formulir tambah buku
    console.print(Panel("✨ Formulir Tambah Buku Baru ✨", style="bold chartreuse3", border_style="chartreuse3", expand=False, padding=1))
    
    # Minta input judul buku, validasi tidak boleh kosong
    judul = Prompt.ask("[bold yellow]✒️  Judul Buku[/bold yellow]")
    while not judul.strip(): # .strip() untuk menghapus spasi di awal/akhir dan cek kekosongan
        console.print(Panel.fit("[bold red]Judul buku tidak boleh kosong.[/bold red]", title="⚠️ Input Salah", border_style="red"))
        judul = Prompt.ask("[bold yellow]✒️  Judul Buku[/bold yellow]")

    # Minta input nama penulis, validasi tidak boleh kosong
    penulis = Prompt.ask("[bold yellow]✍️  Nama Penulis[/bold yellow]")
    while not penulis.strip():
        console.print(Panel.fit("[bold red]Nama penulis tidak boleh kosong.[/bold red]", title="⚠️ Input Salah", border_style="red"))
        penulis = Prompt.ask("[bold yellow]✍️  Nama Penulis[/bold yellow]")
        
    # Minta input tahun terbit, validasi format YYYY dan rentang wajar
    while True:
        tahun_str = Prompt.ask("[bold yellow]📅 Tahun Terbit (YYYY)[/bold yellow]")
        if len(tahun_str) == 4 and tahun_str.isdigit() and 1000 <= int(tahun_str) <= 9999 : # Contoh validasi rentang tahun
            tahun = int(tahun_str)
            break # Keluar loop jika valid
        else:
            console.print(Panel.fit("[bold red]Format tahun tidak valid. Masukkan 4 digit angka (mis: 2023) antara 1000-9999.[/bold red]", title="⚠️ Input Salah", border_style="red"))

    # Minta input jumlah stok awal, validasi harus angka non-negatif
    while True:
        stok_str = Prompt.ask("[bold yellow]📦 Jumlah Stok Awal[/bold yellow]")
        if stok_str.isdigit() and int(stok_str) >= 0:
            stok = int(stok_str)
            break # Keluar loop jika valid
        else:
            console.print(Panel.fit("[bold red]Jumlah stok harus angka non-negatif.[/bold red]", title="⚠️ Input Salah", border_style="red"))

    # Generate ID baru untuk buku
    id_buku_baru = generate_id(app.data_buku)
    # Tambahkan data buku baru ke dictionary data_buku
    app.data_buku[id_buku_baru] = {
        "judul": judul,
        "penulis": penulis,
        "tahun": str(tahun), # Simpan tahun sebagai string agar konsisten
        "stok": stok
    }
    # Simpan semua perubahan data ke file JSON
    simpan_semua_data(app)
    # Tampilkan pesan sukses
    console.print(Panel.fit(f"[bold green]✅ Buku '{judul}' (ID: {id_buku_baru}) berhasil ditambahkan ke perpustakaan![/bold green]", title="🎉 Sukses", border_style="green"))

def edit_buku(app):
    """Fungsi untuk mengedit informasi buku yang sudah ada oleh staff."""
    # Cek otorisasi staff
    if app.kategori_saat_ini != 'staff':
        console.print(Panel.fit("[bold red]❌ Fitur ini hanya untuk Staff![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    console.print(Panel("✏️  Formulir Edit Informasi Buku ✏️", style="bold gold1", border_style="gold1", expand=False, padding=1))
    # Cek apakah ada buku untuk diedit
    if not app.data_buku:
        console.print(Panel.fit("[italic yellow]Belum ada data buku untuk diedit.[/italic yellow]", title="ℹ️ Info", border_style="yellow"))
        return

    lihat_buku(app) # Tampilkan daftar buku agar staff mudah memilih ID
    id_edit = Prompt.ask("[bold yellow]🆔 Masukkan ID Buku yang ingin diedit[/bold yellow]")

    # Cek apakah ID buku yang dimasukkan ada di data
    if id_edit not in app.data_buku:
        console.print(Panel.fit(f"[bold red]❌ Buku dengan ID '{id_edit}' tidak ditemukan.[/bold red]", title="⚠️ Gagal", border_style="red"))
        return

    # Ambil data buku yang akan diedit
    buku = app.data_buku[id_edit]
    # Tampilkan informasi buku saat ini sebelum diedit
    console.print(Panel.fit(f"Mengedit Buku: [bold medium_purple2]{buku['judul']}[/bold medium_purple2] (ID: {id_edit})", title="ℹ️  Info Buku Saat Ini", border_style="medium_purple2"))
    console.print(f"   [dim]Judul Lama  :[/dim] {buku['judul']}")
    console.print(f"   [dim]Penulis Lama:[/dim] {buku['penulis']}")
    console.print(f"   [dim]Tahun Lama  :[/dim] {buku['tahun']}")
    console.print(f"   [dim]Stok Lama   :[/dim] {buku['stok']}")
    console.line()

    # Minta input baru, gunakan nilai lama sebagai default (tekan Enter untuk skip)
    judul_baru = Prompt.ask(f"[bold yellow]✒️  Judul Baru (Enter untuk skip)[/bold yellow]", default=buku['judul'])
    penulis_baru = Prompt.ask(f"[bold yellow]✍️  Penulis Baru (Enter untuk skip)[/bold yellow]", default=buku['penulis'])
    
    # Validasi input tahun baru
    while True:
        tahun_baru_str = Prompt.ask(f"[bold yellow]📅 Tahun Baru (YYYY, Enter untuk skip)[/bold yellow]", default=str(buku['tahun']))
        if tahun_baru_str == str(buku['tahun']) or not tahun_baru_str.strip(): 
            tahun_baru = buku['tahun'] 
            break
        if len(tahun_baru_str) == 4 and tahun_baru_str.isdigit() and 1000 <= int(tahun_baru_str) <= 9999:
            tahun_baru = int(tahun_baru_str)
            break
        else:
            console.print(Panel.fit("[bold red]Format tahun tidak valid. Masukkan 4 digit angka atau tekan Enter untuk skip.[/bold red]", title="⚠️ Input Salah", border_style="red"))

    # Validasi input stok baru
    while True:
        stok_baru_str = Prompt.ask(f"[bold yellow]📦 Stok Baru (Enter untuk skip)[/bold yellow]", default=str(buku['stok']))
        if stok_baru_str == str(buku['stok']) or not stok_baru_str.strip():
            stok_baru = buku['stok']
            break
        if stok_baru_str.isdigit() and int(stok_baru_str) >= 0:
            stok_baru = int(stok_baru_str)
            break
        else:
            console.print(Panel.fit("[bold red]Jumlah stok harus angka non-negatif atau tekan Enter untuk skip.[/bold red]", title="⚠️ Input Salah", border_style="red"))

    # Update data buku dengan nilai baru (gunakan strip untuk menghapus spasi ekstra)
    app.data_buku[id_edit] = {
        "judul": judul_baru.strip() if judul_baru.strip() else buku['judul'],
        "penulis": penulis_baru.strip() if penulis_baru.strip() else buku['penulis'],
        "tahun": str(tahun_baru),
        "stok": stok_baru
    }
    # Simpan perubahan ke file
    simpan_semua_data(app)
    # Tampilkan pesan sukses
    console.print(Panel.fit(f"[bold green]✅ Informasi buku '{app.data_buku[id_edit]['judul']}' (ID: {id_edit}) berhasil diperbarui![/bold green]", title="🎉 Sukses", border_style="green"))

def hapus_buku(app):
    """Fungsi untuk menghapus buku dari sistem oleh staff."""
    # Cek otorisasi staff
    if app.kategori_saat_ini != 'staff':
        console.print(Panel.fit("[bold red]❌ Fitur ini hanya untuk Staff![/bold red]", title="🚫 Akses Ditolak", border_style="red"))
        return

    console.print(Panel("🗑️ Hapus Buku dari Sistem Perpustakaan 🗑️", style="bold indian_red", border_style="indian_red", expand=False, padding=1))
    # Cek apakah ada buku untuk dihapus
    if not app.data_buku:
        console.print(Panel.fit("[italic yellow]Belum ada data buku untuk dihapus.[/italic yellow]", title="ℹ️ Info", border_style="yellow"))
        return

    lihat_buku(app) # Tampilkan daftar buku
    id_hapus = Prompt.ask("[bold yellow]🆔 Masukkan ID Buku yang ingin dihapus[/bold yellow]")

    # Cek apakah ID buku ada
    if id_hapus not in app.data_buku:
        console.print(Panel.fit(f"[bold red]❌ Buku dengan ID '{id_hapus}' tidak ditemukan.[/bold red]", title="⚠️ Gagal", border_style="red"))
        return

    buku = app.data_buku[id_hapus]

    # Cek apakah buku sedang dipinjam oleh anggota
    buku_dipinjam_oleh = []
    for id_anggota, detail_pinjaman in app.peminjaman_anggota.items():
        if id_hapus in detail_pinjaman: # Jika ID buku ada dalam daftar pinjaman anggota
            nama_peminjam = app.data_anggota.get(id_anggota, {}).get('nama', f"ID Anggota {id_anggota}")
            buku_dipinjam_oleh.append(nama_peminjam)
            
    if buku_dipinjam_oleh: # Jika ada yang meminjam
        console.print(Panel.fit(f"[bold orange_red1]❌ Buku '{buku['judul']}' (ID: {id_hapus}) saat ini sedang dipinjam oleh: {', '.join(buku_dipinjam_oleh)}.\nTidak dapat dihapus hingga buku dikembalikan oleh semua peminjam.[/bold orange_red1]", title="⚠️ Operasi Dibatalkan", border_style="red"))
        return
        
    # Minta konfirmasi sebelum menghapus
    konfirmasi_hapus_text = Text.assemble(
        ("❓ Anda YAKIN ingin menghapus buku '", "bold orange_red1"),
        (buku['judul'], "bold white"),
        ("' (ID: ", "bold orange_red1"),
        (id_hapus, "bold white"),
        (")? Tindakan ini ", "bold orange_red1"),
        ("TIDAK DAPAT DIURUNGKAN", "bold white on red"),
        ("!", "bold orange_red1")
    )
    if Confirm.ask(konfirmasi_hapus_text, default=False): # Default konfirmasi adalah Tidak
        # Hapus buku dari data_buku
        del app.data_buku[id_hapus]
        # Hapus buku dari antrian jika ada
        if id_hapus in app.antrian_buku:
            del app.antrian_buku[id_hapus]
        # Simpan perubahan
        simpan_semua_data(app)
        console.print(Panel.fit(f"[bold green]✅ Buku '{buku['judul']}' (ID: {id_hapus}) berhasil dihapus dari sistem.[/bold green]", title="🎉 Sukses", border_style="green"))
    else:
        console.print(Panel.fit("[italic yellow]ℹ️ Penghapusan buku dibatalkan oleh pengguna.[/italic yellow]", title="Operasi Dibatalkan", border_style="yellow"))


# --- Fungsi Tampilan dan Pencarian Buku ---
def _get_sorted_books(app, pilihan_sort, urutan):
    """Fungsi internal untuk mendapatkan daftar buku yang sudah diurutkan."""
    # Tentukan arah pengurutan (ascending atau descending)
    reverse = True if urutan.lower() == 'd' else False
    # Konversi item dictionary buku ke list untuk diurutkan
    items_to_sort = list(app.data_buku.items())

    # Logika pengurutan berdasarkan pilihan kriteria
    if pilihan_sort == '1': # Urutkan berdasarkan ID (integer)
        return sorted(items_to_sort, key=lambda item: int(item[0]), reverse=reverse)
    elif pilihan_sort == '2': # Urutkan berdasarkan Judul (string, case-insensitive)
        return sorted(items_to_sort, key=lambda item: item[1]['judul'].lower(), reverse=reverse)
    elif pilihan_sort == '3': # Urutkan berdasarkan Penulis (string, case-insensitive)
        return sorted(items_to_sort, key=lambda item: item[1]['penulis'].lower(), reverse=reverse)
    elif pilihan_sort == '4' and app.kategori_saat_ini == 'staff': # Urutkan berdasarkan Tahun (integer, hanya staff)
        return sorted(items_to_sort, key=lambda item: int(item[1]['tahun']), reverse=reverse)
    elif pilihan_sort == '5' and app.kategori_saat_ini == 'staff': # Urutkan berdasarkan Stok (integer, hanya staff)
        return sorted(items_to_sort, key=lambda item: item[1]['stok'], reverse=reverse)
    return [] # Kembalikan list kosong jika kriteria tidak cocok

def lihat_buku_staff(app):
    """Menampilkan daftar buku untuk pengguna staff dengan opsi pengurutan."""
    # Cek apakah ada data buku
    if not app.data_buku:
        console.print(Panel.fit("[italic yellow]Belum ada data buku di perpustakaan.[/italic yellow]", title="ℹ️ Info Kosong", border_style="yellow"))
        return

    # Tampilkan panel opsi pengurutan
    console.print(Panel("[bold white on steel_blue]🔍 Opsi Tampilan Daftar Buku (Staff) 🔍[/bold white on steel_blue]", border_style="steel_blue", expand=False, padding=1))
    console.print("[cyan]1.[/cyan] Urutkan berdasarkan ID Buku")
    console.print("[cyan]2.[/cyan] Urutkan berdasarkan Judul Buku")
    console.print("[cyan]3.[/cyan] Urutkan berdasarkan Nama Penulis")
    console.print("[cyan]4.[/cyan] Urutkan berdasarkan Tahun Terbit")
    console.print("[cyan]5.[/cyan] Urutkan berdasarkan Jumlah Stok")
    pilihan_sort = Prompt.ask("[bold yellow]▶️  Pilih kriteria pengurutan[/bold yellow]", choices=["1", "2", "3", "4", "5"], show_choices=False)

    # Minta pilihan arah pengurutan
    console.print(Text.assemble(("Pilih urutan tampilan: (", "default"),("a", "bold green"),("sc / ", "default"),("d", "bold red"),("esc)", "default")))
    urutan = Prompt.ask("[bold yellow]▶️  Pilih urutan (a/d)[/bold yellow]", choices=["a", "d"], default="a", show_choices=False).lower()

    # Dapatkan daftar buku yang sudah diurutkan
    daftar_buku_sorted = _get_sorted_books(app, pilihan_sort, urutan)

    # Buat tabel untuk menampilkan daftar buku
    table = Table(title="📚 Daftar Lengkap Buku Perpustakaan (Staff View) 📚", show_header=True, header_style="bold deep_pink2", border_style="dim steel_blue", min_width=80, show_lines=True)
    table.add_column("ID 🔢", style="dim cyan", no_wrap=True, justify="center")
    table.add_column("Judul Buku 📜", style="light_goldenrod1", min_width=30)
    table.add_column("Penulis ✍️", style="pale_green1", min_width=20)
    table.add_column("Tahun 📅", style="light_sky_blue1", justify="center")
    table.add_column("Stok 📦", style="indian_red1", justify="right")

    # Tambahkan setiap buku ke tabel
    for id_buku, buku in daftar_buku_sorted:
        table.add_row(id_buku, buku['judul'], buku['penulis'], str(buku['tahun']), str(buku['stok']))
    console.print(table) # Tampilkan tabel

def lihat_buku_anggota(app):
    """Menampilkan daftar buku untuk pengguna anggota dengan opsi pengurutan."""
    if not app.data_buku:
        console.print(Panel.fit("[italic yellow]Maaf, belum ada buku yang tersedia di perpustakaan saat ini.[/italic yellow]", title="ℹ️ Info Kosong", border_style="yellow"))
        return

    console.print(Panel("[bold white on steel_blue]🔍 Opsi Tampilan Daftar Buku (Anggota) 🔍[/bold white on steel_blue]", border_style="steel_blue", expand=False, padding=1))
    console.print("[cyan]1.[/cyan] Urutkan berdasarkan Judul Buku")
    console.print("[cyan]2.[/cyan] Urutkan berdasarkan Nama Penulis")
    pilihan_sort_anggota = Prompt.ask("[bold yellow]▶️  Pilih kriteria pengurutan[/bold yellow]", choices=["1", "2"], show_choices=False)
    
    # Mapping pilihan anggota ke kriteria internal yang digunakan _get_sorted_books
    map_pilihan_anggota_ke_internal = {'1': '2', '2': '3'} 
    pilihan_sort_internal = map_pilihan_anggota_ke_internal[pilihan_sort_anggota]

    console.print(Text.assemble(("Pilih urutan tampilan: (", "default"),("a", "bold green"),("sc / ", "default"),("d", "bold red"),("esc)", "default")))
    urutan = Prompt.ask("[bold yellow]▶️  Pilih urutan (a/d)[/bold yellow]", choices=["a", "d"], default="a", show_choices=False).lower()

    daftar_buku_sorted = _get_sorted_books(app, pilihan_sort_internal, urutan)
    
    table = Table(title="📖 Daftar Buku Tersedia di Perpustakaan (Anggota View) 📖", show_header=True, header_style="bold deep_pink2", border_style="dim steel_blue", min_width=70, show_lines=True)
    table.add_column("ID 🔢", style="dim cyan", no_wrap=True, justify="center") 
    table.add_column("Judul Buku 📜", style="light_goldenrod1", min_width=30) 
    table.add_column("Penulis ✍️", style="pale_green1", min_width=20) 
    table.add_column("Status Stok ✅", justify="center") # Kolom status stok untuk anggota

    ada_buku_tampil = False # Flag untuk cek apakah ada buku yang ditampilkan
    for id_buku, buku in daftar_buku_sorted:
        # Tentukan teks status stok berdasarkan jumlah stok
        if buku['stok'] > 0:
            status_stok = "[bold green3]Tersedia[/bold green3]"
            ada_buku_tampil = True
        else:
            status_stok = "[bold gold3]Habis (Antri)[/bold gold3]"
            ada_buku_tampil = True # Tetap tampilkan info buku habis agar bisa antri
            
        table.add_row(id_buku, buku['judul'], buku['penulis'], status_stok)
    
    # Handle kasus jika ada buku di data tapi semua stoknya 0 atau tidak ada buku sama sekali
    if not ada_buku_tampil and app.data_buku : 
        console.print(Panel.fit("[italic yellow]Semua buku yang cocok dengan kriteria sedang habis stoknya. Anda bisa mencoba meminjam untuk masuk antrian jika fitur antri tersedia.[/italic yellow]", title="ℹ️ Info Stok", border_style="yellow"))
    elif ada_buku_tampil:
        console.print(table)
    # Jika tidak ada buku di data_buku sama sekali, sudah ditangani di awal fungsi.

def lihat_buku(app): 
    """Fungsi 'router' untuk memanggil tampilan buku berdasarkan kategori pengguna."""
    if app.kategori_saat_ini == 'staff':
        lihat_buku_staff(app)
    elif app.kategori_saat_ini == 'anggota':
        lihat_buku_anggota(app)
    else: # Jika tidak ada pengguna login atau kategori tidak diketahui
        console.print(Panel.fit("[bold red]❌ Anda perlu login untuk melihat daftar buku.[/bold red]", title="🚫 Akses Ditolak", border_style="red"))


# --- Fungsi Pencarian Buku ---
def _perform_search(app, pilihan_cari, kata_kunci):
    """Fungsi internal untuk melakukan pencarian buku berdasarkan kriteria."""
    hasil = [] # List untuk menyimpan hasil pencarian
    kata_kunci_lower = kata_kunci.lower() # Ubah kata kunci ke huruf kecil untuk pencarian case-insensitive
    
    # Iterasi melalui semua buku dalam data
    for id_buku, buku in app.data_buku.items():
        # Logika pencarian berdasarkan pilihan kriteria
        if pilihan_cari == '1': # Cari berdasarkan ID (eksak, case-sensitive untuk ID)
            if id_buku == kata_kunci: 
                hasil.append((id_buku, buku))
        elif pilihan_cari == '2': # Cari berdasarkan Judul (parsial, case-insensitive)
            if kata_kunci_lower in buku['judul'].lower():
                hasil.append((id_buku, buku))
        elif pilihan_cari == '3': # Cari berdasarkan Penulis (parsial, case-insensitive)
            if kata_kunci_lower in buku['penulis'].lower():
                hasil.append((id_buku, buku))
        elif pilihan_cari == '4' and app.kategori_saat_ini == 'staff': # Cari berdasarkan Tahun (eksak, hanya staff)
            if kata_kunci_lower == str(buku['tahun']).lower(): 
                hasil.append((id_buku, buku))
    return hasil # Kembalikan list hasil pencarian

def cari_buku_staff(app):
    """Fungsi untuk pencarian buku oleh staff."""
    console.print(Panel("[bold white on steel_blue]🔎 Opsi Pencarian Buku (Staff) 🔎[/bold white on steel_blue]", border_style="steel_blue", expand=False, padding=1))
    if not app.data_buku: # Cek apakah ada data buku
        console.print(Panel.fit("[italic yellow]Belum ada data buku untuk dicari.[/italic yellow]", title="ℹ️ Info Kosong", border_style="yellow"))
        return

    # Tampilkan opsi kriteria pencarian untuk staff
    console.print("[cyan]1.[/cyan] Cari berdasarkan ID Buku")
    console.print("[cyan]2.[/cyan] Cari berdasarkan Judul Buku")
    console.print("[cyan]3.[/cyan] Cari berdasarkan Nama Penulis")
    console.print("[cyan]4.[/cyan] Cari berdasarkan Tahun Terbit")
    pilihan_cari = Prompt.ask("[bold yellow]▶️  Pilih kriteria pencarian[/bold yellow]", choices=["1", "2", "3", "4"], show_choices=False)
    
    # Mapping pilihan ke teks prompt yang sesuai
    prompt_text_map = {
        '1': "🆔 Masukkan ID Buku yang dicari",
        '2': "📜 Masukkan kata kunci judul buku",
        '3': "✍️  Masukkan kata kunci nama penulis",
        '4': "📅 Masukkan tahun terbit (YYYY)",
    }
    # Minta input kata kunci pencarian
    kata_kunci = Prompt.ask(f"[bold yellow]⌨️  {prompt_text_map[pilihan_cari]}[/bold yellow]")
    # Validasi kata kunci tidak boleh kosong
    if not kata_kunci.strip():
        console.print(Panel.fit("[bold red]Kata kunci pencarian tidak boleh kosong.[/bold red]", title="⚠️ Input Salah", border_style="red"))
        return

    # Lakukan pencarian menggunakan fungsi internal
    hasil_pencarian = _perform_search(app, pilihan_cari, kata_kunci)

    # Jika tidak ada hasil pencarian
    if not hasil_pencarian:
        console.print(Panel.fit(f"[italic yellow]Tidak ada buku yang cocok dengan kriteria pencarian untuk '[bold]{kata_kunci}[/bold]'.[/italic yellow]", title="🚫 Hasil Tidak Ditemukan", border_style="yellow"))
        return

    # Buat tabel untuk menampilkan hasil pencarian
    table = Table(title=f"🔎 Hasil Pencarian Buku untuk '[italic]{kata_kunci}[/italic]' (Staff View) 🔎", show_header=True, header_style="bold deep_pink2", border_style="dim steel_blue", min_width=80, show_lines=True)
    table.add_column("ID 🔢", style="dim cyan", no_wrap=True, justify="center")
    table.add_column("Judul Buku 📜", style="light_goldenrod1", min_width=30)
    table.add_column("Penulis ✍️", style="pale_green1", min_width=20)
    table.add_column("Tahun 📅", style="light_sky_blue1", justify="center")
    table.add_column("Stok 📦", style="indian_red1", justify="right")

    # Tambahkan hasil pencarian ke tabel
    for id_buku, buku in hasil_pencarian:
        table.add_row(id_buku, buku['judul'], buku['penulis'], str(buku['tahun']), str(buku['stok']))
    console.print(table) # Tampilkan tabel

def cari_buku_anggota(app):
    """Fungsi untuk pencarian buku oleh anggota."""
    console.print(Panel("[bold white on steel_blue]🔎 Opsi Pencarian Buku (Anggota) 🔎[/bold white on steel_blue]", border_style="steel_blue", expand=False, padding=1))
    if not app.data_buku:
        console.print(Panel.fit("[italic yellow]Maaf, belum ada buku yang tersedia untuk dicari.[/italic yellow]", title="ℹ️ Info Kosong", border_style="yellow"))
        return

    # Opsi pencarian untuk anggota lebih terbatas
    console.print("[cyan]1.[/cyan] Cari berdasarkan Judul Buku")
    console.print("[cyan]2.[/cyan] Cari berdasarkan Nama Penulis")
    pilihan_cari_anggota = Prompt.ask("[bold yellow]▶️  Pilih kriteria pencarian[/bold yellow]", choices=["1", "2"], show_choices=False)

    # Mapping pilihan anggota ke kriteria internal
    map_pilihan_anggota_ke_internal = {'1': '2', '2': '3'}
    pilihan_cari_internal = map_pilihan_anggota_ke_internal[pilihan_cari_anggota]

    prompt_text_map_anggota = {
        '1': "📜 Masukkan kata kunci judul buku",
        '2': "✍️  Masukkan kata kunci nama penulis",
    }
    kata_kunci = Prompt.ask(f"[bold yellow]⌨️  {prompt_text_map_anggota[pilihan_cari_anggota]}[/bold yellow]")
    if not kata_kunci.strip():
        console.print(Panel.fit("[bold red]Kata kunci pencarian tidak boleh kosong.[/bold red]", title="⚠️ Input Salah", border_style="red"))
        return
        
    hasil_pencarian = _perform_search(app, pilihan_cari_internal, kata_kunci)

    if not hasil_pencarian:
        console.print(Panel.fit(f"[italic yellow]Tidak ada buku yang cocok dengan kriteria pencarian untuk '[bold]{kata_kunci}[/bold]'.[/italic yellow]", title="🚫 Hasil Tidak Ditemukan", border_style="yellow"))
        return

    table = Table(title=f"🔎 Hasil Pencarian Buku untuk '[italic]{kata_kunci}[/italic]' (Anggota View) 🔎", show_header=True, header_style="bold deep_pink2", border_style="dim steel_blue", min_width=70, show_lines=True)
    table.add_column("ID 🔢", style="dim cyan", no_wrap=True, justify="center") # ID ditampilkan agar anggota bisa pinjam
    table.add_column("Judul Buku 📜", style="light_goldenrod1", min_width=30)
    table.add_column("Penulis ✍️", style="pale_green1", min_width=20)
    table.add_column("Status Stok ✅", justify="center") # Status stok penting untuk anggota

    for id_buku, buku in hasil_pencarian:
        status_stok = "[bold green3]Tersedia[/bold green3]" if buku['stok'] > 0 else "[bold gold3]Habis (Antri)[/bold gold3]"
        table.add_row(id_buku, buku['judul'], buku['penulis'], status_stok)
    console.print(table)

def cari_buku(app): 
    """Fungsi 'router' untuk memanggil fungsi pencarian buku berdasarkan kategori pengguna."""
    if app.kategori_saat_ini == 'staff':
        cari_buku_staff(app)
    elif app.kategori_saat_ini == 'anggota':
        cari_buku_anggota(app)
    else: # Jika tidak login
        console.print(Panel.fit("[bold red]❌ Anda perlu login untuk menggunakan fitur pencarian.[/bold red]", title="🚫 Akses Ditolak", border_style="red"))