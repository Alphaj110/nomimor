# No Mimor

No Mimor est une application Streamlit de jeux de groupe et de débats.
Elle propose des cartes aléatoires, un mode Action/Vérité, un mode Tu préfères,
des devinettes, un mode Débat avec attribution de rôles et timer, ainsi qu'une
interface thématisable.

## Sommaire

- Présentation
- Fonctionnalités
- Stack technique
- Prérequis
- Installation
- Lancement
- Utilisation
- Structure du projet
- Format des données (`questions.json`)
- Personnalisation
- Dépannage

## Présentation

L'application est pensée pour les soirées, jeux entre amis et sessions de débat.
Le contenu est piloté par un fichier JSON externe, ce qui permet d'ajouter ou
modifier les questions sans toucher au code principal.

## Fonctionnalités

### 1) Mode Débat

- Génération aléatoire d'un sujet.
- Attribution automatique des rôles POUR / CONTRE.
- Bouton pour relancer un sujet.
- Bouton pour mélanger les rôles.
- Timer configurable (1 à 30 minutes) avec progression en direct.

### 2) Mode Jeu

- Action et Vérités : tirage aléatoire entre une carte Action ou une carte Vérité.
- Tu préfères : questions binaires pour lancer la discussion.
- Devinettes : question + possibilité d'afficher/masquer la réponse.
- Anti-répétition simple : évite de tirer immédiatement la même carte.

### 3) Interface

- Thèmes visuels (Barbie, Clair, Dark, Sunset, Menthe).
- Page d'accueil avec logo et présentation détaillée des modes.
- Footer global avec copyright, auteur et lien de contact.
- Design responsive desktop/mobile.

## Stack technique

- Python
- Streamlit
- JSON pour le contenu dynamique

## Prérequis

- Python 3.10 ou plus
- pip

## Installation

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

Puis ouvre l'URL affichée par Streamlit (en général http://localhost:8501).

## Utilisation

1. Ouvre l'application.
2. Choisis un thème dans la barre latérale.
3. Va sur Accueil, Débat ou Jeu.
4. En mode Jeu :
	 - choisis un type,
	 - clique sur Nouvelle carte,
	 - lis la nature de la carte (Action/Vérité/catégorie), puis le contenu.
5. En mode Débat :
	 - clique sur Nouveau débat,
	 - mélange les rôles si nécessaire,
	 - démarre le timer.

## Structure du projet

- `app.py` : application Streamlit (UI, logique, styles, navigation).
- `questions.json` : contenu des cartes et sujets de débat.
- `logo.png` : logo utilisé sur l'accueil.
- `requirements.txt` : dépendances Python.
- `README.md` : documentation projet.

## Format des données (`questions.json`)

Le fichier contient deux blocs principaux :

- `debate_questions` : tableau de sujets de débat.
- `game_content` : objet avec catégories de cartes.

Exemple de structure :

```json
{
	"debate_questions": ["Question 1", "Question 2"],
	"game_content": {
		"Actions": ["Action 1"],
		"Vérités": ["Vérité 1"],
		"Tu préfères": ["Tu préfères ..."],
		"Devinettes": ["Question (Réponse)"]
	}
}
```

Notes importantes :

- Pour les devinettes, le format attendu est `Question (Réponse)`.
- Le mode `Action et Vérités` s'appuie sur `Actions` et `Vérités`.
- Un fallback `Verites` (sans accent) est aussi géré côté code.

## Personnalisation

### Modifier les questions

Édite directement `questions.json` puis relance/refraîchis l'app.

### Modifier le nom de l'application

Met à jour le titre dans `app.py` (configuration Streamlit et textes visibles).

### Modifier le logo

Remplace `logo.png` en conservant le même nom (ou adapte le chemin dans `app.py`).

### Modifier les thèmes

Les presets de thèmes se trouvent dans la fonction `load_theme_presets()`.

## Dépannage

### 1) Le JSON est invalide

Vérifie avec :

```bash
python -m json.tool questions.json
```

### 2) Erreur de syntaxe Python

Vérifie avec :

```bash
python -m py_compile app.py
```

### 3) Problème de dépendances

Réinstalle les paquets :

```bash
pip install -r requirements.txt
```

### 4) L'app ne se met pas à jour

Arrête et relance Streamlit :

```bash
streamlit run app.py
```
