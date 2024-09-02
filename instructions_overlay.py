#!/usr/bin/env python3

from PIL import Image
import numpy as np
import cv2  # We'll still use cv2 for getPerspectiveTransform
import fitz
import base64
import os
from io import BytesIO

def make_photo():
    src_pts = np.array([[0, 0], [611, 0], [611, 664], [0, 664]], dtype=np.float32)
    # dst_pts = np.array([[1455, 4547], [2777, 5388], [3388, 4178], [2257, 3698]], dtype=np.float32)
    dst_pts = np.array([  # Top-left
                       [2777, 5388], # top left
                       [1455, 4547], # top right
                       [2150, 3800], # bottom right
                       [3250, 4320] # bottom left
                        ],
                      dtype=np.float32)
    # Load the images
    foreground = Image.open("resources/first_page.jpg")
    foreground = foreground.convert("RGBA")
    foreground.putalpha(255)
    background = Image.open("resources/empty_printer.png")

    # Calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Apply perspective transform using NumPy and PIL
    foreground_array = np.array(foreground)
    warped_foreground = cv2.warpPerspective(foreground_array, M, (background.width, background.height))
    warped_foreground = Image.fromarray(warped_foreground)

    # Combine the images using alpha composite
    background.paste(warped_foreground, (0, 0), warped_foreground)
    
    background.save("resources/new_img.png")
    

def first_page_jpg():
    fp_pdf = fitz.open("resources/my_pdf.pdf")
    page = fp_pdf.load_page(0)  # number of page
    pix = page.get_pixmap()
    output = "resources/first_page-t.jpg"
    pix.save(output)
    fp_pdf.close()

    img = Image.open('resources/first_page-t.jpg')
    resized_img = img.resize((596, 842))
    resized_img.save('resources/first_page.jpg')
    img.close()

    os.remove('resources/first_page-t.jpg')


def html():

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    * {{box-sizing: border-box;}}

    .img-magnifier-container {{
      position:relative;
    }}

    .img-magnifier-glass {{
      position: absolute;
      border: 3px solid #000;
      border-radius: 50%;
      cursor: none;
      /*Set the size of the magnifier glass:*/
      width: 180px;
      height: 180px;
    }}
    </style>
    <script>
    function magnify(imgID, zoom) {{
      var img, glass, w, h, bw;
      img = document.getElementById(imgID);
      /*create magnifier glass:*/
      glass = document.createElement("DIV");
      glass.setAttribute("class", "img-magnifier-glass");
      /*insert magnifier glass:*/
      img.parentElement.insertBefore(glass, img);
      /*set background properties for the magnifier glass:*/
      glass.style.backgroundImage = "url('" + img.src + "')";
      glass.style.backgroundRepeat = "no-repeat";
      glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
      bw = 3;
      w = glass.offsetWidth / 2;
      h = glass.offsetHeight / 2;
      /*execute a function when someone moves the magnifier glass over the image:*/
      glass.addEventListener("mousemove", moveMagnifier);
      img.addEventListener("mousemove", moveMagnifier);
      /*and also for touch screens:*/
      glass.addEventListener("touchmove", moveMagnifier);
      img.addEventListener("touchmove", moveMagnifier);
      function moveMagnifier(e) {{
        var pos, x, y;
        /*prevent any other actions that may occur when moving over the image*/
        e.preventDefault();
        /*get the cursor's x and y positions:*/
        pos = getCursorPos(e);
        x = pos.x;
        y = pos.y;
        /*prevent the magnifier glass from being positioned outside the image:*/
        if (x > img.width - (w / zoom)) {{x = img.width - (w / zoom);}}
        if (x < w / zoom) {{x = w / zoom;}}
        if (y > img.height - (h / zoom)) {{y = img.height - (h / zoom);}}
        if (y < h / zoom) {{y = h / zoom;}}
        /*set the position of the magnifier glass:*/
        glass.style.left = (x - w) + "px";
        glass.style.top = (y - h) + "px";
        /*display what the magnifier glass "sees":*/
        glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
      }}
      function getCursorPos(e) {{
        var a, x = 0, y = 0;
        e = e || window.event;
        /*get the x and y positions of the image:*/
        a = img.getBoundingClientRect();
        /*calculate the cursor's x and y coordinates, relative to the image:*/
        x = e.pageX - a.left;
        y = e.pageY - a.top;
        /*consider any page scrolling:*/
        x = x - window.pageXOffset;
        y = y - window.pageYOffset;
        return {{x : x, y : y}};
      }}
    }}
    </script>
    </head>
    <body>

    <div class="img-magnifier-container">
      <img id="myimage" src="resources/new_img.png" width="525" height="700">
    </div>


    <script>
    /* Initiate Magnify Function
    with the id of the image, and the strength of the magnifier glass:*/
    magnify("myimage", 5);
    </script>

    </body>
    </html>
    """
