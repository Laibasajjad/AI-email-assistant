import os
import re
import time
from datetime import datetime
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
st.set_page_config(page_title='AI Email Assistant', page_icon='✉️', layout='centered', initial_sidebar_state='expanded')
MODEL_NAME = 'gemini-3.6-flash'
MAX_INPUT_LEN = 3000

def get_api_key() -> str | None:
    if st.session_state.get('api_key_input'):
        return st.session_state['api_key_input'].strip()
    try:
        if 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except Exception:
        pass
    return os.environ.get('GEMINI_API_KEY')

def sanitize(text: str) -> str:
    if not text:
        return ''
    text = text.strip()
    return text[:MAX_INPUT_LEN]

def is_valid_email(address: str) -> bool:
    if not address:
        return True
    pattern = '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'
    return re.match(pattern, address) is not None

def build_prompt(recipient_name: str, recipient_role: str, sender_name: str, subject: str, topic: str, tone: str, email_type: str, key_points: str, length: str) -> str:
    lines = ['You are an expert professional email writer.', 'Write a complete, ready-to-send email based on the details below.', '', f'Recipient name: {recipient_name}']
    if recipient_role:
        lines.append(f'Recipient role/relationship: {recipient_role}')
    sender_display = sender_name or 'the sender'
    lines.append(f'Sender name (to sign off with): {sender_display}')
    lines.append(f'Email subject: {subject}')
    lines.append(f'Topic / purpose of the email: {topic}')
    lines.append(f'Type of email: {email_type}')
    lines.append(f'Desired tone: {tone}')
    lines.append(f'Desired length: {length}')
    if key_points:
        lines.append(f'Key points that must be included:\n{key_points}')
    lines.extend(['', 'Formatting rules:', "- Start with an appropriate greeting using the recipient's name.", '- Write clear, well-organized paragraphs (no markdown, no bullet symbols unless the key points naturally call for a short list).', "- End with a suitable sign-off and the sender's name.", '- Do not include the subject line in the body; the subject is handled separately.', '- Do not add placeholder brackets like [Company Name] unless information is genuinely missing — infer sensible details from context instead.', '- Return ONLY the email body text. No preamble, no explanation, no markdown code fences.'])
    return '\n'.join(lines)

def generate_email(prompt: str, api_key: str, temperature: float=0.7) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_NAME)
    generation_config = genai.types.GenerationConfig(temperature=temperature, max_output_tokens=1024)
    response = model.generate_content(prompt, generation_config=generation_config)
    if not response.candidates:
        raise ValueError('Gemini returned no candidates. The prompt may have been blocked.')
    text = (response.text or '').strip()
    if not text:
        raise ValueError('Gemini returned an empty response. Try adjusting your inputs.')
    return text

def call_with_retry(prompt: str, api_key: str, retries: int=2):
    last_error = None
    for attempt in range(retries + 1):
        try:
            return generate_email(prompt, api_key)
        except google_exceptions.ResourceExhausted as e:
            last_error = 'Rate limit reached on the Gemini API. Please wait a moment and try again.'
        except google_exceptions.PermissionDenied:
            raise ValueError("The API key was rejected. Double-check that it's a valid Gemini API key.")
        except google_exceptions.InvalidArgument as e:
            raise ValueError(f'Gemini rejected the request: {e}')
        except google_exceptions.GoogleAPIError as e:
            last_error = f'Gemini API error: {e}'
        except Exception as e:
            last_error = f'Unexpected error: {e}'
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise ValueError(last_error or 'Failed to generate the email after multiple attempts.')
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ''
if 'generated_subject' not in st.session_state:
    st.session_state.generated_subject = ''
if 'history' not in st.session_state:
    st.session_state.history = []
with st.sidebar:
    st.header('⚙️ Settings')
    st.text_input('Gemini API Key', type='password', key='api_key_input', help="Paste your Gemini API key here for this session, or set it once via a .streamlit/secrets.toml file or the GEMINI_API_KEY environment variable so you don't have to re-enter it.", placeholder='AIza...')
    st.caption('Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).')
    st.divider()
    tone = st.selectbox('Tone', ['Formal', 'Professional (default)', 'Friendly', 'Casual', 'Persuasive', 'Apologetic'], index=1)
    email_type = st.selectbox('Email type', ['General email', 'Follow-up', 'Introduction / cold outreach', 'Meeting request', 'Thank-you note', 'Apology', 'Complaint', 'Job application / cover note', 'Status update'])
    length = st.selectbox('Length', ['Short (3-4 sentences)', 'Medium (1-2 paragraphs)', 'Long (detailed)'], index=1)
    st.divider()
    if st.session_state.history:
        st.caption(f'📜 {len(st.session_state.history)} draft(s) generated this session')
        if st.button('Clear history'):
            st.session_state.history = []
            st.rerun()
st.title('✉️ AI Email Assistant')
st.write('Fill in a few details and let Gemini draft a ready-to-send email for you.')
with st.form('email_form', clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        recipient_name = st.text_input("Recipient's name *", placeholder='e.g. Dr. Sarah Khan')
    with col2:
        recipient_email = st.text_input("Recipient's email (optional)", placeholder='e.g. sarah.khan@example.com')
    recipient_role = st.text_input("Recipient's role / your relationship to them (optional)", placeholder='e.g. my manager, a potential client, university professor')
    sender_name = st.text_input('Your name *', placeholder='e.g. Laiba Sajjad')
    subject = st.text_input('Email subject *', placeholder='e.g. Request for Project Deadline Extension')
    topic = st.text_area('What is this email about? *', placeholder="Describe the topic/purpose in your own words, e.g. 'I need to ask for a 3-day extension on the AI project submission because of a scheduling conflict with another course deadline.'", height=120)
    key_points = st.text_area('Key points to include (optional, one per line)', placeholder='e.g.\nNew deadline: Friday\nWilling to submit partial work now\nThank them for understanding', height=100)
    submitted = st.form_submit_button('✨ Generate Email', use_container_width=True)
if submitted:
    errors = []
    recipient_name_c = sanitize(recipient_name)
    sender_name_c = sanitize(sender_name)
    subject_c = sanitize(subject)
    topic_c = sanitize(topic)
    recipient_role_c = sanitize(recipient_role)
    key_points_c = sanitize(key_points)
    recipient_email_c = sanitize(recipient_email)
    if not recipient_name_c:
        errors.append("Recipient's name is required.")
    if not sender_name_c:
        errors.append('Your name is required.')
    if not subject_c:
        errors.append('Email subject is required.')
    if not topic_c:
        errors.append('Please describe what the email is about.')
    if recipient_email_c and (not is_valid_email(recipient_email_c)):
        errors.append("That doesn't look like a valid email address.")
    api_key = get_api_key()
    if not api_key:
        errors.append('No Gemini API key found. Add one in the sidebar, or set it via secrets.toml / the GEMINI_API_KEY environment variable.')
    if errors:
        for err in errors:
            st.error(err)
    else:
        with st.spinner('Drafting your email with Gemini...'):
            prompt = build_prompt(recipient_name=recipient_name_c, recipient_role=recipient_role_c, sender_name=sender_name_c, subject=subject_c, topic=topic_c, tone=tone, email_type=email_type, key_points=key_points_c, length=length)
            try:
                body = call_with_retry(prompt, api_key)
                st.session_state.generated_email = body
                st.session_state.generated_subject = subject_c
                st.session_state.history.insert(0, {'subject': subject_c, 'body': body, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')})
                st.success('Email drafted successfully!')
            except ValueError as e:
                st.error(str(e))
if st.session_state.generated_email:
    st.divider()
    st.subheader('📧 Your Draft')
    st.text_input('Subject', value=st.session_state.generated_subject, key='display_subject', disabled=True)
    edited_body = st.text_area('Body (you can edit this before copying/downloading)', value=st.session_state.generated_email, height=320, key='editable_body')
    dl_col, regen_col = st.columns(2)
    with dl_col:
        file_content = f'Subject: {st.session_state.generated_subject}\n\n{edited_body}'
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button('⬇️ Download as .txt', data=file_content, file_name=f'email_draft_{timestamp_str}.txt', mime='text/plain', use_container_width=True)
    with regen_col:
        if st.button('🔄 Regenerate', use_container_width=True):
            api_key = get_api_key()
            if not api_key:
                st.error('No Gemini API key found. Add one in the sidebar.')
            else:
                with st.spinner('Generating a new version...'):
                    prompt = build_prompt(recipient_name=sanitize(recipient_name), recipient_role=sanitize(recipient_role), sender_name=sanitize(sender_name), subject=sanitize(subject), topic=sanitize(topic), tone=tone, email_type=email_type, key_points=sanitize(key_points), length=length)
                    try:
                        body = call_with_retry(prompt, api_key)
                        st.session_state.generated_email = body
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
if st.session_state.history:
    with st.expander(f'📜 Previous drafts this session ({len(st.session_state.history)})'):
        for i, item in enumerate(st.session_state.history):
            st.markdown(f"**{item['subject']}**  \n*{item['timestamp']}*")
            st.text(item['body'])
            if i < len(st.session_state.history) - 1:
                st.divider()
st.divider()
st.caption('Built with Streamlit and Google Gemini.')
