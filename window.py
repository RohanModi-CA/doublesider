#!/usr/bin/env python3

import sys
import os
import shutil
import ds_code 
import time
import warnings
import math

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QPushButton, QFileDialog, QFrame, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QEvent, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent, QPainter, QPixmap, QColor, QBrush, QPainter, QCursor


warnings.filterwarnings("ignore", category=DeprecationWarning)

class DoubleSider(QWidget):
    def __init__(self):
        super().__init__()
        self.printer = Printer1()

        # Set window title
        self.setWindowTitle("DoubleSider")

        # Create a label
        self.label = QLabel("Drop Files Here")
        self.label.setAlignment(Qt.AlignCenter)

        # Create a frame for drop area styling
        self.drop_frame = QFrame(self)
        self.drop_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 5px;
                min-width: 200px;  
                min-height: 100px; 
            }
        """)

        # Create a button
        self.browse_button = QPushButton("or, click to browse")
        self.browse_button.clicked.connect(self.open_file_dialog)

        # Create layouts
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(self.browse_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.drop_frame)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # Set up drag and drop events
        self.setAcceptDrops(True)
        self.drop_frame.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self.label.setText("Drop Files Here")
        self.drop_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 5px;
                min-width: 200px;  
                min-height: 100px; 
            }
        """)

    def dropEvent(self, event: QDropEvent) -> None:
        event.acceptProposedAction()
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls]

        # Update label with dropped file information
        

        if len(file_paths) == 1:

            if file_paths[0][-3:] == "pdf":

                self.label.setText(f"Dropped: {file_paths[0]}")
                shutil.copy(file_paths[0], "resources/my_pdf.pdf")

                self.printer.show()
                page_count_first_print = math.ceil(ds_code.count_pages(file_paths[0]) / 2)
                self.printer.first_button.setText(f"Start Printing the First {page_count_first_print} Pages ")
                self.close()
            else:
                self.label.setText("PDFs only please.")

            
    
        else:
            self.label.setText(f"One File at a Time.")

        # Update drop frame style
        self.drop_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                min-width: 200px;  
                min-height: 100px; 
            }
        """)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf)"
        )
        if file_name:
            shutil.copy(file_name, "resources/my_pdf.pdf")
            self.label.setText(f"Selected: {file_name}")

            self.printer.show()
            page_count_first_print = math.ceil(ds_code.count_pages(file_name) / 2)
            self.printer.first_button.setText(f"Start Printing the First {page_count_first_print} Pages ")
            self.close()



class Printer1(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("DoubleSider")

        self.first_button = QPushButton("Start Printing")
        self.first_button.clicked.connect(self.first_button_go)
        self.printer2 = Printer2()

        if not ds_code.check_printer("HL-L2320D-series"):
            self.warn_no_printer()
            pass

        self.done_button = QPushButton("Click, once that has *finished* printing.")
        self.done_button.clicked.connect(self.done_button_go)


        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.hbox.addWidget(self.first_button)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

    def first_button_go(self):
        self.first_button.setEnabled(False)
        self.update()
        ds_code.split_pdf("resources/my_pdf.pdf")
        ds_code.send_print("HL-L2320D-series","first")


        import instructions_overlay # this is really hacky moving the order of import to avoid some strange conflict.
        instructions_overlay.first_page_jpg()
        instructions_overlay.make_photo()

        self.vbox.addWidget(self.done_button)

    def done_button_go(self):
        #self.printer2.olivia_pixmap = QPixmap('resources/new_img.png').scaledToHeight(800)
        #self.printer2.olivia.setPixmap(self.printer2.olivia_pixmap)
        import instructions_overlay
        self.printer2.web_view.setHtml(instructions_overlay.html(), baseUrl=QUrl.fromLocalFile(os.getcwd()+os.path.sep))

        self.printer2.show()
        self.close()


    def warn_no_printer(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("The printer is not online!")
        msg.setWindowTitle("Alert")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        app.quit()
        sys.exit()


class Printer2(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("DoubleSider")

        self.instruction_label = QLabel("Great! Now, grab add your stack of papers like so:")
        self.done = QPushButton("Click here to print the rest *after* having done that.")
        self.done.clicked.connect(self.done_go)
        self.olivia = QLabel()

        if not ds_code.check_printer("HL-L2320D-series"):
            #self.warn_no_printer()
            pass



        self.vbox = QVBoxLayout()
        
        self.vbox.addWidget(self.instruction_label)
        self.vbox.addWidget(self.olivia)

        self.setLayout(self.vbox)

        self.web_view = QWebEngineView()
        self.vbox.addWidget(self.web_view)
        self.web_view.setFixedSize(550,720)
        self.vbox.addWidget(self.done)

    def done_go(self):
        self.done.setEnabled(False)
        ds_code.send_print("HL-L2320D-series","second")
        self.close()
        app.quit()
        sys.exit()




def file_cleanup():
    if os.path.exists("resources/first_page.jpg"):
        os.remove("resources/first_page.jpg")
    if os.path.exists("resources/my_pdf.pdf"):
        os.remove("resources/my_pdf.pdf")
    if os.path.exists("resources/new_img.png"):
        os.remove("resources/new_img.png")
    if os.path.exists("resources/first_print.pdf"):
        os.remove("resources/first_print.pdf")
    if os.path.exists("resources/second_print.pdf"):
        os.remove("resources/second_print.pdf")


if __name__ == "__main__":
    file_cleanup()
    app = QApplication(sys.argv)
    window = DoubleSider()
    window.show()
    #b = Printer1()
    #b.show()
    sys.exit(app.exec_())


