from flask import Flask, request, render_template
import pickle
import numpy as np
import os
from tensorflow.keras.models import load_model
from PIL import Image
import io
import base64

app = Flask(__name__)

base_path = os.path.dirname(__file__)

model_path = os.path.join(base_path, '../artifacts/model.pkl')
scaler_path = os.path.join(base_path, '../artifacts/scaler.pkl')
vision_model_path = os.path.join(base_path, '../artifacts/wildfire_model_64x64.h5')

model = pickle.load(open(model_path, 'rb'))
scaler = pickle.load(open(scaler_path, 'rb'))
vision_model = load_model(vision_model_path)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        features = [float(x) for x in request.form.values()]
        final_features = [np.array(features)]
        final_features_scaled = scaler.transform(final_features)
        
        prediction = model.predict(final_features_scaled)
        output = round(prediction[0], 2)

        if output < 10:
            risk_msg = "Risque Faible"
            css_class = "low-risk"
        elif output < 20:
            risk_msg = "Risque Modéré"
            css_class = "medium-risk"
        else:
            risk_msg = "Risque Élevé ! Danger"
            css_class = "high-risk"

        return render_template('home.html', 
                               prediction_text=f'Indice FWI : {output}', 
                               risk_text=risk_msg,
                               css_class=css_class,
                               temp=request.form.get('Temperature'),
                               rh=request.form.get('RH'),
                               ws=request.form.get('Ws'),
                               rain=request.form.get('Rain'))

    except Exception as e:
        return render_template('home.html', prediction_text=f'Erreur : {str(e)}')

@app.route('/predict_image', methods=['POST'])
def predict_image():
    try:
        if 'file' not in request.files:
            return render_template('home.html', img_error="Aucun fichier envoyé")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('home.html', img_error="Aucun fichier sélectionné")

        if file:
            img = Image.open(file.stream).convert('RGB')
            
            data = io.BytesIO()
            img.save(data, "JPEG")
            encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')

            img_resized = img.resize((64, 64))
            img_array = np.array(img_resized)
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            prediction = vision_model.predict(img_array)
            class_idx = np.argmax(prediction, axis=1)[0]
            confidence = np.max(prediction) * 100
            
            if class_idx == 1:
                result_text = "FEU DÉTECTÉ"
                result_css = "high-risk"
            else:
                result_text = "PAS DE FEU"
                result_css = "low-risk"

            return render_template('home.html', 
                                   image_result=result_text, 
                                   image_conf=f"{confidence:.1f}%", 
                                   image_css=result_css,
                                   uploaded_image=encoded_img_data)

    except Exception as e:
        return render_template('home.html', img_error=f'Erreur : {str(e)}')

if __name__ == "__main__":
    app.run(debug=True)