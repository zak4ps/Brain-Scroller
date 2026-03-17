import fitz
import os

pdf_path = "Articles/Glaciers/G47211-SuppMat.pdf"
output_dir = "static/images/glaciers"

if not os.path.exists(pdf_path):
    print(f"ERROR: Cannot find PDF at {pdf_path}")
else:
    doc = fitz.open(pdf_path)
    print(f"PDF opened. Total pages: {len(doc)}")
    
    found_any = False
    for i in range(len(doc)):
        imgs = doc[i].get_images()
        if imgs:
            print(f"Page {i} has {len(imgs)} images.")
            found_any = True
            
    if not found_any:
        print("No raster images found. The 'figures' might be vector drawings.")