from gui.main_window import MainWindow
import resources.resources_rcc

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setOrganizationName("Sonance")
    app.setApplicationName("Sonance")
    
    player = MainWindow()
    player.show()

    sys.exit(app.exec_())
