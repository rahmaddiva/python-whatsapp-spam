from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

app = Flask(__name__)

# Konfigurasi direktori profile agar tidak perlu scan ulang QR
profile_dir = os.path.join(os.getcwd(), "chrome_profile")
os.makedirs(profile_dir, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={profile_dir}")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")

# Inisialisasi driver Chrome dengan profile
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Buka WhatsApp Web
driver.get("https://web.whatsapp.com")
input("Silakan scan QR code WhatsApp, lalu tekan Enter...")

@app.route('/')
def index():
    return '''
    <h2>Kirim Pesan WhatsApp</h2>
    <form method="POST" action="/send">
        Nomor (ex: 085705955978): <input type="text" name="number"><br>
        Pesan: <textarea name="message"></textarea><br>
        Jumlah Kirim: <input type="number" name="count" value="1"><br>
        <input type="submit" value="Kirim">
    </form>
    '''

@app.route('/send', methods=['POST'])
def send_message():
    number = request.form.get('number')
    message = request.form.get('message')
    count = int(request.form.get('count', 1))

    if not number or not message:
        return jsonify({"status": "error", "message": "Nomor dan pesan wajib diisi"})

    # Format nomor ke +62
    if number.startswith('0'):
        number = '62' + number[1:]
    elif number.startswith('+'):
        number = number[1:]

    # Akses URL chat
    url = f"https://web.whatsapp.com/send?phone={number}&text="
    driver.get(url)
    time.sleep(15)  # Tunggu halaman terbuka

    try:
        input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true" and @data-tab="10"]'))
        )

        for _ in range(count):
            input_box.send_keys(message)
            time.sleep(1)
            input_box.send_keys(Keys.ENTER)
            time.sleep(1)

        return jsonify({"status": "success", "message": f"{count} pesan berhasil dikirim ke {number}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
