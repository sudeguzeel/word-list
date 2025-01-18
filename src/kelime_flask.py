from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__, static_folder="static", static_url_path="/static")
#flask'in static dosyaları her zaman güncel tutması için

# veritabanı bağlantısı
app.config['TEMPLATES_AUTO_RELOAD'] = True #flask'ın template'leri her zaman güncel tutması için

def get_db_connection():   #veritabanına bağlanmak için kullanılan fonksiyon.
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-JHUH7QO;'
        'DATABASE=kelime_proje;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()   #cursor=işlrmci
    return conn, cursor


def kelime_cek():
    conn, cursor = get_db_connection()
    try:
        cursor.execute("SELECT * FROM kelime_kutu")
        kelimeler = cursor.fetchall()
        print(f"kelimeler: {kelimeler}")  # çıktıyı kontrol et
        return kelimeler
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return []                         #hata alırsa boş liste döner
    finally:
        conn.close()




@app.route('/')
def ana_sayfa():
    return render_template('anasayfa.html')


@app.route('/kelimeler')  
# veritabanındaki kelimeleri alır ve kelime_kutusu.html şablonuna gönderir. 
def kelimeler():
    kelimeler = kelime_cek()
    return render_template('kelime_kutusu.html', kelimeler=kelimeler) 



# yeni kelime girişi rotası
@app.route('/yeni-kelime')    
def yeni_kelime():
    return render_template('yeni_kelime_girisi.html')

# kelime ekleme işlemi
@app.route('/kelime-kutusu')
def girilen_kelimeler():
    kelimeler = kelime_cek()  # Girilen filmleri veritabanından çekiyoruz
    return render_template('kelime_kutusu.html', kelimeler=kelimeler)


@app.route('/sil_kelime/<int:id>', methods=['GET','POST'])   #eritabanından id'si belirtilen kelimeyi siler ve sonra kelimeler sayfasına yönlendirir.
def sil_kelime(id):
    conn, cursor = get_db_connection()
    cursor.execute("DELETE FROM kelime_kutu WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('girilen_kelimeler'))  # ssilme işleminden sonra girilen_filmler sayfasına yönlendir


@app.route('/guncelle_kelime/<int:id>', methods=['GET', 'POST'])
def guncelle_kelime(id):
    conn, cursor = get_db_connection()
    
    if request.method == 'POST':
        kelime_kendi = request.form['kelime_kendi']
        kelime_anlami = request.form['kelime_anlami']
        
        cursor.execute("""
            UPDATE kelime_kutu SET kelime_kendi = ?, kelime_anlami = ? WHERE id = ?
        """, (kelime_kendi, kelime_anlami, id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('girilen_kelimeler'))  # Güncelleme sonrası tekrar kelimeler sayfasına yönlendir

    else:
        cursor.execute("SELECT * FROM kelime_kutu WHERE id = ?", (id,))
        kelime = cursor.fetchone()
        conn.close()

        return render_template('guncelle_kelime.html', kelime=kelime)  # Güncelleme formunu render et

@app.route('/submit_kelime', methods=['POST'])
def submit_kelime():
    kelime_kendi = request.form['kelime_kendi']
    kelime_anlami = request.form['kelime_anlami']
    
    conn, cursor = get_db_connection()

    # SQL sorgusu ile veriyi veritabanına ekleyin
    cursor.execute("""
        INSERT INTO kelime_kutu (kelime_kendi, kelime_anlami)
        VALUES (?, ?)
    """, (kelime_kendi, kelime_anlami))
    conn.commit()

    return f"kelime başarıyla kaydedildi!"


if __name__ == '__main__':
    print("Uygulama çalışıyor: http://127.0.0.1:5000//")
    app.run(debug=True)
    
    
