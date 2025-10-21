import streamlit as st
import requests
import random
import html
import time
import streamlit.components.v1 as components
import base64
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="High Noon Trivia", page_icon="🤠", layout="wide")

# --- FUNCTION TO SET BACKGROUND ---
# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def get_base64_of_bin_file(bin_file):
    """Reads a binary file and returns its base64 encoded string."""
    if not os.path.exists(bin_file):
        return None
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_app_background(image_file):
    """Injects CSS to set the app background from a local image file."""
    # Create the full, absolute path to the image file
    image_path = os.path.join(SCRIPT_DIR, image_file)
    
    bin_str = get_base64_of_bin_file(image_path)
    if bin_str is None:
        st.error(f"Error: Background image '{image_file}' not found. Attempted to load from: {image_path}")
        st.warning("Please make sure 'c2.jpg' is in the same folder as 'trivia1.py'.")
        return
        
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* --- ADDED: Semi-transparent overlay for brightness reduction --- */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.25); /* 25% black overlay for 75% brightness */
        z-index: -1; /* Place it behind content but above the background image */
    }}
    
    /* Make header/toolbar transparent to show background */
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: none;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- SET THE BACKGROUND ---
set_app_background('c14.jpg')


# --- STYLES, ANIMATIONS, and SOUND SCRIPT ---
CSS_and_JS = """
<style>
/* --- WILD WEST SALOON THEME --- */
/* --- MODIFIED: Changed font to a Western style --- */
@import url('https://fonts.googleapis.com/css2?family=Rye&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700&display=swap');


body {
    background: transparent; /* Make body transparent to see the main background */
    color: #f5eeda;
    /* --- MODIFIED: Set default font --- */
    font-family: 'Roboto Slab', serif;
}

h1 {
    /* --- MODIFIED: Changed font to a Western style --- */
    font-family: 'Rye', cursive;
    font-weight: 700;
    color: #FFFFFF; /* White text for better contrast on image */
    text-shadow: 2px 2px 4px #000000; /* Stronger shadow for readability */
    text-align: center;
    font-size: 3.5rem; /* Made title bigger */
}

h2, h3, h4, h5, h6 {
    color: #F8F8F8; /* Light color for subheaders */
    text-shadow: 1px 1px 2px #000000;
}

.stButton>button {
    border: 2px solid #5a3d24;
    background-color: #6f4e37;
    color: #f5eeda;
    border-radius: 5px;
    padding: 10px 20px;
    font-weight: bold;
    /* --- MODIFIED: Changed font to a Western style for main buttons --- */
    font-family: 'Rye', cursive;
    font-size: 1.1rem;
    transition: all 0.2s ease;
    box-shadow: inset 0 -4px 0 #5a3d24;
    text-shadow: 1px 1px 1px #5a3d24;
}
.stButton>button:hover {
    background-color: #835e42;
    transform: translateY(-2px);
    box-shadow: inset 0 -6px 0 #5a3d24;
}
.stButton>button:active {
    transform: translateY(0);
    box-shadow: inset 0 -2px 0 #5a3d24;
}

/* --- ADDED: Style for HP progress bar --- */
[data-testid="stProgressBar"] > div > div {
    background-image: linear-gradient(to right, #b90000, #ff4c4c);
}


@keyframes shoot-player {
    0% { transform: translateX(0); opacity: 1; }
    80% { transform: translateX(calc(100% + 20px)); opacity: 1; }
    100% { transform: translateX(calc(100% + 50px)); opacity: 0; }
}
@keyframes shoot-bot {
    0% { transform: translateX(0); opacity: 1; }
    80% { transform: translateX(calc(-100% - 20px)); opacity: 1; }
    100% { transform: translateX(calc(-100% - 50px)); opacity: 0; }
}
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-6px); }
    20%, 40%, 60%, 80% { transform: translateX(6px); }
}
@keyframes float-up {
    0% { transform: translateY(0); opacity: 1; }
    100% { transform: translateY(-40px); opacity: 0; }
}

.player-box {
    text-align: center;
    padding: 1rem;
    border-radius: 10px;
    background-color: rgba(245, 238, 218, 0.9);
    color: #3e2e20;
    position: relative;
    border: 4px solid #5a3d24;
    height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: all 0.1s ease-out;
    box-sizing: border-box;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
}
.shaking {
    animation: shake 0.4s ease-in-out;
    border-color: #c0392b;
}

.player-icon {
    font-size: 5rem;
    line-height: 1;
    position: relative;
    z-index: 2;
}

.damage-text {
    position: absolute;
    top: 0px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 1.6rem;
    font-weight: bold;
    color: #c0392b;
    animation: float-up 1s forwards;
    z-index: 10;
    white-space: nowrap;
    text-shadow: 1px 1px 1px rgba(255,255,255,0.5);
}

.bullet {
    font-size: 3rem;
    position: absolute;
    opacity: 0;
    z-index: 3;
    top: 50px;
    color: #3e2e20;
    text-shadow: 1px 1px 2px #FFF;
}
.player-bullet {
    left: 0;
    animation: shoot-player 0.4s ease-out forwards;
}
.bot-bullet {
    right: 0;
    animation: shoot-bot 0.4s ease-out forwards;
}

/* --- ADDED: Styling for Streamlit info/success/warning boxes --- */
.stAlert, .stNotification {
    background-color: rgba(111, 78, 55, 0.9); /* Earthy brown, slightly transparent */
    color: #f5eeda; /* Parchment text */
    border: 2px solid #5a3d24; /* Darker wood border */
    border-radius: 8px;
    padding: 1rem;
    font-weight: bold; /* Make text bold */
    text-shadow: 1px 1px 1px #5a3d24; /* Subtle shadow */
    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
}
.stAlert > div > span, .stNotification > div > span {
    font-weight: bold; /* Ensure content is bold if not already */
}


@media (max-width: 768px) {
    .player-box { height: 150px; }
    .player-icon { font-size: 4rem; }
    h1 { font-size: 2rem; }
}
</style>

<script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.7.77/Tone.js"></script>
<script>
    if (window.synth === undefined) {
        window.synth = new Tone.Synth().toDestination();
        window.noiseSynth = new Tone.NoiseSynth({noise: {type: 'white'}, envelope: {attack: 0.005, decay: 0.1, sustain: 0}}).toDestination();
    }
    function playSound(soundType) {
        if (Tone.context.state !== 'running') { Tone.start(); }
        const now = Tone.now();
        if (soundType === 'clash') { window.synth.triggerAttackRelease("E4", "16n", now); } 
        else if (soundType === 'incorrect') { window.synth.triggerAttackRelease("A2", "8n", now); } 
        else if (soundType === 'impact') { window.noiseSynth.triggerAttackRelease("8n", now); }
    }
</script>
"""
st.markdown(CSS_and_JS, unsafe_allow_html=True)


# --- GAME DATA ---
TOPICS = {
    "Indian History & Culture": "custom",
    "Any Category": 0, "General Knowledge": 9, "Entertainment: Film": 11,
    "Entertainment: Music": 12, "Science & Nature": 17, "Science: Computers": 18,
    "Mythology": 20, "Sports": 21, "Geography": 22, "History": 23,
    "Entertainment: Japanese Anime & Manga": 31,
}

INDIA_QUESTIONS = {
    "easy": [
        {"question": "Which festival is known as the 'Festival of Lights' in India?", "answers": ["Holi", "Diwali", "Eid", "Christmas"], "correct": "Diwali"},
        {"question": "What is the capital city of India?", "answers": ["Mumbai", "Kolkata", "Chennai", "New Delhi"], "correct": "New Delhi"},
        {"question": "Which of these is a famous monument in Agra, India?", "answers": ["Qutub Minar", "Gateway of India", "Taj Mahal", "Hawa Mahal"], "correct": "Taj Mahal"}
    ],
    "medium": [
        {"question": "The 'Dandi March' led by Mahatma Gandhi was a protest against the tax on what?", "answers": ["Salt", "Cotton", "Tea", "Spices"], "correct": "Salt"},
        {"question": "Which Indian festival celebrates the victory of good over evil, culminating in the burning of Ravana's effigy?", "answers": ["Navaratri", "Dussehra", "Makar Sankranti", "Pongal"], "correct": "Dussehra"},
        {"question": "In which state is the festival of 'Onam' predominantly celebrated?", "answers": ["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh"], "correct": "Kerala"}
    ],
    "hard": [
        {"question": "Which Veda is primarily a collection of hymns and is considered one of the oldest sacred texts in the world?", "answers": ["Yajurveda", "Samaveda", "Atharvaveda", "Rigveda"], "correct": "Rigveda"},
        {"question": "The 'Khajuraho Group of Monuments' are famous for their Nagara-style architectural symbolism and are located in which state?", "answers": ["Rajasthan", "Madhya Pradesh", "Uttar Pradesh", "Gujarat"], "correct": "Madhya Pradesh"},
        {"question": "Which Indian classical dance form, originating from Tamil Nadu, is traditionally performed by women?", "answers": ["Kathakali", "Kuchipudi", "Bharatanatyam", "Odissi"], "correct": "Bharatanatyam"}
    ]
}

ROUND_SETTINGS = {
    1: {"name": "Easy", "damage": 15, "bot_accuracy": 0.50, "questions": 3},
    2: {"name": "Medium", "damage": 20, "bot_accuracy": 0.70, "questions": 3},
    3: {"name": "Hard", "damage": 30, "bot_accuracy": 0.85, "questions": 3},
}

# --- API HANDLING ---
def get_new_question(category_id, difficulty):
    if category_id == "custom":
        q_list = INDIA_QUESTIONS.get(difficulty.lower(), [])
        if 'used_custom_questions' not in st.session_state:
            st.session_state.used_custom_questions = []
        
        available_questions = [q for q in q_list if q['question'] not in st.session_state.used_custom_questions]
        if not available_questions:
            return {"question": "No more custom questions for this level.", "answers": ["Next", "Round", "Please", "Click"], "correct": "Next"}
            
        question = random.choice(available_questions)
        st.session_state.used_custom_questions.append(question['question'])
        return question

    base_url = f"https://opentdb.com/api.php?amount=1&type=multiple&difficulty={difficulty.lower()}"
    if category_id != 0:
        base_url += f"&category={category_id}"
    
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            q = data["results"][0]
            question_text = html.unescape(q["question"])
            correct_answer = html.unescape(q["correct_answer"])
            incorrect_answers = [html.unescape(ans) for ans in q["incorrect_answers"]]
            all_answers = incorrect_answers + [correct_answer]
            random.shuffle(all_answers)
            return {"question": question_text, "answers": all_answers, "correct": correct_answer}
    except requests.exceptions.RequestException:
        return {"question": "The API is offline. Who is the best duelist?", "answers": ["You", "The Bot", "Me", "Us"], "correct": "You"}
    return None

# --- STATE MANAGEMENT FUNCTIONS ---
def reset_game_state():
    st.session_state.screen = 'setup'
    st.session_state.player_hp = 100
    st.session_state.computer_hp = 100
    st.session_state.round_number = 1
    st.session_state.question_in_round = 0
    st.session_state.last_attack = None
    st.session_state.current_question = None
    st.session_state.message = ""
    st.session_state.info = ""
    st.session_state.round_over = False
    st.session_state.selected_topic = "Any Category"
    st.session_state.show_animation = False
    st.session_state.used_custom_questions = []
    st.session_state.sound_to_play = None
    # --- ADDED: Score counters ---
    st.session_state.player_score = 0
    st.session_state.bot_score = 0

if 'screen' not in st.session_state:
    reset_game_state()

# --- GAME LOGIC FUNCTIONS ---
def new_round_check():
    st.session_state.last_attack = None
    st.session_state.question_in_round += 1
    
    questions_per_round = ROUND_SETTINGS[st.session_state.round_number]["questions"]
    
    if st.session_state.question_in_round > questions_per_round:
        if st.session_state.round_number < len(ROUND_SETTINGS):
            st.session_state.round_number += 1
            st.session_state.question_in_round = 1
            st.session_state.message = f"Round {st.session_state.round_number}, Draw!"
        else:
            st.session_state.screen = "game_over"
            return
    fetch_question()

def fetch_question():
    # --- MODIFIED: Clear old messages when fetching a new question ---
    st.session_state.message = ""
    st.session_state.info = ""
    category_id = TOPICS[st.session_state.selected_topic]
    difficulty = ROUND_SETTINGS[st.session_state.round_number]["name"]
    st.session_state.current_question = get_new_question(category_id, difficulty)
    st.session_state.round_over = False
    
def handle_answer(player_answer):
    if st.session_state.round_over: return

    is_correct = (player_answer == st.session_state.current_question["correct"])
    settings = ROUND_SETTINGS[st.session_state.round_number]
    damage = settings["damage"]
    computer_is_correct = (random.random() < settings["bot_accuracy"])
    
    # --- ADDED: Increment scores ---
    if is_correct:
        st.session_state.player_score += 1
    if computer_is_correct:
        st.session_state.bot_score += 1

    st.session_state.info = f"Correct answer was: **{st.session_state.current_question['correct']}**"

    if is_correct and not computer_is_correct:
        st.session_state.computer_hp = max(0, st.session_state.computer_hp - damage)
        st.session_state.message = f"💥 Direct hit! You dealt **{damage} damage**!"
        st.session_state.last_attack = {'attacker': 'player', 'damage': damage}
        st.session_state.sound_to_play = 'impact'
    elif not is_correct and computer_is_correct:
        st.session_state.player_hp = max(0, st.session_state.player_hp - damage)
        st.session_state.message = f"🛡️ The varmint shot back! You take **{damage} damage**."
        st.session_state.last_attack = {'attacker': 'bot', 'damage': damage}
        st.session_state.sound_to_play = 'impact'
    elif is_correct and computer_is_correct:
        st.session_state.message = "⚡️ Bullets collide! A clash, no damage dealt."
        st.session_state.last_attack = None
        st.session_state.sound_to_play = 'clash'
    else: # Both incorrect
        st.session_state.message = "💨 Tumbleweeds... both duelists missed."
        st.session_state.last_attack = None
        st.session_state.sound_to_play = 'incorrect'

    st.session_state.show_animation = True
    
def start_game(topic):
    reset_game_state()
    st.session_state.screen = "game"
    st.session_state.message = "The duel is about to begin, partner. Good luck."
    st.session_state.round_over = True
    st.session_state.selected_topic = topic

def back_to_setup():
    reset_game_state()

# --- Main App Logic ---
# --- MODIFIED: Changed title to be more thematic ---
st.title("High Noon Trivia")

if st.session_state.screen == "setup":
    st.subheader("Pick Your Battlefield")
    topic = st.selectbox("Choose your category, partner:", options=list(TOPICS.keys()))
    if st.button("🤠 Start the Duel!", use_container_width=True):
        start_game(topic)
        st.rerun()

elif st.session_state.screen == "game_over":
    st.subheader("The Dust Has Settled...")
    player_hp = st.session_state.player_hp
    computer_hp = st.session_state.computer_hp

    # --- MODIFIED: Thematic victory/defeat messages ---
    if player_hp > computer_hp:
        st.header("You're the quickest draw in the West! 🎉")
        st.balloons()
    elif computer_hp > player_hp:
        st.header("Better luck next time, partner. 💔")
    else:
        st.header("A Draw! Well fought. 🤝")
        
    st.write(f"**Final Tally:** You: {player_hp} HP | Bot: {computer_hp} HP")
    # --- ADDED: Display final correct answer counts ---
    st.write(f"**Bullseyes:** You: {st.session_state.player_score} | Bot: {st.session_state.bot_score}")
    if st.button("Go Again?", use_container_width=True):
        back_to_setup()
        st.rerun()

elif st.session_state.screen == "game":
    attack_info = st.session_state.last_attack
    p_col, mid_col, b_col = st.columns([5, 2, 5])

    # Player Display
    with p_col:
        player_class = "player-box"
        player_damage_html = ""
        if attack_info and attack_info['attacker'] == 'bot':
            player_class += " shaking"
            player_damage_html = f"<div class='damage-text'>-{attack_info['damage']} HP</div>"
        
        player_html_body = f"<div class='{player_class}'>{player_damage_html}<div class='player-icon'>🤠</div><h3>You</h3></div>"
        components.html(f"<html><head>{CSS_and_JS}</head><body>{player_html_body}</body></html>", height=200)
        st.progress(st.session_state.player_hp, text=f"❤️ {st.session_state.player_hp}/100")
        # --- MODIFIED: Player score display icon ---
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;'>⭐ Score: {st.session_state.player_score}</div>", unsafe_allow_html=True)


    # Animation Display
    with mid_col:
        bullet_html = ""
        if st.session_state.show_animation and attack_info:
            if attack_info['attacker'] == 'player':
                bullet_html = '<div class="bullet player-bullet">•</div>'
            elif attack_info['attacker'] == 'bot':
                bullet_html = '<div class="bullet bot-bullet">•</div>'
        components.html(f'<html><head>{CSS_and_JS}</head><body style="display:flex; align-items:center; justify-content:center; height:100%; position:relative;">{bullet_html}</body></html>', height=120)

    # Bot Display
    with b_col:
        bot_class = "player-box"
        bot_damage_html = ""
        if attack_info and attack_info['attacker'] == 'player':
            bot_class += " shaking"
            bot_damage_html = f"<div class='damage-text'>-{attack_info['damage']} HP</div>"

        bot_html_body = f"<div class='{bot_class}'>{bot_damage_html}<div class='player-icon'>🤖</div><h3>Tin Can</h3></div>"
        components.html(f"<html><head>{CSS_and_JS}</head><body>{bot_html_body}</body></html>", height=200)
        st.progress(st.session_state.computer_hp, text=f"❤️ {st.session_state.computer_hp}/100")
        # --- MODIFIED: Bot score display icon ---
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;'>⭐ Score: {st.session_state.bot_score}</div>", unsafe_allow_html=True)


    # Game Info and Controls
    st.divider()
    st.subheader(f"Round {st.session_state.round_number}: {ROUND_SETTINGS[st.session_state.round_number]['name']}")
    # --- ADDED: Question counter display ---
    if st.session_state.question_in_round > 0:
        total_q = ROUND_SETTINGS[st.session_state.round_number]['questions']
        st.write(f"Question {st.session_state.question_in_round} of {total_q}")

    if st.session_state.message: st.info(st.session_state.message)
    if st.session_state.info: st.success(st.session_state.info)

    if st.session_state.show_animation:
        if st.session_state.sound_to_play:
            sound_type = st.session_state.sound_to_play
            components.html(f"<script>playSound('{sound_type}');</script>", height=0, scrolling=False)
            st.session_state.sound_to_play = None

        time.sleep(0.8)
        st.session_state.show_animation = False
        st.session_state.round_over = True
        if st.session_state.player_hp <= 0 or st.session_state.computer_hp <= 0:
            st.session_state.screen = "game_over"
        st.rerun()

    if st.session_state.round_over and st.session_state.screen == "game":
        # --- MODIFIED: Thematic button text ---
        if st.button("▶️ Next Question, Partner", use_container_width=True):
            new_round_check()
            st.rerun()
    elif st.session_state.current_question and not st.session_state.round_over:
        q = st.session_state.current_question
        st.subheader(q["question"])
        answer_cols = st.columns(2)
        for i, ans in enumerate(q["answers"]):
            with answer_cols[i % 2]:
                if st.button(ans, key=f"ans_{i}", use_container_width=True):
                    handle_answer(ans)
                    st.rerun()


