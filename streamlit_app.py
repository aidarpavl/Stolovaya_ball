import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Google Apps Script URL (сіздің URL-іңіз)
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwui6LgqaV-SjkyLsv3gZEeUvrZ2v9NT65WAc8C7dcA2p5lIz2GU_roRcZpm06e3v-8/exec"

# Бет конфигурациясы
st.set_page_config(
    page_title="Тамақтану сапасын бағалау | Жас дарын",
    page_icon="🍲",
    layout="centered"
)

# CSS стильдер
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .header {
        text-align: center;
        background: linear-gradient(135deg, #f5b042, #ff8c00);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    .grade-btn {
        background: #f5f5f5;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .grade-btn:hover {
        background: #ffecb3;
        border-color: #ffc107;
    }
    .selected {
        background: linear-gradient(135deg, #ffc107, #ff8c00);
        color: white;
        border-color: #ff8c00;
    }
    .score-card {
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        background: #f5f5f5;
        cursor: pointer;
        transition: all 0.3s;
        border: 2px solid #e0e0e0;
    }
    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    .score-selected {
        background: linear-gradient(135deg, #ffc107, #ff8c00);
        color: white;
        border-color: #ff8c00;
        transform: scale(1.02);
    }
    .score-value {
        font-size: 48px;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 12px;
        margin-top: 2rem;
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

# Басты бет
st.markdown("""
    <div class="header">
        <h1>🍲 Тамақты бағалау</h1>
        <p>Жас дарын</p>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Сынып таңдау
    st.markdown("### 📚 Сыныпты таңдаңыз:")
    
    grades = ["5 сынып", "6 сынып", "7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"]
    cols = st.columns(4)
    for i, grade in enumerate(grades):
        col = cols[i % 4]
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
    
    # 5 балл
    with score_cols[0]:
        if st.button("🌟 5\nӨте дәмді", key="score_5", use_container_width=True):
            st.session_state.selected_score = 5
            st.rerun()
    
    # 4 балл
    with score_cols[1]:
        if st.button("👍 4\nҚанағаттанарлық", key="score_4", use_container_width=True):
            st.session_state.selected_score = 4
            st.rerun()
    
    # 3 балл
    with score_cols[2]:
        if st.button("😐 3\nТөмен", key="score_3", use_container_width=True):
            st.session_state.selected_score = 3
            st.rerun()
    
    # Таңдалған бағаны көрсету
    if st.session_state.selected_score:
        score_text = {5: "Өте дәмді 🌟", 4: "Қанағаттанарлық 👍", 3: "Төмен 😐"}
        st.success(f"✅ Таңдалған баға: {st.session_state.selected_score} - {score_text[st.session_state.selected_score]}")
    else:
        st.info("👆 Тамақ сапасын бағалаңыз")
    
    st.markdown("---")
    
    # Жіберу батырмасы
    submit_disabled = not (st.session_state.selected_grade and st.session_state.selected_score)
    
    if st.button("✨ Бағалауды жіберу ✨", disabled=submit_disabled, use_container_width=True):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            "grade": st.session_state.selected_grade,
            "score": st.session_state.selected_score,
            "timestamp": timestamp
        }
        
        with st.spinner("📡 Деректер Google кестеге жазылуда..."):
            try:
                response = requests.post(
                    APPS_SCRIPT_URL,
                    headers={"Content-Type": "application/json"},
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("result") == "success" or result.get("status") == "success":
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
                        st.error(f"❌ Қате: {result.get('message', 'Белгісіз қате')}")
                else:
                    st.error(f"❌ HTTP қатесі: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"""❌ Қосылу қатесі: {str(e)}
                
🔧 Тексеріңіз:
• Интернет байланысы
• Apps Script URL дұрыстығы
• Apps Script "Кез келген адам" ретінде орналастырылған
                """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        ⏱️ Деректер Google кестеге автоматты түрде сақталада<br>
        GitHub: aidarpavl/Stolovaya_ball
    </div>
""", unsafe_allow_html=True)

# Бүгіннің статистикасын көрсету (опционально)
st.markdown("---")
with st.expander("📊 Бүгінгі статистика"):
    try:
        # Бұл жерде статистиканы көрсетуге болады
        st.info("Кестеден деректерді көру үшін Google Sheets-ке өтіңіз")
    except:
        pass
