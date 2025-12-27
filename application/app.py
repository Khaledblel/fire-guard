from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import os

app = Flask(__name__)

base_path = os.path.dirname(__file__)
model_path = os.path.join(base_path, '../artifacts/model.pkl')
scaler_path = os.path.join(base_path, '../artifacts/scaler.pkl')

print(f"Chargement du modèle depuis : {model_path}")
model = pickle.load(open(model_path, 'rb'))
scaler = pickle.load(open(scaler_path, 'rb'))


@app.route('/')
def home():
    """Affiche la page d'accueil avec le formulaire."""
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Récupère les données du formulaire, normalise, prédit et renvoie le résultat.
    """
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
                               css_class=css_class)

    except Exception as e:
        return render_template('home.html', prediction_text=f'Erreur : {str(e)}')

if __name__ == "__main__":
    app.run(debug=True)