import random
import streamlit as st
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="Myth Buster Bot", page_icon="🕵️‍♂️")
st.title("Fact Buster Bot")
st.caption("Bust myths with science, history, and facts ✅❌")

# ----------------------------
# Sidebar Controls (API key input removed)
# ----------------------------
with st.sidebar:
    st.subheader("⚙️ Controls")
    model_name = st.selectbox(
        "Groq Model",
        ["deepseek-r1-distill-llama-70b", "gemma2-9b-it", "llama-3.1-8b-instant"],
        index=2
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens", 50, 2000, 900)

    st.markdown("### Modes")
    quiz_mode = st.checkbox("🎯 Enable Quiz Mode")

    if st.button("🧹 Clear Chat"):
        for key in ["history", "memory", "quiz_score", "quiz_questions"]:
            if key in st.session_state:
                st.session_state.pop(key)
        st.rerun()

# ----------------------------
# API Key (Directly set here)
# ----------------------------
GROQ_API_KEY = "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"

# ----------------------------
# Memory & State
# ----------------------------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

if "history" not in st.session_state:
    st.session_state.history = []

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

# ----------------------------
# Chat LLM Setup
# ----------------------------
system_prompt = """
You are 🕵️ Myth Buster Bot.
Your job:
1. Detect if the statement is a Myth ❌ or Fact ✅.
2. Give a short, clear explanation with a reliable reference (WHO, Harvard, Wikipedia).
3. Categorize into: Health, Science, History, Everyday Life.
4. If the user asks something fun (aliens, superstitions), give a fun + factual reply.
5. If in Quiz Mode, ask True/False myth questions and track the score.
Answer in this structure:

**Verdict:** Myth ❌ / Fact ✅
**Category:** (Health/Science/History/Life)
**Explanation:** short reasoning + reference
"""

llm = ChatGroq(
    model_name=model_name,
    temperature=temperature,
    max_tokens=max_tokens,
    api_key=GROQ_API_KEY
)

conv = ConversationChain(
    llm=llm,
    memory=st.session_state.memory,
    verbose=False
)

# ----------------------------
# Quiz Questions Pool
# ----------------------------
QUIZ_POOL = [
    ("Sugar causes hyperactivity in kids.", "Myth"),
    ("Cracking your knuckles causes arthritis.", "Myth"),
    ("You should drink 8 glasses of water daily.", "Myth"),
    ("Humans only use 10% of their brains.", "Myth"),
    ("The Great Wall of China is visible from space.", "Myth"),
    ("Lightning never strikes the same place twice.", "Myth"),
    ("Shaving hair makes it grow back thicker.", "Myth"),
    ("Bulls get angry when they see red.", "Myth"),
    ("Goldfish have a 3-second memory.", "Myth"),
    ("Vaccines cause autism.", "Myth"),
    ("Earth revolves around the Sun.", "Fact"),
    ("Bananas grow on trees.", "Myth"),  # actually giant herbs
    ("Ostriches bury their heads in the sand.", "Myth"),
    ("Coffee stunts your growth.", "Myth"),
    ("Carrots improve night vision.", "Myth"),
    ("An apple a day keeps the doctor away.", "Myth"), 
    ("Mount Everest is the tallest mountain in the world.", "Fact"),
    ("Penguins mate for life.", "Fact"),
    ("The Sahara is the largest desert in the world.", "Fact"),
    ("Humans and dinosaurs lived together.", "Myth"),
    ("Water boils at 100°C (212°F) at sea level.", "Fact"),
    ("The human body has 206 bones.", "Fact"),
    ("Sharks existed before trees.", "Fact"),
    ("Light travels faster than sound.", "Fact"),
    ("Octopuses have three hearts.", "Fact"),
    ("Bananas are berries, botanically speaking.", "Fact"),
    ("The Amazon rainforest produces about 20% of the world's oxygen.", "Fact"),
    ("Your heart beats about 100,000 times a day.", "Fact"),
    ("The Pacific Ocean is the largest ocean on Earth.", "Fact"),
]
# ----------------------------
# Chat UI
# ----------------------------
# Show history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your myth or say 'Start Quiz'...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ------------------------
    # Quiz Mode Handling
    # ------------------------
    if quiz_mode and user_input.lower().strip() == "start quiz":
        q, ans = random.choice(QUIZ_POOL)
        st.session_state.quiz_questions.append((q, ans))
        bot_reply = f"🎯 Quiz Time! True or False?\n\n**{q}**"
    elif quiz_mode and user_input.lower() in ["true", "false"]:
        if st.session_state.quiz_questions:
            q, correct = st.session_state.quiz_questions[-1]
            user_ans = "Fact" if user_input.lower() == "true" else "Myth"
            if user_ans == correct:
                st.session_state.quiz_score += 1
                bot_reply = f"✅ Correct! **{q}** is {correct}."
            else:
                bot_reply = f"❌ Wrong. **{q}** is actually {correct}."
            bot_reply += f"\n\nYour score: {st.session_state.quiz_score}"
        else:
            bot_reply = "⚠️ No active quiz. Type 'Start Quiz' to begin."
    else:
        # ------------------------
        # Normal Myth-Busting
        # ------------------------
        with st.spinner("Thinking..."):
            bot_reply = conv.run(system_prompt + "\n\nUser: " + user_input)

    # Show bot response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.history.append({"role": "assistant", "content": bot_reply})
