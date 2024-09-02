#!/usr/bin/env python3

from PyPDF2 import PdfReader, PdfWriter
import subprocess
import os


base_dir = os.path.dirname(__file__)

def count_pages(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        page_count = len(reader.pages)
    return page_count

def split_pdf(pdf_path, page_range):

    with open(pdf_path, "rb") as pdf_file:
        range_reader = PdfReader(pdf_file)
        range_writer = PdfWriter()
        for page in page_range:
            page_to_add = range_reader.pages[page - 1]
            range_writer.add_page(page_to_add)

        with open(os.path.join(base_dir, "resources/temp-pdf.pdf"), "wb") as temp_pdf:
            range_writer.write(temp_pdf)


    with open(os.path.join(base_dir, "resources/temp-pdf.pdf"), "rb") as pdf_file:
        reader = PdfReader(pdf_file)

        page_list = range(len(reader.pages)) # creates a 0 index based list of pages


        # Create a new PDF writer object
        first_writer = PdfWriter()
        second_writer = PdfWriter()

        for page_num in page_list: 

            if page_num % 2 == 0: # add pages (0,2,4, ...) to the page to be printed immediately
                page = reader.pages[page_num]
                first_writer.add_page(page)
            elif page_num % 2 == 1: # add the next pages to the second print
                page = reader.pages[page_num]
                second_writer.add_page(page)
        if len(reader.pages) % 2 == 1:
            with open(os.path.join(base_dir, "resources/dot.pdf"), "rb") as dot_pdf:
                dot_reader = PdfReader(dot_pdf)
                dot_page = dot_reader.pages[0]
                second_writer.add_page(dot_page)

        # Save the new PDF file
        with open(os.path.join(base_dir, "resources/first_print.pdf"), "wb") as first_pdf:
            first_writer.write(first_pdf)
        with open(os.path.join(base_dir, "resources/second_print.pdf"), "wb") as second_pdf:
            second_writer.write(second_pdf)



def check_printer(printer_name):
    process = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
    output_list = process.stdout.split("\n")
    printer_status = ""
    for line in output_list:
        if line.find(printer_name) != -1:
            printer_status = line
            break
        pass

    if printer_status.find("idle") == -1 and printer_status.find("enabled") == -1:
       return False
    return True

def send_print(printer_name, first_or_second):
    if first_or_second != "first" and first_or_second != "second":
        raise ValueError("must be either 'first' or 'second'")
    first_print_process = os.system(f"lpr -P {printer_name} {base_dir}/resources/{first_or_second}_print.pdf")



   


