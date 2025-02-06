from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.cloud import aiplatform
import requests

# Définir les scopes nécessaires
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

# Charger les credentials et ajouter les scopes
credentials = service_account.Credentials.from_service_account_file(
    "./serviceAccountKey.json", scopes=SCOPES
)

# Initialisation de Vertex AI avec tes credentials et ton projet
aiplatform.init(
    project="quizgame-1935d",  # Remplace par ton ID de projet
    location="us-central1",  # Remplace par la région que tu utilises
    credentials=credentials  # Passe les credentials directement
)

@app.route('/IA', methods=['GET'])
def IA():
    # Exemple de texte que tu veux envoyer
    texte = "parle moi de l'IA"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # Vérifier et rafraîchir les credentials si nécessaire
    try:
        if not credentials.valid:
            credentials.refresh(Request())
    except Exception as e:
        return jsonify({"error": f"Problème avec les credentials : {str(e)}"}), 500
    
    # Préparer les paramètres de la requête POST
    data = {
        'contents': [{
            'parts': [{
                'text': texte
            }]
        }]
    }

    # Envoi de la requête POST
    response = requests.post(url, json=data, headers={
        "Authorization": f"Bearer {credentials.token}",  # Utiliser le token d'accès pour authentifier la requête
        "Content-Type": "application/json"  # Spécifier le type de contenu comme JSON
    })

    # Vérifie la réponse et la retourne
    if response.status_code == 200:
        return jsonify(response.json())  # Retourne la réponse JSON
    else:
        # Si l'API renvoie une erreur, loguer la réponse complète
        error_details = response.json() if response.content else 'No content in response'
        return jsonify({
            "error": "Erreur lors de l'appel à l'API Gemini",
            "status_code": response.status_code,
            "details": error_details
        }), response.status_code

if __name__ == "__main__":
    app.run(debug=True)
