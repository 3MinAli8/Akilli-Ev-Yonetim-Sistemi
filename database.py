import sqlite3
import numpy as np

# Veritabanı dosya adı (PyCharm projenin ana dizininde oluşturulacak)
DB_NAME = "smarthome.db"


def get_connection():
    """
    Veritabanı bağlantısını başlatan yardımcı fonksiyon.
    """
    return sqlite3.connect(DB_NAME)


def init_db():
    """
    Veritabanını ve gerekli tabloları (Users ve AccessLogs) yoksa sıfırdan oluşturur.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. KULLANICILAR TABLOSU
    # - id: Benzersiz numara
    # - name: Kişi adı
    # - gender: Cinsiyet
    # - role: Ev Sahibi / Misafir / Yönetici
    # - face_encoding: Yüzün matematiksel vektörü (BLOB formatında)
    # - created_at: Kayıt tarihi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        role TEXT DEFAULT 'Ev Sahibi',
        face_encoding BLOB NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. GİRİŞ LOGLARI TABLOSU
    # - log_id: Log numarası
    # - user_id: Giren kişinin Users tablosundaki ID'si (Bilinmiyorsa NULL)
    # - status: 'Başarılı', 'Bilinmeyen Yüz' vb.
    # - timestamp: Giriş denemesinin yapıldığı anlık saat/tarih
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AccessLogs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✓ Veritabanı ve tablolar başarıyla hazırlandı.")


def add_user(name, gender, encoding_array, role="Ev Sahibi"):
    """
    Yeni bir kullanıcıyı veritabanına ekler.
    :param name: Kişinin adı
    :param gender: Cinsiyeti ('Erkek' / 'Kadın')
    :param encoding_array: Kameradan alınan Numpy yüz vektörü
    :param role: Kullanıcı rolü (Varsayılan: 'Ev Sahibi')
    :return: Eklenen kullanıcının ID'si
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Numpy dizisini SQLite'ın BLOB tipine kaydedebilmek için bayt (bytes) formatına dönüştürüyoruz
    encoding_bytes = encoding_array.tobytes()

    cursor.execute('''
        INSERT INTO Users (name, gender, role, face_encoding) 
        VALUES (?, ?, ?, ?)
    ''', (name, gender, role, encoding_bytes))

    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()

    print(f"✓ Kullanıcı eklendi: {name} (ID: {inserted_id})")
    return inserted_id


def get_all_users():
    """
    Eşleştirme yapılabilmesi için veritabanındaki tüm kullanıcıları çeker.
    BLOB verisini tekrar Numpy dizisine çevirir.
    :return: Kullanıcı sözlüklerinden oluşan bir liste
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, gender, role, face_encoding FROM Users')
    rows = cursor.fetchall()

    users = []
    for row in rows:
        user_id, name, gender, role, encoding_bytes = row

        # Veritabanından gelen bayt verisini tekrar float64 tipinde Numpy dizisine dönüştürüyoruz
        encoding_array = np.frombuffer(encoding_bytes, dtype=np.float64)

        users.append({
            "id": user_id,
            "name": name,
            "gender": gender,
            "role": role,
            "encoding": encoding_array
        })

    conn.close()
    return users


def log_access(user_id, status):
    """
    Kapıdaki her bir giriş/tanıma denemesini log tablosuna kaydeder.
    :param user_id: Tanınan kullanıcının ID'si (Tanınamadıysa None verilmeli)
    :param status: Giriş durumu ('Başarılı', 'Bilinmeyen Yüz', 'Erişim Engellendi')
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO AccessLogs (user_id, status) 
        VALUES (?, ?)
    ''', (user_id, status))

    conn.commit()
    conn.close()
    print(f"✓ Log Kaydedildi: [{status}]")


def get_access_logs():
    """
    Arayüzde gösterilmek üzere son giriş loglarını isimlerle birleştirerek (JOIN) getirir.
    :return: Log verileri listesi
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            AccessLogs.log_id,
            COALESCE(Users.name, 'Bilinmeyen Kişi') AS user_name,
            AccessLogs.status,
            AccessLogs.timestamp
        FROM AccessLogs
        LEFT JOIN Users ON AccessLogs.user_id = Users.id
        ORDER BY AccessLogs.timestamp DESC
    ''')

    logs = cursor.fetchall()
    conn.close()
    return logs


# ==============================================================================
# TEST VE ÇALIŞTIRMA BÖLÜMÜ
# Bu dosya doğrudan çalıştırıldığında aşağıdaki test kodları yürütülür.
# ==============================================================================
if __name__ == "__main__":
    # 1. Veritabanını ve tabloları başlat
    init_db()

    print("\n--- TEST 1: Kullanıcı Ekleme ---")
    # Kamera modülünden gelen 128 elemanlı yüz vektörünü simüle etmek için rastgele bir dizi üretiyoruz
    ornek_yuz_vektoru = np.random.rand(128)
    
    # Test kullanıcısı ekleyelim
    yeni_id = add_user(
        name="Ali", 
        gender="Erkek", 
        encoding_array=ornek_yuz_vektoru, 
        role="Ev Sahibi"
    )

    print("\n--- TEST 2: Giriş Logu Oluşturma ---")
    # Başarılı giriş logu atalım
    log_access(user_id=yeni_id, status="Başarılı")
    # Tanınmayan yüz logu atalım (user_id = None)
    log_access(user_id=None, status="Bilinmeyen Yüz")

    print("\n--- TEST 3: Veritabanındaki Kullanıcıları Okuma ---")
    kullanicilar = get_all_users()
    for k in kullanicilar:
        print(f"ID: {k['id']} | İsim: {k['name']} | Cinsiyet: {k['gender']} | Rol: {k['role']} | Vektör Boyutu: {len(k['encoding'])}")

    print("\n--- TEST 4: Giriş Loglarını Okuma ---")
    loglar = get_access_logs()
    for log in loglar:
        print(f"Log ID: {log[0]} | Kişi: {log[1]} | Durum: {log[2]} | Tarih: {log[3]}")