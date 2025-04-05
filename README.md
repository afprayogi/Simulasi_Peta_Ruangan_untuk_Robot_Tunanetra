# Simulasi Peta Ruangan untuk Robot Tunanetra

Simulasi ini dirancang untuk membangun peta ruangan acak sebagai alat bantu eksperimen sistem navigasi robot tunanetra. Ruangan-ruangan dalam simulasi saling terhubung melalui pintu dan dilengkapi halangan, dinding kuat, serta titik referensi (ESP).

## Fitur

- Ruangan besar saling berhimpitan secara acak
- Pintu antar ruangan (warna hijau) dan pintu keluar (warna merah)
- Titik awal robot dijamin tidak berada di halangan
- Halangan dan dinding kuat acak untuk tantangan navigasi
- Grid visual (10x10 atau lebih) untuk setiap ruangan
- Titik referensi sinyal (ESP) diletakkan dekat pintu

## Teknologi

- Python 3.x
- Matplotlib
- Numpy
## Instalasi & Menjalankan

1. Install dependensi:

```bash
pip install matplotlib
pip install numpy
```

## Acknowledgment

Proyek ini dikembangkan secara mandiri oleh afprayogi, dengan bantuan ChatGPT dari OpenAI sebagai asisten ide dan pemrograman selama proses pembuatan simulasi.

Terima kasih juga kepada komunitas open-source dan dokumentasi Matplotlib yang sangat membantu dalam visualisasi peta.
