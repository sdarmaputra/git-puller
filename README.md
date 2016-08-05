# git-puller
Automatic git puller service

## Fitur
1. Bisa menentukan aksi pull atau clone berdasarkan keberadaan repositori
2. Penggantian beberapa file konfigurasi aplikasi tanpa menyentuh file langsung pada direktori sandbox
3. Konfigurasi container docker secara otomatis untuk aplikasi yang dikloning

## Batasan
1. Sementara hanya mendukung kode sumber berbasis PHP

## Langkah-langkah instalasi (disarankan menggunakan OS Linux):
1. Install Python dan pip (disarankan)
2. Install Python Tornado, docker-py dan gitPython
3. Install Docker
4. Pull image richarvey/nginx-php-fpm dari Docker Hub
5. Kloning Repositori ini pada direktori server
6. Aplikasi siap digunakan, selanjutnya adalah langkah-langkah konfigurasi


## Langkah-langkah konfigurasi:
1. Atur direktori penyimpanan aplikasi yang akan dijalankan dalam sandbox pada variabel parent_dir file puller.py
2. Atur alamat IP server pada variabel serverUrl file webservice.py
3. Jalankan aplikasi dengan menggunakan perintah python webservice

**Catatan: secara default aplikasi akan berjalan pada port 8000**

**Langkah-langkah konfigurasi aplikasi akan diperbarui pada repositori ini jika terjadi perubahan terhadap aplikasi**

**Salam**
