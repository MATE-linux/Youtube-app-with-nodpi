import random
import asyncio
import threading
from PyQt5 import QtWebEngineWidgets, QtCore, QtWidgets, QtNetwork
from PyQt5.QtGui import QIcon

# Глобальные переменные
BLOCKED = [line.rstrip().encode() for line in open('blacklist.txt', 'r', encoding='utf-8')]
TASKS = []
stop_event = threading.Event()  # Событие для остановки asyncio-сервера

# Асинхронные функции
async def main(host, port):
    server = await asyncio.start_server(new_conn, host, port)
    async with server:
        while not stop_event.is_set():  # Проверяем stop_event
            await asyncio.sleep(0.1)
        print("Server is stopping...")

async def pipe(reader, writer):
    try:
        while not reader.at_eof() and not writer.is_closing():
            writer.write(await reader.read(1500))
            await writer.drain()
    except Exception as e:
        print(f"Error in pipe: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def new_conn(local_reader, local_writer):
    http_data = await local_reader.read(1500)
    try:
        type, target = http_data.split(b"\r\n")[0].split(b" ")[0:2]
        host, port = target.split(b":")
    except:
        local_writer.close()
        return

    if type != b"CONNECT":
        local_writer.close()
        return

    local_writer.write(b'HTTP/1.1 200 OK\n\n')
    await local_writer.drain()

    try:
        remote_reader, remote_writer = await asyncio.open_connection(host, port)
    except:
        local_writer.close()
        return

    if port == b'443':
        await fragment_data(local_reader, remote_writer)

    TASKS.append(asyncio.create_task(pipe(local_reader, remote_writer)))
    TASKS.append(asyncio.create_task(pipe(remote_reader, local_writer)))

async def fragment_data(local_reader, remote_writer):
    head = await local_reader.read(5)
    data = await local_reader.read(1500)
    parts = []
    if all([data.find(site) == -1 for site in BLOCKED]):
        remote_writer.write(head + data)
        await remote_writer.drain()
        return

    while data:
        part_len = random.randint(1, len(data))
        parts.append(bytes.fromhex("1603") + bytes([random.randint(0, 255)]) + int(
            part_len).to_bytes(2, byteorder='big') + data[0:part_len])
        data = data[part_len:]

    remote_writer.write(b''.join(parts))
    await remote_writer.drain()

def run_function():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Запускаем asyncio-сервер
        loop.run_until_complete(main(host='127.0.0.1', port=8881))
    except asyncio.CancelledError:
        print("Asyncio server stopped")
    finally:
        # Отменяем все задачи
        for task in TASKS:
            task.cancel()
        # Очищаем ресурсы
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

# Класс главного окна PyQt5
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        # Устанавливаем событие stop_event при закрытии окна
        stop_event.set()
        event.accept()

# Интерфейс PyQt5
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.webView = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        self.webView.setUrl(QtCore.QUrl("https://www.youtube.com"))
        self.webView.setObjectName("webView")
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Youtube", "Youtube"))
        MainWindow.setWindowIcon(QIcon('youtube.png'))

def interface_window():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    proxy = QtNetwork.QNetworkProxy()
    proxy.setType(QtNetwork.QNetworkProxy.HttpProxy)
    proxy.setHostName("127.0.0.1")
    proxy.setPort(8881)
    QtNetwork.QNetworkProxy.setApplicationProxy(proxy)

    window = MainWindow()
    window.show()
    app.exec_()  # Убираем sys.exit

def subrun():
    run_function()

def substart():
    interface_window()

def run():
    thread1 = threading.Thread(target=substart)
    thread2 = threading.Thread(target=subrun)

    thread2.start()
    thread1.start()

    # Ждем, пока окно PyQt5 не закроется
    thread1.join()

    # Останавливаем asyncio-сервер
    stop_event.set()
    thread2.join()

    print("All threads are done")

if __name__ == '__main__':
    run()