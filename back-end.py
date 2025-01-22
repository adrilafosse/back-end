import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

api_key = os.getenv('API_KEY')  # Accès à la variable d'environnement

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@app.route('/Exemple', methods=['GET'])
def Exemple():
    texte = """Génère moi un JSON contenant 1 nouveau exemple de prompt en t'inspirant de ces 9 exemples :}" :
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

    response = requests.post(f"{url}?key={api_key}", 
        json= {
            "contents": [
                {
                    "parts": [
                        {
                            "text": texte
                        },
                    ],
                },
            ],
        }, 
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error"})

@app.route('/Generer', methods=['POST'])
def Generer():
    data = request.get_json()
    texte = data.get("texte", "")
    
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

    response = requests.post(f"{url}?key={api_key}", json=payload, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error"})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
