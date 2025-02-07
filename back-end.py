import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import firebase_admin 
from firebase_admin import credentials, firestore, db, auth

app = Flask(__name__)
CORS(app, supports_credentials=True)

api_key = os.getenv('API_KEY')  # Accès à la variable d'environnement

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://quizgame-1935d-default-rtdb.europe-west1.firebasedatabase.app'
})

firestore_db = firestore.client()

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

codes = []

@app.route('/Cookie', methods=['GET'])
def Cookie():
    code = os.urandom(16).hex()
    codes.append(code)
    return jsonify({"cookie": code})
  
@app.route('/CookiePseudo', methods=['POST'])
def CookiePseudo():
    data = request.get_json()
    pseudo = data.get("pseudo", "")
    try:
        # Création d'un nouvel utilisateur Firebase avec un pseudo
        utilisateur = auth.create_user(display_name=pseudo)
        # Générer un jeton personnalisé pour l'utilisateur
        token = auth.create_custom_token(utilisateur.uid)
        return jsonify({"uid": utilisateur.uid, "token": token.decode('utf-8')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/Exemple', methods=['GET'])
def Exemple():
    codeUtilisateur = request.args.get('cookie')  # Récupère via l'URL
    if codeUtilisateur in codes:
        texte = """Génère moi un JSON contenant 1 nouveau exemple de prompt en t'inspirant de ces 9 exemples :
            Les présidents de la 5e république en France,
            Les présidents des Etats-Unis,
            Les rois de France,
            Jérôme à 3 frères et 4 soeurs,
            Ludivine a visité ces pays hors de l'Europe : Vietnam, Etats-Unis, Canada, Martinique et Tunisie,
            Adrien est allé faire du ski à Risoul, Val d'isère, Isola 2000, Alpes d'Huez, les Arcs, Courchevelle, les Menuires, le Sauze et Avoriaz et j'aimerais retourner à l'Alpes d'Huez,
            Le plat traditionnel Canadien est la poutine,
            Le Beausset compte 1098 habitants en 2022 et elle est catégorisée petite ville,
            Les monuments emblématiques de Paris,
            Les fleuves principaux en Europe,
            Camille a déjà visité des îles tropicales,
            Le plat national espagnol est la paella, souvent préparée avec du riz, des fruits de mer, du poulet et des épices,
            Martin collectionne les timbres représentant des animaux en voie de disparition,
            Une des capitales des pays nordiques est Copenhague,
            Sophie adore les films de science-fiction comme Star Wars,
            Les fromages français célèbres,
            Jean a remporté la médaille d'or en athlétisme dans ces compétitions : les Jeux olympiques de 2012, le championnat d'Europe 2014 et les Mondiaux de 2015,
            Le Mont-Blanc, situé dans les Alpes, est la plus haute montagne d'Europe occidentale avec une altitude de 4 807 mètres"""

        try:
            # Appel à l'API externe avec la clé d'API
            reponse = requests.post(f"{url}?key={api_key}", 
                json={"contents": [{"parts": [{"text": texte}]}]}, 
                headers={"Content-Type": "application/json", "Accept": "application/json"})

            # Si la requête réussit (code 200), on retourne les données
            if reponse.status_code == 200:
                return jsonify(reponse.json())
            else:
                return jsonify({"error": "Erreur lors de l'appel à l'API externe", "status_code": reponse.status_code})

        except requests.exceptions.RequestException as e:
            # Si une exception survient, on la gère et on retourne un message d'erreur
            return jsonify({"error": "Erreur lors de l'appel à l'API externe", "message": str(e)})

    else:
        return jsonify({"message": "Code utilisateur non valide"})

@app.route('/Generer', methods=['POST'])
def Generer():
    data = request.get_json()
    texte = data.get("texte", "")
    codeUtilisateur = request.args.get('cookie')
    if codeUtilisateur in codes:
        prompt_texte = f"""Génère moi un JSON avec une question, 1 bonne réponse et 3 mauvaises réponses à partir du texte suivant : "{texte}"
                       sous le forme {{question: 'question'}}, {{bonneReponse: 'bonne réponse'}}, {{mauvaiseReponse1: 'mauvaise réponse 1'}},
                       {{mauvaiseReponse2: 'mauvaise réponse 2'}}, {{mauvaiseReponse3: 'mauvaise réponse 3'}}"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt_texte
                        },
                    ],
                },
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        reponse = requests.post(f"{url}?key={api_key}", json=payload, headers=headers)

        if reponse.status_code == 200:
            return jsonify(reponse.json())
    else:
        return jsonify({"error"})
    
@app.route('/Supprimer', methods=['GET'])
def Supprimer():
    codeUtilisateur = request.args.get('cookie')
    if codeUtilisateur in codes:
        codes.remove(codeUtilisateur)
        return jsonify({"message": "Code supprimé avec succès"}), 200
    else:
        return jsonify({"error": "Code non trouvé"}), 404

@app.route('/Score', methods=['POST'])
def Score():
    try:
        data = request.get_json()
        reponseUtilisateur = data.get("reponse","")
        pseudo = data.get("pseudo","")
        idPartie = data.get("valeur","")
        compteur = data.get("compteur","")
        timer = data.get("timer","")
        token = data.get("token","")
        uid = data.get("uid","")
        
        if all([timer, reponseUtilisateur, pseudo, idPartie, compteur, token, uid]):
            ref = db.reference(f'/{idPartie}/question_reponse/{compteur}')
            data = ref.get()
            bonneReponse = data.get('reponse1')
            if bonneReponse == reponseUtilisateur :
                verification = auth.verify_id_token(token)
                if verification['uid'] != uid:
                    return jsonify({"error": "UID et token ne correspondent pas."}), 403
                else:
                    try:
                        scoreJoueur = firestore_db.collection(idPartie).document("score").get().to_dict().get(pseudo, "Le joueur n'a pas de score")  
                        if scoreJoueur == "Le joueur n'a pas de score" :
                            data = {
                                pseudo: 100+timer,
                            }
                            firestore_db.collection(idPartie).document("score").update(data)
                            return jsonify({"message": "score mise à jour"}), 200
                        else:
                            data = {
                                pseudo: scoreJoueur + 100 + timer,
                            }
                            firestore_db.collection(idPartie).document("score").update(data)
                            return jsonify({"message": "score mise à jour"}), 200
                    except Exception as e:
                        data = {
                            pseudo: 100 + timer,
                        }
                        firestore_db.collection(idPartie).document("score").set(data)
                        return jsonify({"message": "score mise à jour"}), 200                   
            else:
                return jsonify({"message": "score mise à jour"}), 200  
        else:
            print("tous les champs ne sont pas remplie")

    except Exception as e:
        return jsonify({"error": f"Erreur de connexion à la base de données : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
