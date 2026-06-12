import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io

# Бет конфигурациясы
st.set_page_config(
    page_title="Тамақтану сапасын бағалау | Жас дарын",
    page_icon="🍲",
    layout="centered"
)

# GitHub CSV файлының URL-і
GITHUB_CSV_URL = "https://raw.githubusercontent.com/aidarpavl/Stolovaya_ball/refs/heads/main/ZHD_Stolovaya_otvety.csv"
GITHUB_API_URL = "https://api.github.com/repos/aidarpavl/Stolovaya_ball/contents/ZHD_Stolovaya_otvety.csv"

# GitHub токені (өз токеніңізбен ауыстырыңыз)
# Токенді https://github.com/settings/tokens мекенжайынан алуға болады
GITHUB_TOKEN = ""  # Қажет болса, өз токеніңізді қойыңыз

# CSS стильдер
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        background: linear-gradient(135deg, #f5b042, #ff8c00);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .grade-btn {
        background: #f5f5f5;
        border: 2px solid #e0e0e0;
        border-radius: 50px;
        padding: 0.5rem 1rem;
        text-align: center;
        cursor: pointer;
        margin: 0.25rem;
        display: inline-block;
        transition: all 0.3s;
    }
    .grade-btn:hover {
        background: #ffecb3;
        border-color: #ffc107;
    }
    .score-card {
        background: #f5f5f5;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        border: 2px solid #e0e0e0;
    }
    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        color: #666;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Сессия күйін бастау
if 'selected_grade' not in st.session_state:
    st.session_state.selected_grade = None
if 'selected_score' not in st.session_state:
    st.session_state.selected_score = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Басты header
st.markdown("""
    <div class="main-header">
        <h1>🍲 Тамақты бағалау</h1>
        <p>Жас дарын - күнделікті ас сапасына көзқарас</p>
    </div>
""", unsafe_allow_html=True)

# CSV файлынан деректерді оқу функциясы
def load_data():
    try:
        df = pd.read_csv(GITHUB_CSV_URL)
        return df
    except:
        # Егер файл жоқ болса, жаңа DataFrame құру
        return pd.DataFrame(columns=["Уақыт", "Сынып", "Балл"])

# Деректерді GitHub-қа сақтау функциясы
def save_to_github(df):
    try:
        # CSV-ге сақтау
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        # GitHub API арқылы файлды жаңарту
        if GITHUB_TOKEN:
            # Файлдың ағымдағы SHA-сын алу
            response = requests.get(GITHUB_API_URL, headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            })
            
            if response.status_code == 200:
                sha = response.json().get('sha')
            else:
                sha = None
            
            # Файлды жүктеу
            import base64
            content_base64 = base64.b64encode(csv_content.encode()).decode()
            
            upload_data = {
                "message": "Update survey data",
                "content": content_base64,
                "branch": "main"
            }
            
            if sha:
                upload_data["sha"] = sha
            
            response = requests.put(GITHUB_API_URL, 
                headers={
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json=upload_data
            )
            
            return response.status_code == 200
        else:
            # Токен жоқ болса, жергілікті сақтау (тек демо)
            st.warning("GitHub токені орнатылмаған. Деректер уақытша сақталады.")
            return True
            
    except Exception as e:
        st.error(f"Сақтау қатесі: {str(e)}")
        return False

# Сынып таңдау
st.markdown("### 📚 Сыныпты таңдаңыз:")

grades = ["5 сынып", "6 сынып", "7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"]
grade_cols = st.columns(4)

for i, grade in enumerate(grades):
    col = grade_cols[i % 4]
    with col:
        if st.button(grade, key=f"grade_{grade}", use_container_width=True):
            st.session_state.selected_grade = grade
            st.rerun()

# Таңдалған сыныпты көрсету
if st.session_state.selected_grade:
    st.success(f"✅ Таңдалған сынып: {st.session_state.selected_grade}")
else:
    st.info("👆 Сыныпты таңдаңыз")

st.markdown("---")

# Бағалау таңдау
st.markdown("### ⭐ Тамақ сапасын бағалаңыз:")

score_cols = st.columns(3)

score_options = {
    5: {"emoji": "🌟", "text": "Өте дәмді", "color": "#4CAF50"},
    4: {"emoji": "👍", "text": "Қанағаттанарлық", "color": "#FF9800"},
    3: {"emoji": "😐", "text": "Төмен", "color": "#f44336"}
}

for i, (score, info) in enumerate(score_options.items()):
    with score_cols[i]:
        if st.button(f"{info['emoji']} {score}\n{info['text']}", key=f"score_{score}", use_container_width=True):
            st.session_state.selected_score = score
            st.rerun()

# Таңдалған бағаны көрсету
if st.session_state.selected_score:
    info = score_options[st.session_state.selected_score]
    st.success(f"✅ Таңдалған баға: {st.session_state.selected_score} - {info['text']} {info['emoji']}")
else:
    st.info("👆 Тамақ сапасын бағалаңыз")

st.markdown("---")

# Жіберу батырмасы
submit_disabled = not (st.session_state.selected_grade and st.session_state.selected_score)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✨ Бағалауды жіберу ✨", disabled=submit_disabled, use_container_width=True):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Жаңа деректерді қосу
        df = load_data()
        new_row = pd.DataFrame({
            "Уақыт": [timestamp],
            "Сынып": [st.session_state.selected_grade],
            "Балл": [st.session_state.selected_score]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Сақтау
        with st.spinner("📡 Деректер сақталуда..."):
            if save_to_github(df):
                st.balloons()
                st.success(f"""✅ **Сәтті сақталды!**
                
📅 Уақыт: {timestamp}
📚 Сынып: {st.session_state.selected_grade}
⭐ Балл: {st.session_state.selected_score}
                """)
                
                # Сессияны тазалау
                st.session_state.selected_grade = None
                st.session_state.selected_score = None
                st.rerun()
            else:
                st.error("❌ Деректер сақталмады. Қайталап көріңіз.")

# Статистиканы көрсету
st.markdown("---")
with st.expander("📊 Статистика"):
    df = load_data()
    if len(df) > 0:
        st.metric("Жалпы жауаптар саны", len(df))
        
        # Сынып бойынша статистика
        st.subheader("Сынып бойынша")
        class_stats = df.groupby("Сынып").size().reset_index(name="Жауап саны")
        st.dataframe(class_stats, use_container_width=True)
        
        # Балл бойынша статистика
        st.subheader("Бағалар бойынша")
        score_stats = df.groupby("Балл").size().reset_index(name="Жауап саны")
        st.dataframe(score_stats, use_container_width=True)
        
        # Орташа балл
        avg_score = df["Балл"].mean()
        st.metric("Орташа балл", f"{avg_score:.2f}")
    else:
        st.info("Әлі дерек жоқ. Бірінші болып бағалаңыз!")

# Footer
st.markdown("""
    <div class="footer">
        ⏱️ Деректер GitHub репозиторийінде сақталада<br>
        <a href="https://github.com/aidarpavl/Stolovaya_ball" target="_blank">GitHub репозиторийі</a> | 
        <a href="https://raw.githubusercontent.com/aidarpavl/Stolovaya_ball/refs/heads/main/ZHD_Stolovaya_otvety.csv" target="_blank">CSV файлы</a>
    </div>
""", unsafe_allow_html=True)