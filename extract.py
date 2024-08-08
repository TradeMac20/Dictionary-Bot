import easyocr
 

reader = easyocr.Reader(['en'])
result = reader.readtext('images/downloaded_image.jpg', detail = 0)
image_word = result
