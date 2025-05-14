from PIL import Image
import hashlib
import getpass
import os

# Konversi teks menjadi biner
def str_to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

# Konversi biner menjadi teks
def bin_to_str(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)

# Menyisipkan pesan dan stego key ke gambar
def sisipkan_pesan(gambar_path, pesan, key):
    try:
        img = Image.open(gambar_path)
        encoded = img.copy()
        width, height = img.size
        pixels = encoded.load()

        # Buat data yang akan disisipkan
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        data = key_hash + "|" + pesan + "|EOF"
        data_bin = str_to_bin(data)

        max_bits = width * height * 3
        if len(data_bin) > max_bits:
            print("Gambar terlalu kecil untuk menyisipkan pesan.")
            return

        idx = 0
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                if idx < len(data_bin): r = (r & ~1) | int(data_bin[idx]); idx += 1
                if idx < len(data_bin): g = (g & ~1) | int(data_bin[idx]); idx += 1
                if idx < len(data_bin): b = (b & ~1) | int(data_bin[idx]); idx += 1
                pixels[x, y] = (r, g, b)
                if idx >= len(data_bin): break
            if idx >= len(data_bin): break

        simpan_path = input("Masukkan nama file untuk gambar output (misal: hasil.png): ")
        encoded.save(simpan_path)
        print(f"Gambar berhasil disimpan sebagai: {simpan_path}")
    except Exception as e:
        print(f"[ERROR] {e}")

# Mengekstrak pesan dari gambar
def ekstrak_pesan(gambar_path, key_input):
    try:
        img = Image.open(gambar_path)
        width, height = img.size
        pixels = img.load()

        data_bin = ""
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                data_bin += str(r & 1)
                data_bin += str(g & 1)
                data_bin += str(b & 1)

        data_str = bin_to_str(data_bin)

        if "|EOF" not in data_str:
            print("Tidak ditemukan pesan tersembunyi yang valid.")
            return

        raw_msg = data_str.split("|EOF")[0]
        hash_stored, pesan = raw_msg.split("|", 1)
        key_hash = hashlib.sha256(key_input.encode()).hexdigest()[:16]

        if key_hash == hash_stored:
            print(f"\nStego Key cocok!")
            print(f"Pesan tersembunyi: {pesan}")
        else:
            print("Stego Key salah!")
    except Exception as e:
        print(f"[ERROR] {e}")

# Menu utama
def main():
    while True:
        print("\n====== STEGANOGRAFI ======")
        print("1. Pengirim (Sisipkan pesan)")
        print("2. Penerima (Ambil pesan)")
        print("3. Keluar")
        pilihan = input("Pilih menu (1/2/3): ")

        if pilihan == "1":
            print("\nMODE PENGIRIM")
            path = input("Masukkan path ke file gambar (.png): ")
            if not os.path.exists(path):
                print("[❌] File tidak ditemukan!")
                continue
            pesan = input("Masukkan pesan tersembunyi: ")
            key = getpass.getpass("Masukkan Stego Key (rahasia): ")
            sisipkan_pesan(path, pesan, key)

        elif pilihan == "2":
            print("\nMODE PENERIMA")
            path = input("Masukkan path ke file gambar stego (.png): ")
            if not os.path.exists(path):
                print("File tidak ditemukan!")
                continue
            key = getpass.getpass("Masukkan Stego Key untuk membuka pesan: ")
            ekstrak_pesan(path, key)

        elif pilihan == "3":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid.")

# Eksekusi utama
if __name__ == "__main__":
    main()
