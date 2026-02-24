import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional
import time

# ===========================
# CONFIGURATION
# ===========================
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 500;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
    }
    
    .bot-message {
        background-color: #f5f5f5;
        border-left: 5px solid #4CAF50;
    }
    
    /* Source card styling */
    .source-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #fff;
        border: 1px solid #ddd;
        margin-bottom: 0.5rem;
    }
    
    /* Stats styling */
    .stat-card {
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
    
    /* Success/Error messages */
    .success-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .error-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# ===========================
# SESSION STATE INITIALIZATION
# ===========================
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'refresh_token' not in st.session_state:
    st.session_state.refresh_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'uploaded_files_count' not in st.session_state:
    st.session_state.uploaded_files_count = 0

# ===========================
# API HELPER FUNCTIONS
# ===========================

def make_request(method: str, endpoint: str, data: dict = None, files: dict = None, auth: bool = True):
    """Make API request with proper error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if auth and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    if data and not files:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, headers=headers, timeout=60)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=30)
        
        return response
    
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to server. Please check if backend is running.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def handle_api_response(response, success_message: str = None):
    """Handle API response with proper error messages"""
    if not response:
        return None
    
    if response.status_code in [200, 201]:
        if success_message:
            st.success(success_message)
        return response.json()
    elif response.status_code == 401:
        st.error("🔒 Session expired. Please login again.")
        st.session_state.access_token = None
        st.session_state.page = "login"
        st.rerun()
    else:
        try:
            error_data = response.json()
            st.error(f"❌ {error_data.get('detail', 'Unknown error occurred')}")
        except:
            st.error(f"❌ Error: {response.status_code}")
        return None

# ===========================
# AUTH FUNCTIONS
# ===========================

def login_user(email: str, password: str) -> bool:
    """Login user and store tokens"""
    response = make_request("POST", "/auth/login", {
        "email": email,
        "password": password
    }, auth=False)
    
    data = handle_api_response(response)
    if data:
        st.session_state.access_token = data["access_token"]
        st.session_state.refresh_token = data["refresh_token"]
        return True
    return False

def signup_user(email: str, password: str, full_name: str) -> bool:
    """Signup new user"""
    response = make_request("POST", "/auth/signup", {
        "email": email,
        "password": password,
        "full_name": full_name
    }, auth=False)
    
    return handle_api_response(response, "✅ Account created successfully!") is not None

def get_user_info():
    """Get current user information"""
    response = make_request("GET", "/auth/me")
    return handle_api_response(response)

def forgot_password(email: str) -> bool:
    """Request password reset"""
    response = make_request("POST", "/auth/forgot-password", {
        "email": email
    }, auth=False)
    
    return handle_api_response(response, "📧 Reset link sent to your email!") is not None

def change_password(old_password: str, new_password: str) -> bool:
    """Change user password"""
    response = make_request("POST", "/auth/change-password", {
        "old_password": old_password,
        "new_password": new_password
    })
    
    return handle_api_response(response, "✅ Password changed successfully!") is not None

# ===========================
# CHAT FUNCTIONS
# ===========================

def send_chat_message(query: str, top_k: int = 5, similarity_threshold: float = 0.5):
    """Send chat message and get response"""
    response = make_request("POST", "/chat", {
        "query": query,
        "top_k": top_k,
        "similarity_threshold": similarity_threshold
    })
    
    return handle_api_response(response)

def upload_document(file):
    """Upload and index document"""
    files = {"file": file}
    response = make_request("POST", "/upload-document", files=files)
    return handle_api_response(response)

# ===========================
# UI PAGES
# ===========================

def login_page():
    """Login page UI"""
    st.markdown("<h1 style='text-align: center;'>🤖 RAG Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Login to your account</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            
            with col_btn2:
                if st.form_submit_button("📝 Create Account", use_container_width=True):
                    st.session_state.page = "signup"
                    st.rerun()
            
            if login_btn:
                if email and password:
                    with st.spinner("Logging in..."):
                        if login_user(email, password):
                            st.session_state.page = "chat"
                            st.rerun()
                else:
                    st.warning("⚠️ Please fill all fields")
        
        if st.button("🔑 Forgot Password?", use_container_width=True):
            st.session_state.page = "forgot_password"
            st.rerun()

def signup_page():
    """Signup page UI"""
    st.markdown("<h1 style='text-align: center;'>📝 Create Account</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Join us today</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        with st.form("signup_form"):
            full_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                signup_btn = st.form_submit_button("🚀 Create Account", use_container_width=True)
            
            with col_btn2:
                if st.form_submit_button("🔙 Back to Login", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()
            
            if signup_btn:
                if not all([full_name, email, password, confirm_password]):
                    st.warning("⚠️ Please fill all fields")
                elif password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    with st.spinner("Creating account..."):
                        if signup_user(email, password, full_name):
                            time.sleep(1)
                            st.session_state.page = "login"
                            st.rerun()

def forgot_password_page():
    """Forgot password page UI"""
    st.markdown("<h1 style='text-align: center;'>🔑 Reset Password</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Enter your email to receive reset link</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        with st.form("forgot_password_form"):
            email = st.text_input("📧 Email", placeholder="Enter your registered email")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                send_btn = st.form_submit_button("📨 Send Reset Link", use_container_width=True)
            
            with col_btn2:
                if st.form_submit_button("🔙 Back to Login", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()
            
            if send_btn:
                if email:
                    with st.spinner("Sending..."):
                        forgot_password(email)
                else:
                    st.warning("⚠️ Please enter your email")

# Add this function after forgot_password_page()

def reset_password_page():
    """Reset password page with token"""
    st.markdown("<h1 style='text-align: center;'>🔐 Reset Password</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Enter your new password</h3>", unsafe_allow_html=True)
    
    # Get token from URL
    query_params = st.query_params
    token = ""
    
    if hasattr(query_params, 'get'):
        token = query_params.get("token", "")
    elif isinstance(query_params, dict):
        token = query_params.get("token", [""])[0] if "token" in query_params else ""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        if not token:
            st.warning("⚠️ No reset token found!")
            st.info("Please enter the token from your email or click the link again.")
            token = st.text_input("Reset Token", placeholder="Paste your reset token here")
        else:
            st.success("✅ Reset token detected")
            st.code(token[:20] + "...", language=None)
        
        with st.form("reset_password_form"):
            new_password = st.text_input("🔒 New Password", type="password", placeholder="Min 8 characters")
            confirm_password = st.text_input("🔒 Confirm New Password", type="password", placeholder="Re-enter password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                reset_btn = st.form_submit_button("✅ Reset Password", use_container_width=True)
            
            with col_btn2:
                if st.form_submit_button("🔙 Back to Login", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()
            
            if reset_btn:
                if not token:
                    st.error("❌ Please provide reset token")
                elif not new_password or not confirm_password:
                    st.warning("⚠️ Please fill all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match!")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    with st.spinner("Resetting password..."):
                        response = make_request("POST", "/auth/reset-password", {
                            "token": token,
                            "new_password": new_password
                        }, auth=False)
                        
                        if handle_api_response(response, "✅ Password reset successful! Please login."):
                            time.sleep(2)
                            st.session_state.page = "login"
                            # Clear query params
                            st.query_params.clear()
                            st.rerun()

def chat_page():
    """Main chat interface"""
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Dashboard")
        
        # Get user info if not already loaded
        if not st.session_state.user_info:
            st.session_state.user_info = get_user_info()
        
        # User Profile Section
        if st.session_state.user_info:
            st.markdown("### 👤 Profile")
            st.info(f"**Email:** {st.session_state.user_info['email']}")
            if st.session_state.user_info.get('full_name'):
                st.info(f"**Name:** {st.session_state.user_info['full_name']}")
            
            # Stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Chats", len(st.session_state.messages))
            with col2:
                st.metric("📄 Files", st.session_state.uploaded_files_count)
        
        st.divider()
        
        # Document Upload Section
        st.markdown("### 📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Upload .docx file",
            type=['docx'],
            help="Upload a Word document to index"
        )
        
        if uploaded_file:
            if st.button("🚀 Upload & Index", use_container_width=True):
                with st.spinner("Processing document..."):
                    result = upload_document(uploaded_file)
                    if result:
                        st.success(f"✅ Indexed {result['indexed']}/{result['total_chunks']} chunks")
                        st.session_state.uploaded_files_count += 1
                        time.sleep(1)
                        st.rerun()
        
        st.divider()
        
        # RAG Settings
        st.markdown("### 🎛️ RAG Settings")
        top_k = st.slider(
            "Number of documents",
            min_value=1,
            max_value=10,
            value=5,
            help="How many similar documents to retrieve"
        )
        
        similarity_threshold = st.slider(
            "Similarity threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Minimum similarity score (0-1)"
        )
        
        st.divider()
        
        # Change Password
        with st.expander("🔐 Change Password"):
            with st.form("change_password_form"):
                old_pass = st.text_input("Old Password", type="password")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Change Password", use_container_width=True):
                    if new_pass != confirm_pass:
                        st.error("Passwords don't match!")
                    elif len(new_pass) < 8:
                        st.error("Password must be 8+ characters")
                    else:
                        change_password(old_pass, new_pass)
        
        st.divider()
        
        # Clear Chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_info = None
            st.session_state.messages = []
            st.session_state.page = "login"
            st.rerun()
    
    # Main Chat Area
    st.title("💬 RAG Chatbot")
    st.markdown("Ask me anything about your documents!")
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
                
                # Display sources if available
                if "sources" in message and message["sources"]:
                    with st.expander(f"📚 View {len(message['sources'])} Sources"):
                        for idx, source in enumerate(message["sources"], 1):
                            st.markdown(f"**Source {idx}:** `{source['source_file']}`")
                            st.caption(f"Similarity: {source['similarity']:.2%}")
                            st.text(source['content'])
                            if idx < len(message["sources"]):
                                st.divider()
    
    # Chat input
    if prompt := st.chat_input("💭 Ask me anything...", key="chat_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                response = send_chat_message(prompt, top_k, similarity_threshold)
                
                if response:
                    st.markdown(response["answer"])
                    
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
                    
                    # Display sources
                    if response.get("sources"):
                        with st.expander(f"📚 View {response['num_sources']} Sources"):
                            for idx, source in enumerate(response["sources"], 1):
                                st.markdown(f"**Source {idx}:** `{source['source_file']}`")
                                st.caption(f"Similarity: {source['similarity']:.2%}")
                                st.text(source['content'])
                                if idx < len(response["sources"]):
                                    st.divider()
                    
                    st.rerun()
                else:
                    st.error("Failed to get response. Please try again.")



# ===========================
# MAIN APP ROUTER
# ===========================

# def main():
#     """Main application router"""
    
#     # Check authentication
#     if st.session_state.access_token:
#         chat_page()
#     else:
#         if st.session_state.page == "login":
#             login_page()
#         elif st.session_state.page == "signup":
#             signup_page()
#         elif st.session_state.page == "forgot_password":
#             forgot_password_page()

# if __name__ == "__main__":
#     main()

def main():
    """Main application router"""
    
    # Check for reset token in URL
    query_params = st.query_params
    if hasattr(query_params, 'get'):
        if query_params.get("token"):
            st.session_state.page = "reset_password"
    elif isinstance(query_params, dict) and "token" in query_params:
        st.session_state.page = "reset_password"
    
    # Route to pages
    if st.session_state.access_token:
        chat_page()
    else:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "signup":
            signup_page()
        elif st.session_state.page == "forgot_password":
            forgot_password_page()
        elif st.session_state.page == "reset_password":
            reset_password_page()

if __name__ == "__main__":
    main()