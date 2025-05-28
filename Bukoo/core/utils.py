# File: Bukoo/core/utils.py

# Impor modul yang diperlukan
import json # Untuk serialisasi dan deserialisasi objek Python ke/dari format JSON
from collections import deque # Untuk struktur data deque (digunakan untuk antrian)

# Daftar nama file untuk menyimpan data (konstanta)
FILE_BUKU = 'data/buku.json'
FILE_STAFF = 'data/staff.json'
FILE_ANGGOTA = 'data/anggota.json'
FILE_RIWAYAT = 'data/riwayat.json'
FILE_PEMINJAMAN = 'data/peminjaman.json'
FILE_KETERLAMBATAN = 'data/keterlambatan.json'
FILE_ANTRIAN = 'data/antrian.json'
FILE_TRANSAKSI = 'data/transaksi.json'

def simpan_semua_data(app):
    """
    Menyimpan semua data state aplikasi (buku, staff, anggota, dll.) ke dalam file JSON terpisah.

    Args:
        app (Bukoo): Instance aplikasi utama yang memegang semua data.
    """
    # Menyimpan data buku
    with open(FILE_BUKU, 'w') as f:
        json.dump(app.data_buku, f, indent=2) # indent=2 untuk pretty printing JSON
    # Menyimpan data staff
    with open(FILE_STAFF, 'w') as f:
        json.dump(app.data_staff, f, indent=2)
    # Menyimpan data anggota
    with open(FILE_ANGGOTA, 'w') as f:
        json.dump(app.data_anggota, f, indent=2)
    # Menyimpan riwayat peminjaman
    with open(FILE_RIWAYAT, 'w') as f:
        json.dump(app.riwayat_peminjaman, f, indent=2)
    # Menyimpan data peminjaman aktif anggota
    with open(FILE_PEMINJAMAN, 'w') as f:
        json.dump(app.peminjaman_anggota, f, indent=2)
    # Menyimpan data keterlambatan (denda)
    with open(FILE_KETERLAMBATAN, 'w') as f:
        json.dump(app.keterlambatan, f, indent=2)
    # Menyimpan data antrian buku (mengubah deque menjadi list sebelum simpan)
    with open(FILE_ANTRIAN, 'w') as f:
        json.dump({k: list(v) for k, v in app.antrian_buku.items()}, f, indent=2)
    # Menyimpan stack/log transaksi
    with open(FILE_TRANSAKSI, 'w') as f:
        json.dump(app.stack_transaksi, f, indent=2)

def muat_semua_data(app):
    """
    Memuat semua data state aplikasi dari file JSON.
    Jika file tidak ditemukan atau ada error, data akan diinisialisasi sebagai struktur kosong.

    Args:
        app (Bukoo): Instance aplikasi utama untuk diisi datanya.
    """
    # Memuat data buku
    try:
        with open(FILE_BUKU, 'r') as f:
            app.data_buku = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): # Tangani jika file tidak ada atau format JSON salah
        app.data_buku = {} # Inisialisasi sebagai dictionary kosong

    # Memuat data staff
    try:
        with open(FILE_STAFF, 'r') as f:
            app.data_staff = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.data_staff = {}

    # Memuat data anggota
    try:
        with open(FILE_ANGGOTA, 'r') as f:
            app.data_anggota = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.data_anggota = {}

    # Memuat riwayat peminjaman
    try:
        with open(FILE_RIWAYAT, 'r') as f:
            app.riwayat_peminjaman = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.riwayat_peminjaman = [] # Inisialisasi sebagai list kosong

    # Memuat data peminjaman aktif anggota
    try:
        with open(FILE_PEMINJAMAN, 'r') as f:
            app.peminjaman_anggota = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.peminjaman_anggota = {}

    # Memuat data keterlambatan (denda)
    try:
        with open(FILE_KETERLAMBATAN, 'r') as f:
            app.keterlambatan = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.keterlambatan = {}

    # Memuat data antrian buku (mengubah list kembali menjadi deque setelah muat)
    try:
        with open(FILE_ANTRIAN, 'r') as f:
            temp_antrian = json.load(f)
            app.antrian_buku = {k: deque(v) for k, v in temp_antrian.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        app.antrian_buku = {}

    # Memuat stack/log transaksi
    try:
        with open(FILE_TRANSAKSI, 'r') as f:
            app.stack_transaksi = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.stack_transaksi = [] # Inisialisasi sebagai list kosong

def generate_id(data_dict):
    """
    Menghasilkan ID unik berikutnya untuk dictionary data.
    ID adalah string angka, dimulai dari '1'.

    Args:
        data_dict (dict): Dictionary yang key-nya adalah ID (sebagai string angka).

    Returns:
        str: ID unik berikutnya sebagai string.
    """
    # Jika dictionary tidak kosong
    if data_dict:
        # Cari ID tertinggi (sebagai integer), tambah 1, lalu ubah kembali ke string
        return str(int(max(data_dict.keys(), key=int)) + 1)
    else:
        # Jika dictionary kosong, ID pertama adalah '1'
        return '1'