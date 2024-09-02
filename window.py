#!/usr/bin/env python3

import sys
import os
import shutil
import ds_code 
import time
import warnings
import math

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QPushButton, QFileDialog, QFrame, QMessageBox, QLineEdit)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QEvent, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent, QPainter, QPixmap, QColor, QBrush, QPainter, QCursor


warnings.filterwarnings("ignore", category=DeprecationWarning)

base_dir = os.path.dirname(__file__)


with open(os.path.join(base_dir,"resources/printer_name.txt"), "r") as pn_txt:
    printer_name = pn_txt.read().strip()


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
                shutil.copy(file_paths[0], os.path.join(base_dir, "resources/my_pdf.pdf"))

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
            shutil.copy(file_name, os.path.join(base_dir, "resources/my_pdf.pdf"))
            self.label.setText(f"Selected: {file_name}")

            self.printer.show()
            
            self.printer.total_pages = ds_code.count_pages(file_name)
            self.printer.total_label.setText(f"There are {self.printer.total_pages} total pages.")
            self.printer.currently_printing.setText(f"You have selected {self.printer.total_pages} pages.")
            self.printer.page_range.setText(f"1-{self.printer.total_pages}")

            page_count_first_print = math.ceil(self.printer.total_pages / 2)
            self.printer.first_button.setText(f"Start Printing the First {page_count_first_print} Pages ")
            self.close()



class Printer1(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("DoubleSider")

        self.total_label = QLabel()
        self.currently_printing = QLabel()
        self.range_label = QLabel("Define the pages you'd want printed. \nFor example: 1-12, 14, 24-25")
    
        self.page_range = QLineEdit()
        self.page_range.textChanged.connect(self.range_validator)


        self.first_button = QPushButton("Start Printing")
        self.first_button.clicked.connect(self.first_button_go)
        self.printer2 = Printer2()

        if not ds_code.check_printer(printer_name):
            self.warn_no_printer()
            pass

        self.done_button = QPushButton("Click, once that has *finished* printing.")
        self.done_button.clicked.connect(self.done_button_go)


        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.total_label)
        self.vbox.addWidget(self.currently_printing)
        self.vbox.addWidget(self.range_label)
        self.vbox.addWidget(self.page_range)
        self.hbox.addWidget(self.first_button)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

    def range_validator(self, text):
        try:
            self.first_button.setEnabled(False)
            list_of_pages = []
            page_ranges_list = text.split(",")
            for page_range in page_ranges_list:
                page_range = page_range.replace(",","").strip()

                start_and_end = page_range.split("-")
                if len(start_and_end) >= 3:
                    raise ValueError("bad input0")
                if len(start_and_end) == 1:
                    if int(start_and_end[0]) > self.total_pages:
                        raise ValueError("out of range")
                    if not(int(start_and_end[0]) in list_of_pages):
                        list_of_pages.append(int(start_and_end[0]))
                elif len(start_and_end) == 2:
                    if int(start_and_end[0]) > int(start_and_end[1]):
                        raise ValueError("bad input 1")
                    pages_in_this_range = range(int(start_and_end[0]), int(start_and_end[1])+1) 
                    for page in pages_in_this_range:
                        if int(page) > self.total_pages:
                            raise ValueError("out of range")
                        if not(page in list_of_pages):
                            list_of_pages.append(int(page))

            list_of_pages = sorted(list_of_pages)
            self.first_button.setText(f"Start Printing the First {math.ceil(len(list_of_pages) / 2)} Pages")
            self.currently_printing.setText(f"You have selected {len(list_of_pages)} pages.")
            self.first_button.setEnabled(True)
            return list_of_pages
        except ValueError:
            pass
      

    def range_creator(self):
        list_of_pages = []
        try:
            text = self.page_range.text()
            page_ranges_list = text.split(",")
            for page_range in page_ranges_list:
                page_range = page_range.replace(",","").strip()

                start_and_end = page_range.split("-")
                if len(start_and_end) >= 3:
                    raise ValueError("bad input0")
                if len(start_and_end) == 1:
                    if int(start_and_end[0]) > self.total_pages:
                        raise ValueError("out of range")
                    if not(int(start_and_end[0]) in list_of_pages):
                        list_of_pages.append(int(start_and_end[0]))
                elif len(start_and_end) == 2:
                    if int(start_and_end[0]) > int(start_and_end[1]):
                        raise ValueError("bad input 1")
                    pages_in_this_range = range(int(start_and_end[0]), int(start_and_end[1])+1) 
                    for page in pages_in_this_range:
                        if int(page) > self.total_pages:
                            raise ValueError("out of range")
                        if not(page in list_of_pages):
                            list_of_pages.append(int(page))
        except ValueError:
            pass

        return list_of_pages


    def first_button_go(self):
        self.first_button.setEnabled(False)
        self.update()
        ds_code.split_pdf(os.path.join(base_dir, os.path.join(base_dir,"resources/my_pdf.pdf")), sorted(self.range_creator())) # add list processer
        ds_code.send_print(printer_name,"first")


        import instructions_overlay # this is really hacky moving the order of import to avoid some strange conflict.
        instructions_overlay.first_page_jpg()
        instructions_overlay.make_photo()

        self.vbox.addWidget(self.done_button)

    def done_button_go(self):
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

        if not ds_code.check_printer(printer_name):
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
        ds_code.send_print(printer_name,"second")
        self.close()
        app.quit()
        sys.exit()




def file_cleanup():
    if os.path.exists(os.path.join(base_dir, "resources/first_page.jpg")):
        os.remove(os.path.join(base_dir, "resources/first_page.jpg"))
    if os.path.exists(os.path.join(base_dir, "resources/my_pdf.pdf")):
        os.remove(os.path.join(base_dir, "resources/my_pdf.pdf"))
    if os.path.exists(os.path.join(base_dir, "resources/new_img.png")):
        os.remove(os.path.join(base_dir, "resources/new_img.png"))
    if os.path.exists(os.path.join(base_dir, "resources/first_print.pdf")):
        os.remove(os.path.join(base_dir, "resources/first_print.pdf"))
    if os.path.exists(os.path.join(base_dir, "resources/second_print.pdf")):
        os.remove(os.path.join(base_dir, "resources/second_print.pdf"))


if __name__ == "__main__":
    file_cleanup()
    app = QApplication(sys.argv)
    window = DoubleSider()
    window.show()
    #b = Printer1()
    #b.show()
    sys.exit(app.exec_())


