import cv2
import pytesseract
import re
import json
import requests
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

imagen_path = 'patente0.jpg'
imagen = cv2.imread(imagen_path)
patente = []
texto = []

gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
gray = cv2.blur(gray, (3, 3))
canny = cv2.Canny(gray, 150, 200)
canny = cv2.dilate(canny, None, iterations=1)
cnts, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

for c in cnts:
    area = cv2.contourArea(c)
    x, y, w, h = cv2.boundingRect(c)
    epsilon = 0.09 * cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, epsilon, True)
    if len(approx) == 4 and area > 9000:
        print('area=', area)
        aspect_ratio = float(w) / h
        if aspect_ratio > 2.4:
            patente = gray[y:y+h, x:x+w]
            texto = pytesseract.image_to_string(patente, lang='eng', config='--psm 7')
            
            texto = re.sub(r'[^A-Za-z0-9]', '', texto)

            if len(texto) >= 6:
                print(f'Patente detectada: {texto}')

                registro = {
                    "patente": texto,
                    "timestamp": datetime.now().isoformat(), 
                    "ubicacion": "Entrada principal"
                }

                json_data = json.dumps(registro, indent=4)
                print("JSON generado:", json_data)

                url = "http://127.0.0.1:5001/registropatente"
                try:
                    response = requests.post(url, json=registro)
                    if response.status_code == 200:
                        print("Datos enviados correctamente al servicio.")
                    else:
                        print(f"Error al enviar los datos: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Error de conexión: {e}")

            print('patente=', texto)
            cv2.imshow('patente', patente)
            cv2.moveWindow('patente', 780, 10)
            cv2.rectangle(imagen, (x, y), (x+w, y+h), (0, 255, 0))
            cv2.putText(imagen, texto, (x-20, y-10), 1, 2.2, (0, 255, 0), 3)

cv2.imshow('Imagen', imagen)
cv2.moveWindow('Imagen', 45, 10)
cv2.waitKey(0)