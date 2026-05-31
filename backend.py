

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# =========================
# CONFIGURATION CORS
# =========================
# Permet au frontend Hostinger
# d'accéder à l'API.
# Remplace le domaine plus tard.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# OPENAI
# =========================
# La clé API doit être définie
# dans les variables d'environnement.

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# MODELE DE REQUÊTE
# =========================

class RecipeRequest(BaseModel):
    ingredients: list[str]


# =========================
# ROUTE TEST
# =========================
# Permet de vérifier si
# le backend fonctionne.

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "CookMate backend actif"
    }


# =========================
# ROUTE GENERATION IA
# =========================

@app.post("/generate")
def generate_recipe(data: RecipeRequest):

    ingredients_text = ", ".join(data.ingredients)

    prompt = f"""
Tu es un chef cuisinier professionnel.

Crée UNE recette réaliste et simple.

Règles importantes :
- Utilise principalement les ingrédients fournis
- Tu peux ajouter uniquement des ingrédients basiques
  comme sel, poivre, huile, eau ou épices
- N'invente pas des ingrédients complexes
- La recette doit être logique
- Réponse en français
- Étapes courtes et claires

Ingrédients disponibles :
{ingredients_text}

Format EXACT attendu :

Titre: ...
Temps: ...
Difficulté: ...
Description: ...
Étapes:
1. ...
2. ...
3. ...
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant culinaire précis et réaliste."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=500
    )

    recipe = response.choices[0].message.content

    return {
        "success": True,
        "ingredients": data.ingredients,
        "recipe": recipe
    }


# =========================
# LANCEMENT LOCAL
# =========================
# Permet de tester facilement.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )