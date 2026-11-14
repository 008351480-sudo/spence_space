from PIL import Image
import pytesseract
import re
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

vidcap = cv2.VideoCapture(0)

if not cv2.VideoCapture(0).isOpened():
    print("Error: Could not open webcam.")
    exit()

input("Press Enter to capture your receipt...")

success, frame = vidcap.read()
if success:
        cv2.imwrite("captured_image.jpg", frame)
        print("Photo captured and saved as 'captured_image.jpg'.")
        




        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        text=pytesseract.image_to_string(gray_frame, lang='eng', config='--psm 6')
        clean_text = text.replace("\x0c", "").strip()
        print("Extracted Text:")
        if clean_text.strip():

            print(clean_text)
        else:
            print("No text found in the image.")
else:
    print("Error: Could not read frame from webcam.")

price_pattern = re.compile(r'(.*?)\s+(\d+[\.,]\d{2})') ## text pattern to match item names and prices
                                                       ## add text pattern for recognizing quantity
print("--- Extracted Items ---")
for line in clean_text.split("\n"):
    match = price_pattern.match(line.strip())
    if match:
        item_name = match.group(1).strip()
        price = match.group(2).replace(',', '.') # Normalize decimal separators
        
        # Filter out common receipt metadata blocks
        if not any(word in item_name.upper() for word in ["TOTAL", "SUBTOTAL", "TAX", "CASH"]):
            print(f"Item: {item_name} -> Price: ${price}")

vidcap.release()
cv2.destroyAllWindows()