from multiprocessing import Process



import subprocess
def subrun():
    
    subprocess.run(['python3', 'nodpi.py']) 
    print('runned')
def substart():
    
    subprocess.run(['python3', 'interface.py']) 
    print('started')


def run():

        p1 = Process(target=subrun, args=(), daemon=True)
        p2 = Process(target=substart, args=(), daemon=True)
        p1.start()
        p2.start()
        p1.join()
        p2.join()

def start_window():
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
    from PyQt5.QtGui import QIcon
    app = QApplication([])

    window = QWidget()
    window.setGeometry(300, 300, 300, 300)
    window.setWindowIcon(QIcon('youunlock.png'))
    window.setWindowTitle('Разблокировщик ютуба')

    startbutton=QPushButton('Запуск сервиса')
    startbutton.clicked.connect(run)

    layout = QVBoxLayout()
    layout.addWidget(startbutton)

    window.setLayout(layout)
    window.show()
    app.exec_() 
run()

