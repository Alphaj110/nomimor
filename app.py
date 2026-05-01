import json
import random
import re
import base64
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
import streamlit as st


# -----------------------------
# Data
# -----------------------------

QUESTIONS_FILE = Path(__file__).with_name("questions.json")
LOGO_FILE = Path(__file__).with_name("logo.png")


def load_questions_data() -> dict:
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def load_debate_questions() -> list[str]:
    data = load_questions_data()
    return data.get("debate_questions", [])


def load_game_content() -> dict[str, list[str]]:
    data = load_questions_data()
    return data.get("game_content", {})


def load_intensity_cache() -> dict:
    """Load pre-calculated card intensity scores from cache"""
    cache_file = Path(__file__).with_name("intensity_cache.json")
    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"scores": {}}


# Cache loaded once at startup
INTENSITY_CACHE = load_intensity_cache()


def load_game_modes() -> dict[str, dict[str, list[str]]]:
    game_content = load_game_content()
    game_modes: dict[str, dict[str, list[str]]] = {"Etincelle": {}, "Flamme": {}}

    for category, cards in game_content.items():
        basic_cards: list[str] = []
        intense_cards: list[str] = []

        for card in cards:
            if is_intense_game_card(category, card):
                intense_cards.append(card)
            else:
                basic_cards.append(card)

        game_modes["Etincelle"][category] = basic_cards
        game_modes["Flamme"][category] = intense_cards

    return game_modes


def normalize_text_for_regex(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def score_card_intensity(category: str, card_text: str) -> int:
    """Score a card's intensity from 1-10 based on textual criteria.
    1-4.9: Étincelle (light), 5-10: Flamme (intense)"""
    text = normalize_text_for_regex(f"{category} {card_text}")
    score = 1
    
    scoring_criteria = [
        (r"sexe|sexuel|sexting|threesome|orgas|fantasm|kink|porn|film\s*x", 9),
        (r"couch|faire\s+l'amour|plan\s+cul|coucher|position\w*|toy|dildo|vibr", 8),
        (r"strip|twerk|nudite|nus|nu\s", 7),
        (r"baiser|embrass|kiss|lech|suce|caresse|touche|massage|proximite|enlev", 6),
        (r"seduct|flirt|coquin|sensuel|hot|attir|tendre|romant|charme|amour|crush|date|rendez", 4),
        (r"fais|pratique", 4),
        (r"secret|confession|honte|genant|embarrass|regret|mensonge", 3),
        (r"compliment|sympath|blague|rire|drole|hilarant|rigolo", 1),
    ]
    
    for pattern, points in scoring_criteria:
        if re.search(pattern, text):
            score = max(score, points)
    
    if len(card_text) > 120:
        score += 1
    if "ou" in text and "?" in text:
        score = max(1, score - 1)
    
    return min(10, max(1, score))


def get_game_mode_content(mode_name: str) -> dict[str, list[str]]:
    game_modes = load_game_modes()
    if mode_name in game_modes:
        return game_modes[mode_name]
    return load_game_content()


def resolve_game_intensity_choice(choice: str, category: str) -> str:
    if choice != "Aléatoire":
        return choice

    available_modes = [mode_name for mode_name in ("Etincelle", "Flamme") if get_game_mode_content(mode_name).get(category)]
    if available_modes:
        return random.choice(available_modes)
    return random.choice(["Etincelle", "Flamme"])


def is_intense_game_card(category: str, card_text: str) -> bool:
    """A card is intense (Flamme) if its score is 5 or higher.
    Uses pre-calculated scores from intensity_cache.json"""
    if category in INTENSITY_CACHE.get("scores", {}):
        score = INTENSITY_CACHE["scores"][category].get(card_text)
        if score is not None:
            return score >= 5
    # Fallback if not in cache
    return score_card_intensity(category, card_text) >= 5


def load_theme_presets() -> dict[str, dict[str, str]]:
    return {
        "Barbie": {
            "pink_main": "#FF69B4",
            "pink_light": "#FFC0CB",
            "soft_accent": "#D7B8FF",
            "white": "#FFFFFF",
            "text_dark": "#5A245C",
            "bg_a": "#fff8fc",
            "bg_b": "#ffeef8",
            "title": "#c21883",
            "sidebar_a": "#ffd8eb",
            "sidebar_b": "#f3ddff",
            "button_a": "#ff4fa3",
            "button_b": "#ff8fc8",
            "role_pour_a": "#ff4fa3",
            "role_pour_b": "#ff69b4",
            "role_contre_a": "#b38bff",
            "role_contre_b": "#9d6dff",
            "card_border": "rgba(255, 105, 180, 0.28)",
            "card_shadow": "rgba(255, 105, 180, 0.14)",
            "card_surface": "rgba(255, 255, 255, 0.88)",
            "question_surface": "linear-gradient(135deg, #fff, var(--pink-light))",
            "hero_surface": "linear-gradient(135deg, var(--pink-light), var(--white))",
            "home_surface": "linear-gradient(180deg, var(--white), var(--pink-light))",
            "footer_surface": "rgba(255, 255, 255, 0.9)",
            "question_text": "#7a2a67",
            "small_note": "#8a5d8f",
            "sidebar_text": "#6e2b71",
        },
        "Clair": {
            "pink_main": "#2A8BF2",
            "pink_light": "#CFE8FF",
            "soft_accent": "#9AD5CA",
            "white": "#FFFFFF",
            "text_dark": "#133554",
            "bg_a": "#f8fbff",
            "bg_b": "#eef6ff",
            "title": "#1565c0",
            "sidebar_a": "#e9f4ff",
            "sidebar_b": "#e7f7f3",
            "button_a": "#2A8BF2",
            "button_b": "#4DA4FF",
            "role_pour_a": "#2A8BF2",
            "role_pour_b": "#4DA4FF",
            "role_contre_a": "#32B29D",
            "role_contre_b": "#5CC6B5",
            "card_border": "rgba(42, 139, 242, 0.22)",
            "card_shadow": "rgba(42, 139, 242, 0.12)",
            "card_surface": "rgba(255, 255, 255, 0.88)",
            "question_surface": "linear-gradient(135deg, #fff, var(--pink-light))",
            "hero_surface": "linear-gradient(135deg, var(--pink-light), var(--white))",
            "home_surface": "linear-gradient(180deg, var(--white), var(--pink-light))",
            "footer_surface": "rgba(255, 255, 255, 0.9)",
            "question_text": "#1f4f78",
            "small_note": "#4f708f",
            "sidebar_text": "#1e4c72",
        },
        "Dark": {
            "pink_main": "#FF4FB0",
            "pink_light": "#4A2D63",
            "soft_accent": "#7C4DFF",
            "white": "#1F1A2B",
            "text_dark": "#F4E9FF",
            "bg_a": "#15111F",
            "bg_b": "#22172E",
            "title": "#ff8fd2",
            "sidebar_a": "#261A36",
            "sidebar_b": "#1E142B",
            "button_a": "#FF4FB0",
            "button_b": "#C75CFF",
            "role_pour_a": "#FF4FB0",
            "role_pour_b": "#F95D9B",
            "role_contre_a": "#7C4DFF",
            "role_contre_b": "#5F87FF",
            "card_border": "rgba(255, 79, 176, 0.28)",
            "card_shadow": "rgba(124, 77, 255, 0.22)",
            "card_surface": "rgba(28, 22, 39, 0.94)",
            "question_surface": "linear-gradient(135deg, rgba(42, 30, 60, 0.96), rgba(66, 39, 92, 0.96))",
            "hero_surface": "linear-gradient(135deg, rgba(42, 30, 60, 0.96), rgba(66, 39, 92, 0.96))",
            "home_surface": "linear-gradient(180deg, rgba(28, 22, 39, 0.96), rgba(43, 28, 60, 0.96))",
            "footer_surface": "rgba(25, 18, 34, 0.94)",
            "question_text": "#f5ddff",
            "small_note": "#eadcff",
            "sidebar_text": "#f0ddff",
        },
        "Sunset": {
            "pink_main": "#FF7A59",
            "pink_light": "#FFD2C7",
            "soft_accent": "#FFC95C",
            "white": "#FFFFFF",
            "text_dark": "#5A2C1D",
            "bg_a": "#fff8f4",
            "bg_b": "#ffeedd",
            "title": "#d85835",
            "sidebar_a": "#ffe4d7",
            "sidebar_b": "#ffeecf",
            "button_a": "#FF7A59",
            "button_b": "#FFA24A",
            "role_pour_a": "#FF7A59",
            "role_pour_b": "#FF9A6B",
            "role_contre_a": "#F3A833",
            "role_contre_b": "#FFCA62",
            "card_border": "rgba(255, 122, 89, 0.24)",
            "card_shadow": "rgba(255, 122, 89, 0.14)",
            "card_surface": "rgba(255, 255, 255, 0.88)",
            "question_surface": "linear-gradient(135deg, #fff, var(--pink-light))",
            "hero_surface": "linear-gradient(135deg, var(--pink-light), var(--white))",
            "home_surface": "linear-gradient(180deg, var(--white), var(--pink-light))",
            "footer_surface": "rgba(255, 255, 255, 0.9)",
            "question_text": "#724230",
            "small_note": "#8b5d4b",
            "sidebar_text": "#6f3f2d",
        },
        "Menthe": {
            "pink_main": "#2DBE9D",
            "pink_light": "#C8F2E9",
            "soft_accent": "#7CC7B9",
            "white": "#FFFFFF",
            "text_dark": "#184A43",
            "bg_a": "#f5fffc",
            "bg_b": "#eafbf5",
            "title": "#169a7d",
            "sidebar_a": "#dcf7f0",
            "sidebar_b": "#d7f2e6",
            "button_a": "#2DBE9D",
            "button_b": "#34D1AE",
            "role_pour_a": "#2DBE9D",
            "role_pour_b": "#34D1AE",
            "role_contre_a": "#4EA5B8",
            "role_contre_b": "#68B9CB",
            "card_border": "rgba(45, 190, 157, 0.22)",
            "card_shadow": "rgba(45, 190, 157, 0.12)",
            "card_surface": "rgba(255, 255, 255, 0.88)",
            "question_surface": "linear-gradient(135deg, #fff, var(--pink-light))",
            "hero_surface": "linear-gradient(135deg, var(--pink-light), var(--white))",
            "home_surface": "linear-gradient(180deg, var(--white), var(--pink-light))",
            "footer_surface": "rgba(255, 255, 255, 0.9)",
            "question_text": "#25665a",
            "small_note": "#4d7e74",
            "sidebar_text": "#215f54",
        },
    }


# -----------------------------
# Logic helpers
# -----------------------------

def get_random_item(items: list[str], previous_item: str | None = None) -> str:
    if not items:
        return "Aucun contenu disponible."
    if len(items) == 1:
        return items[0]

    candidate = random.choice(items)
    while candidate == previous_item:
        candidate = random.choice(items)
    return candidate


def assign_roles() -> tuple[str, str]:
    role_j1 = random.choice(["POUR", "CONTRE"])
    role_j2 = "CONTRE" if role_j1 == "POUR" else "POUR"
    return role_j1, role_j2


def split_devinette_card(card_text: str) -> tuple[str, str | None]:
    match = re.match(r"^(.*)\(([^()]*)\)\s*$", card_text)
    if not match:
        return card_text, None
    prompt = match.group(1).strip()
    answer = match.group(2).strip()
    return prompt, answer if prompt and answer else None


def normalize_initials(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", value).upper().strip()
    return (cleaned[:4] or fallback)


def render_animated_logo() -> None:
    if not LOGO_FILE.exists():
        st.warning("Logo introuvable: logo.png")
        return

    encoded_logo = base64.b64encode(LOGO_FILE.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div class='logo-heartbeat-wrap'>
            <img src='data:image/png;base64,{encoded_logo}' class='logo-heartbeat' alt='Logo No Mimor'>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Styles
# -----------------------------

def inject_base_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Quicksand:wght@400;600;700&display=swap');

            :root {
                --pink-main: #FF69B4;
                --pink-light: #FFC0CB;
                --soft-accent: #D7B8FF;
                --white: #FFFFFF;
                --text-dark: #5A245C;
                --bg-a: #fff8fc;
                --bg-b: #ffeef8;
                --title: #c21883;
                --sidebar-a: #ffd8eb;
                --sidebar-b: #f3ddff;
                --button-a: #ff4fa3;
                --button-b: #ff8fc8;
                --role-pour-a: #ff4fa3;
                --role-pour-b: #ff69b4;
                --role-contre-a: #b38bff;
                --role-contre-b: #9d6dff;
                --card-border: rgba(255, 105, 180, 0.28);
                --card-shadow: rgba(255, 105, 180, 0.14);
                --question-text: #7a2a67;
                --small-note: #8a5d8f;
                --sidebar-text: #6e2b71;
            }

            .stApp {
                background:
                    radial-gradient(circle at 10% 20%, rgba(255, 105, 180, 0.18) 0, rgba(255, 105, 180, 0) 35%),
                    radial-gradient(circle at 90% 15%, var(--soft-accent) 0, transparent 32%),
                    linear-gradient(160deg, var(--bg-a), var(--bg-b));
                background-size: 100% 100%, 110% 110%, 180% 180%;
                color: var(--text-dark);
                font-family: 'Quicksand', sans-serif;
                animation: bgDrift 18s ease-in-out infinite;
            }

            h1, h2, h3 {
                font-family: 'Baloo 2', cursive;
                color: var(--title);
                letter-spacing: 0.4px;
            }

            .main-card {
                background: var(--card-surface);
                border: 1px solid var(--card-border);
                border-radius: 18px;
                padding: 1.2rem 1rem;
                box-shadow: 0 10px 30px var(--card-shadow);
                animation: floatIn 0.5s ease-out;
                transition: transform 0.28s ease, box-shadow 0.28s ease;
            }

            .main-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 14px 34px var(--card-shadow);
            }

            .question-box {
                border-radius: 16px;
                background: var(--question-surface);
                padding: 1rem;
                border-left: 8px solid var(--pink-main);
                font-size: 1.1rem;
                color: var(--question-text);
                animation: softFadeUp 0.65s ease-out;
                transition: transform 0.22s ease, box-shadow 0.22s ease;
            }

            .question-box:hover {
                transform: translateY(-1px);
                box-shadow: 0 8px 18px var(--card-shadow);
            }

            .role-pill {
                display: inline-block;
                padding: 0.35rem 0.8rem;
                border-radius: 999px;
                font-weight: 700;
                color: #fff;
                margin-left: 0.4rem;
                animation: popIn 0.4s ease-out;
            }

            .role-pour {
                background: linear-gradient(135deg, var(--role-pour-a), var(--role-pour-b));
            }

            .role-contre {
                background: linear-gradient(135deg, var(--role-contre-a), var(--role-contre-b));
            }

            .small-note {
                font-size: 0.92rem;
                color: var(--small-note);
            }

            div[data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--sidebar-a), var(--sidebar-b));
                border-right: 2px solid rgba(255, 105, 180, 0.25);
            }

            div[data-testid="stSidebar"] * {
                color: var(--sidebar-text);
            }

            .stButton > button {
                position: relative;
                overflow: hidden;
                border: none;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--button-a), var(--button-b));
                color: #fff;
                font-weight: 700;
                padding: 0.55rem 1.1rem;
                transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
                box-shadow: 0 6px 18px var(--card-shadow);
            }

            .stButton > button:hover {
                transform: translateY(-3px) scale(1.04);
                box-shadow: 0 12px 28px var(--card-shadow);
                filter: saturate(1.12) brightness(1.05);
            }

            .stButton > button:active {
                transform: translateY(-1px) scale(0.98);
            }

            .home-hero {
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-bottom: 1.5rem;
                background: var(--hero-surface);
                border: 1px solid var(--card-border);
                animation: softFadeUp 0.65s ease-out;
            }

            .home-card {
                border-radius: 16px;
                padding: 1rem;
                border: 1px solid var(--card-border);
                background: var(--home-surface);
                box-shadow: 0 8px 20px var(--card-shadow);
                height: 100%;
                animation: softFadeUp 0.75s ease-out;
                transition: transform 0.24s ease, box-shadow 0.24s ease;
                margin-bottom: 1.8rem;
            }

            .home-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 14px 28px var(--card-shadow);
            }

            .logo-heartbeat-wrap {
                display: flex;
                justify-content: center;
                margin-bottom: 0.5rem;
            }

            .logo-heartbeat {
                width: 100%;
                max-width: 300px;
                animation: logoHeartbeat 1.25s ease-in-out infinite;
                transform-origin: center;
                will-change: transform;
            }

            .theme-chip {
                display: inline-block;
                padding: 0.2rem 0.65rem;
                border-radius: 999px;
                background: var(--pink-light);
                color: var(--text-dark);
                font-size: 0.85rem;
                font-weight: 700;
                animation: popIn 0.5s ease-out;
                transition: transform 0.2s ease;
            }

            .theme-chip:hover {
                transform: translateY(-1px);
            }

            .app-footer {
                position: fixed;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 999;
                padding: 0.55rem 0.8rem;
                border-top: 1px solid var(--card-border);
                background: var(--footer-surface);
                backdrop-filter: blur(6px);
                text-align: center;
                font-size: 0.84rem;
                line-height: 1.45;
                color: var(--small-note);
                animation: footerSlideIn 0.65s ease-out;
                transition: background 0.25s ease;
            }

            .app-footer strong {
                color: var(--text-dark);
            }

            .app-footer .dot {
                margin: 0 0.35rem;
                opacity: 0.65;
            }

            div[data-testid="stAppViewContainer"] .main .block-container {
                padding-bottom: 5.2rem;
            }

            .app-footer a {
                color: var(--title);
                font-weight: 700;
                text-decoration: none;
            }

            .app-footer a:hover {
                text-decoration: underline;
            }

            @media (max-width: 900px) {
                .main-card {
                    padding: 1rem 0.8rem;
                }

                .question-box {
                    font-size: 1rem;
                }

                .home-card {
                    margin-bottom: 0.7rem;
                }

                .logo-heartbeat {
                    max-width: 240px;
                }

                .theme-chip {
                    font-size: 0.78rem;
                }

                .app-footer {
                    font-size: 0.76rem;
                    padding: 0.5rem 0.55rem;
                }

                div[data-testid="stAppViewContainer"] .main .block-container {
                    padding-bottom: 6rem;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                .stApp,
                .main-card,
                .question-box,
                .role-pill,
                .home-hero,
                .home-card,
                .theme-chip,
                .app-footer,
                .logo-heartbeat {
                    animation: none !important;
                    transition: none !important;
                }
            }

            @keyframes bgDrift {
                0% { background-position: 0% 0%, 100% 0%, 0% 50%; }
                50% { background-position: 2% 2%, 98% 2%, 100% 50%; }
                100% { background-position: 0% 0%, 100% 0%, 0% 50%; }
            }

            @keyframes softFadeUp {
                from { opacity: 0; transform: translateY(22px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes footerSlideIn {
                from { opacity: 0; transform: translateY(18px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes floatIn {
                from { opacity: 0; transform: translateY(12px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes popIn {
                from { opacity: 0; transform: scale(0.82); }
                to { opacity: 1; transform: scale(1); }
            }

            @keyframes logoHeartbeat {
                0% { transform: scale(1); }
                14% { transform: scale(1.025); }
                28% { transform: scale(1.05); }
                42% { transform: scale(1.025); }
                100% { transform: scale(1); }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_theme_variables(theme: dict[str, str]) -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --pink-main: {theme['pink_main']};
                --pink-light: {theme['pink_light']};
                --soft-accent: {theme['soft_accent']};
                --white: {theme['white']};
                --text-dark: {theme['text_dark']};
                --bg-a: {theme['bg_a']};
                --bg-b: {theme['bg_b']};
                --title: {theme['title']};
                --sidebar-a: {theme['sidebar_a']};
                --sidebar-b: {theme['sidebar_b']};
                --button-a: {theme['button_a']};
                --button-b: {theme['button_b']};
                --role-pour-a: {theme['role_pour_a']};
                --role-pour-b: {theme['role_pour_b']};
                --role-contre-a: {theme['role_contre_a']};
                --role-contre-b: {theme['role_contre_b']};
                --card-border: {theme['card_border']};
                --card-shadow: {theme['card_shadow']};
                --card-surface: {theme['card_surface']};
                --question-surface: {theme['question_surface']};
                --hero-surface: {theme['hero_surface']};
                --home-surface: {theme['home_surface']};
                --footer-surface: {theme['footer_surface']};
                --question-text: {theme['question_text']};
                --small-note: {theme['small_note']};
                --sidebar-text: {theme['sidebar_text']};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Session state
# -----------------------------

def init_session_state() -> None:
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = "Barbie"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"
    if "debate_question" not in st.session_state:
        st.session_state.debate_question = random.choice(load_debate_questions())
    if "role_j1" not in st.session_state or "role_j2" not in st.session_state:
        st.session_state.role_j1, st.session_state.role_j2 = assign_roles()
    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_duration_sec" not in st.session_state:
        st.session_state.timer_duration_sec = 60
    if "game_intensity_choice" not in st.session_state:
        st.session_state.game_intensity_choice = "Etincelle"
    if "game_mode_choice" not in st.session_state:
        st.session_state.game_mode_choice = None
    if "game_pick" not in st.session_state:
        st.session_state.game_pick = {
            "category": None,
            "content": "Choisis un type puis clique sur 'Nouvelle carte'.",
            "answer": None,
        }
    if "game_reveal_answer" not in st.session_state:
        st.session_state.game_reveal_answer = False
    if "player1_initials" not in st.session_state:
        st.session_state.player1_initials = "J"
    if "player2_initials" not in st.session_state:
        st.session_state.player2_initials = "S"
    if "played_cards" not in st.session_state:
        st.session_state.played_cards = {"Etincelle": [], "Flamme": []}
    if "cards_drawn_count" not in st.session_state:
        st.session_state.cards_drawn_count = 0
    if "current_intensity_score" not in st.session_state:
        st.session_state.current_intensity_score = 2


# -----------------------------
# Debate mode
# -----------------------------

def start_debate_timer(minutes: int) -> None:
    duration = max(1, minutes) * 60
    st.session_state.timer_duration_sec = duration
    st.session_state.timer_end = datetime.now() + timedelta(seconds=duration)


def reset_debate_timer() -> None:
    st.session_state.timer_end = None


def render_timer() -> None:
    st.subheader("Timer du Mind date")
    col_a, col_b, col_c = st.columns([1.2, 1, 1])
    with col_a:
        minutes = st.number_input(
            "Durée (minutes)",
            min_value=1,
            max_value=30,
            value=max(1, st.session_state.timer_duration_sec // 60),
            step=1,
        )
    with col_b:
        if st.button("Démarrer", use_container_width=True):
            start_debate_timer(minutes)
    with col_c:
        if st.button("Réinitialiser", use_container_width=True):
            reset_debate_timer()

    if st.session_state.timer_end is None:
        st.markdown("<p class='small-note'>Le timer est en pause.</p>", unsafe_allow_html=True)
        return

    remaining = int((st.session_state.timer_end - datetime.now()).total_seconds())
    total = max(1, st.session_state.timer_duration_sec)
    if remaining <= 0:
        st.success("Temps écoulé ! Fin du Mind date")
        st.session_state.timer_end = None
        st.progress(1.0)
        return

    mins, secs = divmod(remaining, 60)
    st.info(f"Temps restant : {mins:02d}:{secs:02d}")
    st.progress(max(0.0, min(1.0, 1 - (remaining / total))))


def render_debat_mode() -> None:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.header("Mode Mind date")
    st.markdown("<p class='small-note'>Choisis un sujet, prends position et défends tes idées.</p>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("Nouveau Mind date", use_container_width=True):
            questions = load_debate_questions()
            st.session_state.debate_question = get_random_item(questions, st.session_state.debate_question)
    with col_right:
        if st.button("Mélanger les rôles", use_container_width=True):
            st.session_state.role_j1, st.session_state.role_j2 = assign_roles()

    st.markdown(
        f"""
        <div class='question-box'>
            <strong>Sujet du Mind date :</strong><br>
            {st.session_state.debate_question}
        </div>
        """,
        unsafe_allow_html=True,
    )

    role_col_1, role_col_2 = st.columns(2)
    with role_col_1:
        role_class = "role-pour" if st.session_state.role_j1 == "POUR" else "role-contre"
        st.markdown(f"{st.session_state.player1_initials} : <span class='role-pill {role_class}'>{st.session_state.role_j1}</span>", unsafe_allow_html=True)
    with role_col_2:
        role_class = "role-pour" if st.session_state.role_j2 == "POUR" else "role-contre"
        st.markdown(f"{st.session_state.player2_initials} : <span class='role-pill {role_class}'>{st.session_state.role_j2}</span>", unsafe_allow_html=True)

    st.markdown("---")
    render_timer()
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Game mode
# -----------------------------

def get_card_intensity_score(category: str, card_text: str) -> int:
    """Get pre-calculated intensity score from cache, fallback to calculation"""
    if category in INTENSITY_CACHE.get("scores", {}):
        score = INTENSITY_CACHE["scores"][category].get(card_text)
        if score is not None:
            return score
    # Fallback if not in cache (shouldn't happen if cache is complete)
    return score_card_intensity(category, card_text)


def roll_game_content(intensity: str, category: str) -> None:
    """Draw a card, progressing in intensity and avoiding recent repeats."""
    resolved_intensity = resolve_game_intensity_choice(intensity, category)
    game_data = get_game_mode_content(resolved_intensity)
    
    st.session_state.cards_drawn_count += 1
    st.session_state.current_intensity_score = min(10, 2 + (st.session_state.cards_drawn_count // 3))

    if category == "Action et Vérités":
        actions = game_data.get("Actions", [])
        truths = game_data.get("Vérités", game_data.get("Verites", []))

        pools: list[tuple[str, list[str]]] = []
        if actions:
            pools.append(("Action", actions))
        if truths:
            pools.append(("Vérité", truths))

        if not pools:
            st.session_state.game_pick = {
                "category": "Action / Vérité",
                "content": "Aucune carte Action ou Vérité disponible.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False
            return

        nature, pool = random.choice(pools)
        available = [
            card for card in pool
            if card not in st.session_state.played_cards.get(resolved_intensity, [])
            and abs(get_card_intensity_score(nature, card) - st.session_state.current_intensity_score) <= 2
        ]
        
        if not available:
            available = [c for c in pool if c not in st.session_state.played_cards.get(resolved_intensity, [])]
        if not available:
            available = pool
            
        selected = random.choice(available)
        st.session_state.game_pick = {
            "category": nature,
            "content": selected,
            "answer": None,
        }
        st.session_state.played_cards[resolved_intensity].append(selected)
        st.session_state.game_reveal_answer = False
        return

    if category not in game_data:
        return

    pool = game_data[category]
    available = [
        card for card in pool
        if card not in st.session_state.played_cards.get(resolved_intensity, [])
        and abs(get_card_intensity_score(category, card) - st.session_state.current_intensity_score) <= 2
    ]
    
    if not available:
        available = [c for c in pool if c not in st.session_state.played_cards.get(resolved_intensity, [])]
    if not available:
        available = pool
    
    raw_content = random.choice(available)
    visible_content, answer = raw_content, None
    if category == "Devinettes":
        visible_content, answer = split_devinette_card(raw_content)

    st.session_state.game_pick = {
        "category": category,
        "content": visible_content,
        "answer": answer,
    }
    st.session_state.played_cards[resolved_intensity].append(raw_content)
    st.session_state.game_reveal_answer = False


def render_game_choice_buttons() -> None:
    st.subheader("Choisis l'intensité du jeu")
    tone_col1, tone_col2, tone_col3 = st.columns(3)

    with tone_col1:
        if st.button("Etincelle", use_container_width=True):
            st.session_state.game_intensity_choice = "Etincelle"
            st.session_state.game_mode_choice = None
            st.session_state.game_pick = {
                "category": None,
                "content": "Choisis un type puis clique sur 'Nouvelle carte'.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False
    with tone_col2:
        if st.button("Flamme", use_container_width=True):
            st.session_state.game_intensity_choice = "Flamme"
            st.session_state.game_mode_choice = None
            st.session_state.game_pick = {
                "category": None,
                "content": "Choisis un type puis clique sur 'Nouvelle carte'.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False
    with tone_col3:
        if st.button("Aléatoire", use_container_width=True):
            st.session_state.game_intensity_choice = "Aléatoire"
            st.session_state.game_mode_choice = None
            st.session_state.game_pick = {
                "category": None,
                "content": "Choisis un type puis clique sur 'Nouvelle carte'.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False

    st.caption(f"Mode sélectionné : {st.session_state.game_intensity_choice}")
    st.subheader("Choisis le type de jeu")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Action et Vérités", use_container_width=True):
            st.session_state.game_mode_choice = "Action et Vérités"
            st.session_state.game_pick = {
                "category": "Action / Vérité",
                "content": "Clique sur 'Nouvelle carte' pour tirer une Action ou une Vérité.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False
    with col2:
        if st.button("Tu préfères", use_container_width=True):
            st.session_state.game_mode_choice = "Tu préfères"
            st.session_state.game_pick = {
                "category": "Tu préfères",
                "content": "Clique sur 'Nouvelle carte' pour tirer un tu préfères.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False
    with col3:
        if st.button("Devinettes", use_container_width=True):
            st.session_state.game_mode_choice = "Devinettes"
            st.session_state.game_pick = {
                "category": "Devinettes",
                "content": "Clique sur 'Nouvelle carte' pour tirer une devinette.",
                "answer": None,
            }
            st.session_state.game_reveal_answer = False

    st.caption(f"Type sélectionné : {st.session_state.game_mode_choice or 'Aucun'}")


def render_jeu_mode() -> None:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.header("Mode Jeu")
    st.markdown("<p class='small-note'>Choisis d'abord une intensité, puis un type : Action et Vérités, Tu préfères ou Devinettes.</p>", unsafe_allow_html=True)

    render_game_choice_buttons()

    if st.session_state.game_mode_choice is None:
        st.info("Sélectionne un type de jeu pour commencer.")
    else:
        if st.button("Nouvelle carte", use_container_width=True):
            roll_game_content(st.session_state.game_intensity_choice, st.session_state.game_mode_choice)

    pick = st.session_state.game_pick

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("Catégorie")
        st.markdown(f"<div class='question-box'><strong>{pick['category'] or '—'}</strong></div>", unsafe_allow_html=True)
    with col_b:
        st.subheader("Contenu")
        st.markdown(f"<div class='question-box'>{pick['content']}</div>", unsafe_allow_html=True)

        st.caption(f"Intensité active : {st.session_state.game_intensity_choice}")

        if pick.get("category") == "Devinettes" and pick.get("answer"):
            toggle_label = "Masquer la réponse" if st.session_state.game_reveal_answer else "Réponse"
            if st.button(toggle_label, use_container_width=True):
                st.session_state.game_reveal_answer = not st.session_state.game_reveal_answer
            if st.session_state.game_reveal_answer:
                st.success(f"Réponse : {pick['answer']}")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Home
# -----------------------------

def render_home_mode() -> None:
    _, logo_col, _ = st.columns([2, 1.25, 2])
    with logo_col:
        render_animated_logo()

    st.header("Bienvenue sur No Mimor ")
    st.markdown(
        """
        <div class='home-hero'>
            <p class='small-note'>No Mimor est une app de soirée en 2 modes : Mind date pour argumenter avec un timer, et Jeu pour piocher des cartes fun (Actions, Tu préfères, Devinettes).</p>
            <strong>Comment démarrer :</strong> choisis un mode ci-dessous, puis utilise les boutons pour générer un nouveau contenu à chaque tour.
            <br>
            <strong>Personnalisation :</strong> change le thème dans la barre de gauche pour adapter l'ambiance visuelle à ta partie.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            <div class='home-card'>
                <h3><strong>Mind date</strong></h3>
                <p>
                    Génère un sujet Mind date aléatoire, puis attribue automatiquement les rôles <strong>POUR</strong> et <strong>CONTRE</strong> aux joueurs.
                    Utilise le bouton <strong>Nouveau Mind date</strong> pour changer de sujet et <strong>Mélanger les rôles</strong> pour relancer la dynamique.
                    Le timer intégré permet de fixer une durée (1 à 30 min) et de suivre le temps restant en direct.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)
        if st.button("Aller au mode Mind date", use_container_width=True):
            st.session_state.current_page = "Mind date"
            st.rerun()
    with right:
        st.markdown(
            """
            <div class='home-card'>
                <h3><strong>Jeux</strong></h3>
                <p>
                    Choisis une catégorie de cartes selon l'ambiance : <strong>Actions et vérités</strong>, <strong>Tu préfères</strong> ou <strong>Devinettes</strong>.
                    Clique sur <strong>Nouvelle carte</strong> pour piocher un nouveau défi/question, sans répéter la carte précédente.
                    En mode devinette, tu as le pouvoir d'afficher ou masquer la réponse pour laisser les joueurs réfléchir avant la révélation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)
        if st.button("Aller au mode Jeu", use_container_width=True):
            st.session_state.current_page = "Jeu"
            st.rerun()


def render_footer() -> None:
    current_year = datetime.now().year
    st.markdown(
        f"""
        <div class='app-footer'>
            <strong>© {current_year} No Mimor</strong><span class='dot'>•</span>By Jordan<span class='dot'>•</span>Tous droits réservés
            <br>
            Mind date, Jeux & thèmes personnalisables<span class='dot'>•</span>Version 1.0<span class='dot'>•</span>
            <a href='mailto:jordanlokimomo@gmail.com?subject=Contact%20No%20Mimor'>Contact</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# App entry
# -----------------------------

def main() -> None:
    st.set_page_config(page_title="No Mimor", layout="wide", initial_sidebar_state="expanded")
    init_session_state()
    themes = load_theme_presets()

    st.sidebar.title("Navigation")
    if st.sidebar.button("Accueil", use_container_width=True):
        st.session_state.current_page = "Accueil"
    if st.sidebar.button("Débat", use_container_width=True):
        st.session_state.current_page = "Débat"
    if st.sidebar.button("Jeu", use_container_width=True):
        st.session_state.current_page = "Jeu"

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Joueurs")
    
    def normalize_player1():
        st.session_state.player1_initials = normalize_initials(st.session_state.player1_initials, "J")
    
    def normalize_player2():
        st.session_state.player2_initials = normalize_initials(st.session_state.player2_initials, "S")
    
    st.sidebar.text_input("Initiales joueur 1", key="player1_initials", max_chars=4, on_change=normalize_player1)
    st.sidebar.text_input("Initiales joueur 2", key="player2_initials", max_chars=4, on_change=normalize_player2)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Thèmes")
    for theme_name in themes:
        label = f"Actif - {theme_name}" if st.session_state.current_theme == theme_name else theme_name
        if st.sidebar.button(label, key=f"theme_{theme_name}", use_container_width=True):
            st.session_state.current_theme = theme_name

    inject_base_css()
    apply_theme_variables(themes[st.session_state.current_theme])

    st.markdown(f"<span class='theme-chip'>Thème actif : {st.session_state.current_theme}</span>", unsafe_allow_html=True)

    if st.session_state.current_page == "Accueil":
        render_home_mode()
    elif st.session_state.current_page == "Mind date":
        render_debat_mode()
    else:
        render_jeu_mode()

    render_footer()


if __name__ == "__main__":
    main()
