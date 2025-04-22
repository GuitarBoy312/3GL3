import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from audiorecorder import audiorecorder
import io

# OpenAI API 키 설정
if 'openai_client' not in st.session_state:
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])

# 시스템 메시지 정의
SYSTEM_MESSAGE = {
    "role": "system", 
    "content": '''
    너는 초등학교 영어교사야. 나는 초등학생이고, 나와 영어로 대화하는 연습을 해 줘. 영어공부와 관계없는 질문에는 대답할 수 없어. 그리고 나는 무조건 영어로 말할거야. 내 발음이 좋지 않더라도 영어로 인식하도록 노력해 봐.            
    [대화의 제목]
    Hi, I'm Momo.
    [지시]
    1. 내가 너에게 "What's this?" 또는 "What's that? 라고 질문을 할거야. 
    2. 너는 내 질문을 듣고 물건을 무작위로 정해서 "It's ...." 이라고 대답을 해. 물건은 매번 바뀌어야 해.
    3. 그 후, 내가 "Nice."라고 하면
    4. 너는 "What's this?" 또는 "What's that? 이라고 질문해. 질문의 끝에 아래의 [stuff list]에 있는 물건과 관련된 이모지를 붙여서 내가 대답할 수 있게 해야해.
    5. 그 후 내가 물건이 뭐라고 말하면, 너는 "Nice." 라고만 답해. 
    [stuff list]
    1. ball🥎
    2. bike🚲
    3. doll🎎
    4. cup☕
    5. hat👒
    6. robot🤖
    '''
}

# 초기화 함수
def initialize_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])
    st.session_state['chat_history'] = [SYSTEM_MESSAGE]
    st.session_state['initialized'] = True

# 세션 상태 초기화
if 'initialized' not in st.session_state or not st.session_state['initialized']:
    initialize_session()

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    st.session_state['chat_history'].append({"role": "user", "content": prompt})
    response = st.session_state['openai_client'].chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['chat_history']
    )
    assistant_response = response.choices[0].message.content
    st.session_state['chat_history'].append({"role": "assistant", "content": assistant_response})
    return assistant_response

# 음성을 녹음하고 텍스트로 변환하는 함수
def record_and_transcribe():
    audio = audiorecorder("녹음 시작", "녹음 완료", pause_prompt="잠깐 멈춤")
    
    if len(audio) > 0:
        st.success("녹음이 완료되었습니다. 변환 중입니다...")
        st.write("내가 한 말 듣기")
        st.audio(audio.export().read())
        
        audio_bytes = io.BytesIO()
        audio.export(audio_bytes, format="wav")
        audio_file = io.BytesIO(audio_bytes.getvalue())
        audio_file.name = "audio.wav"
        transcription = st.session_state['openai_client'].audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text
    
    return None

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech_openai(text):
    try:
        response = st.session_state['openai_client'].audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )
        st.write("인공지능 선생님의 대답 듣기")    
        st.audio(response.content)
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

# Streamlit UI
st.write(
    "<div style='text-align: center; font-size: 35px; font-weight: bold;'>"
    "✨인공지능 영어대화 선생님 잉글링👩‍🏫</div>",
    unsafe_allow_html=True
)
st.write(
    "<div style='text-align: center; font-size: 25px; font-weight: bold;'>"
    "자기소개와 만나고 헤어지는 인사하기🖐</div>",
    unsafe_allow_html=True
)
st.divider()

# 처음부터 다시하기 버튼
if st.button("처음부터 다시하기", type="primary"):
    initialize_session()
    st.rerun()

# 확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
        """     
        **1️⃣ [녹음 시작] 버튼을 눌러 잉글링에게 말하기.**  
        **2️⃣ [녹음 완료] 버튼을 누르고 내가 한 말과 잉글링의 대답 들어보기.**  
        **3️⃣ 재생 막대의 버튼으로 재생 ▶ 및 정지 ⏸,
        잉글링의 말이 빠르다면 재생 막대의 오른쪽 스노우맨 버튼(점 세 개)을 눌러 재생 속도를 조절하기.**  
        **4️⃣ 1~3번을 반복하기.  
        말문이 막힐 땐 [잠깐 멈춤] 버튼을 누르고 할 말을 생각한 후 [녹음 시작] 버튼을 다시 눌러 말하기.**
        **5️⃣ 왼쪽의 대화 기록을 확인하며 내가 잘 말하고 들었는지 확인이 가능합니다.**
        """
    )

    st.warning(
        "🙏 잉글링은 완벽하게 이해하거나 제대로 대답하지 않을 수 있어요.\n\n"
        "🙏 그럴 때에는 [처음부터 다시하기] 버튼을 눌러주세요."
    )

    st.divider()

 

    st.markdown(
        """
        **물어보고 대답할 물건들**    
        🥎 ball(볼, 공)  
        🚲 bike(바이크, 자전거)  
        🎎 doll(돌, 인형)  
        ☕ cup(컵)  
        👒 hat(햇, 모자)  
        🤖 robot(로봇)  
        """
    )
    st.write("### 🗣️ 잉글링과 이렇게 대화해 보세요!")
    st.markdown(
        """
        **😀 나:** What's this?(왓스 디스) 또는 What's that?(왓스 댓)  
        **🤖 잉글링:** It's a 물건(이츠 어 물건)  
        **😀 나:** Nice.(나이스)  
        **🤖 잉글링:** What's this?(왓스 디스) 또는 What's that?(왓스 댓)  
        **😀 나:** It's a 물건(이츠 어 물건)  
        **🤖 잉글링:** Nice.(나이스)  
        """
    )
    
# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    user_input_text = record_and_transcribe()
    if user_input_text:
        response = get_chatgpt_response(user_input_text)
        if response:
            text_to_speech_openai(response)

# 사이드바 구성
with st.sidebar:
    st.header("대화 기록")
    for message in st.session_state['chat_history'][1:]:  # 시스템 메시지 제외
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
