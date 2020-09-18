# Cara install

Versi **python** yang digunakan `3.8`
Versi **Django** yang digunakan `2.2.16 (LTS)` Long time support until 2022

## Buat environment python

Setelah selesai install python atau jika sudah memilikinya.<br>
buat sebuah folder untuk environment contoh nama folder : **env**

Setelah buat folder **env** masuk ke folder tersebut dengan `cd env`<br>
Didalam folder tersebut jalankan command 
`virtualenv .`<br>
yang berarti kita menginstall environment didalam directory tersebut.

Kemudian dari dalam folder tersebut run lagi `Scripts\activate`.<br>
Kemudian masuk ke folder parent, atau keluar satu folder dengan `cd ..`<br>
Lalu dari situ clone repository ini dengan `git clone https://github.com/play-verse/ucp`<br>
Sehingga bentuk folder saat ini menjadi
```
--- folder kita saat ini
  -- env
  -- ucp
```

## Install library

Pastikan bahwa di command prompt sudah ada tulisan **(env)** sebagai prefix
`(env) D:/.....` <br>
Masuk ke folder `ucp` yang merupakan directory hasil clone, <br>
Kemudian jalankan `pip install -r requirements.txt`<br>
Tunggu hingga selesai menginstall

Kemudian, karena menggunakan windows dan harus memiliki mysqlclient nya sendiri untuk windows
Source information [https://stackoverflow.com/questions/51146117/installing-mysqlclient-in-python-3-6-in-windows](https://stackoverflow.com/questions/51146117/installing-mysqlclient-in-python-3-6-in-windows)

Install terlebih dahulu di
[https://www.lfd.uci.edu/~gohlke/pythonlibs/](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
Cari file di web tersebut dengan nama `mysqlclient‑1.4.6‑cp38‑cp38‑win32.whl`, download dan simpan.

Kemudian jalankan 
`pip install (path file tadi)`
contoh : `pip install C:\Downloads\mysqlclient‑1.4.6‑cp38‑cp38‑win32.whl`

## Setting up database

## Run server
