import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import numpy as np
import database as db  # Arkadaşının kodlarının database.py olarak kaydedildiğini varsayıyoruz

# "Veritabanı.txt" içerisinde yer almayan eksik silme fonksiyonu
def delete_user_from_db(user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_deleted > 0

class SmartHomePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Akıllı Ev Kontrol Paneli")
        self.root.geometry("500x400")
        
        # Veritabanını başlat
        db.init_db()

        # Durum Değişkenleri
        self.telegram_active = False
        self.bluetooth_active = False

        self.create_widgets()

    def create_widgets(self):
        # Üst Başlık
        lbl_title = tk.Label(self.root, text="Sistem Yönetim Paneli", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=15)

        # Kullanıcı Yönetimi Butonları
        frame_users = tk.LabelFrame(self.root, text="Kullanıcı Yönetimi", padx=10, pady=10)
        frame_users.pack(fill="x", padx=20, pady=5)

        btn_add = tk.Button(frame_users, text="Yeni Kullanıcı Ekle", command=self.add_user_ui, width=20)
        btn_add.pack(side="left", padx=10)

        btn_delete = tk.Button(frame_users, text="Kullanıcı Sil", command=self.delete_user_ui, width=20)
        btn_delete.pack(side="right", padx=10)

        # Haberleşme ve Uyarı Butonları
        frame_comm = tk.LabelFrame(self.root, text="Haberleşme & Uyarılar", padx=10, pady=10)
        frame_comm.pack(fill="x", padx=20, pady=15)

        self.btn_telegram = tk.Button(frame_comm, text="Telegram: KAPALI", command=self.toggle_telegram, width=20, fg="red")
        self.btn_telegram.pack(side="left", padx=10)

        self.btn_bluetooth = tk.Button(frame_comm, text="Bluetooth: BAĞLI DEĞİL", command=self.toggle_bluetooth, width=20, fg="red")
        self.btn_bluetooth.pack(side="right", padx=10)

        # Logları Görüntüleme
        btn_logs = tk.Button(self.root, text="Son Giriş Loglarını Gör", command=self.show_logs)
        btn_logs.pack(pady=10)

    def add_user_ui(self):
        name = simpledialog.askstring("Yeni Kullanıcı", "Kullanıcı Adı:")
        if not name:
            return
        gender = simpledialog.askstring("Yeni Kullanıcı", "Cinsiyet (Erkek/Kadın):")
        
        # Kamera modülü bağlanana kadar rastgele 128 boyutlu Numpy vektörü kullanıyoruz
        dummy_encoding = np.random.rand(128) 
        
        try:
            # db.add_user arkadaşının dosyasından çağrılıyor
            new_id = db.add_user(name=name, gender=gender, encoding_array=dummy_encoding)
            messagebox.showinfo("Başarılı", f"Kullanıcı başarıyla eklendi!\nID: {new_id}")
        except Exception as e:
            messagebox.showerror("Hata", f"Kullanıcı eklenirken hata oluştu:\n{e}")

    def delete_user_ui(self):
        user_id = simpledialog.askinteger("Kullanıcı Sil", "Silinecek Kullanıcının ID'sini girin:")
        if user_id:
            success = delete_user_from_db(user_id)
            if success:
                messagebox.showinfo("Başarılı", f"ID {user_id} sistemden silindi.")
            else:
                messagebox.showwarning("Bulunamadı", f"ID {user_id} ile eşleşen kullanıcı bulunamadı.")

    def toggle_telegram(self):
        self.telegram_active = not self.telegram_active
        if self.telegram_active:
            self.btn_telegram.config(text="Telegram: AKTİF", fg="green")
            # TODO: Telegram Bot API başlatma kodları buraya gelecek
            print("Telegram bildirimleri başlatıldı.")
        else:
            self.btn_telegram.config(text="Telegram: KAPALI", fg="red")
            # TODO: Telegram Bot API durdurma kodları buraya gelecek
            print("Telegram bildirimleri durduruldu.")

    def toggle_bluetooth(self):
        self.bluetooth_active = not self.bluetooth_active
        if self.bluetooth_active:
            self.btn_bluetooth.config(text="Bluetooth: BAĞLI", fg="green")
            # TODO: PyBluez veya Serial (HC-05 vb.) bağlanma kodları buraya gelecek
            print("Bluetooth modülüne bağlanılıyor...")
        else:
            self.btn_bluetooth.config(text="Bluetooth: BAĞLI DEĞİL", fg="red")
            # TODO: Bluetooth bağlantı koparma kodları buraya gelecek
            print("Bluetooth bağlantısı kesildi.")

    def show_logs(self):
        logs = db.get_access_logs()
        log_window = tk.Toplevel(self.root)
        log_window.title("Erişim Logları")
        log_window.geometry("400x300")
        
        listbox = tk.Listbox(log_window, width=50)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for log in logs:
            listbox.insert(tk.END, f"{log[3]} - {log[1]} ({log[2]})")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomePanel(root)
    root.mainloop()
