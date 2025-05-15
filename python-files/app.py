import streamlit as st
import re
import time

# Configure page
st.set_page_config(
    page_title="Malicious Code Detector",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Apply styles based on dark mode
def get_styles():
    if st.session_state.dark_mode:
        return """
        <style>
        @keyframes fadeBackgroundDark {
            from { 
                background: linear-gradient(135deg, #ffffff, #a3dfff, #7dd3fc);
                color: #000000;
            }
            to { 
                background: linear-gradient(135deg, #0f2027, #233940, #2c5364);
                color: #e0e0e0;
            }
        }
        
        .stApp {
            background: linear-gradient(135deg, #0f2027, #233940, #2c5364);
            color: #e0e0e0;
            animation: fadeBackgroundDark 0.8s ease-in-out;
        }
        
        @keyframes fadeTextAreaDark {
            from {
                background-color: #fff;
                color: #000;
                border-color: #aaa;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            to {
                background-color: #2c3e50;
                color: #ddd;
                border-color: #555;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }
        }
        
        .stTextArea > div > div > textarea {
            background-color: #2c3e50;
            color: #ddd;
            border-color: #555;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            animation: fadeTextAreaDark 0.7s ease-in-out;
        }
        
        @keyframes fadeButtonDark {
            from {
                background-color: #00aaff;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            to {
                background-color: #3399ff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }
        }
        
        .danger {
            color: #ff6f6f;
            font-weight: 600;
        }
        .safe {
            color: #81c784;
            font-weight: 600;
        }
        .stButton button {
            background-color: #3399ff;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            animation: fadeButtonDark 0.6s ease-in-out;
        }
        .stButton button:hover {
            background-color: #1e88e5;
        }
        </style>
        """
    else:
        return """
        <style>
        @keyframes fadeBackgroundLight {
            from {
                background: linear-gradient(135deg, #0f2027, #233940, #2c5364);
                color: #e0e0e0;
            }
            to {
                background: linear-gradient(135deg, #ffffff, #a3dfff, #7dd3fc);
                color: #000000;
            }
        }
        
        .stApp {
            background: linear-gradient(135deg, #ffffff, #a3dfff, #7dd3fc);
            color: #000000;
            animation: fadeBackgroundLight 0.8s ease-in-out;
        }
        
        @keyframes fadeTextAreaLight {
            from {
                background-color: #2c3e50;
                color: #ddd;
                border-color: #555;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }
            to {
                background-color: #fff;
                color: #000;
                border-color: #aaa;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        }
        
        .stTextArea > div > div > textarea {
            background-color: #fff;
            color: #000;
            border-color: #aaa;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            animation: fadeTextAreaLight 0.7s ease-in-out;
        }
        
        @keyframes fadeButtonLight {
            from {
                background-color: #3399ff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }
            to {
                background-color: #00aaff;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
        }
        
        .danger {
            color: #d32f2f;
            font-weight: 600;
        }
        .safe {
            color: #388e3c;
            font-weight: 600;
        }
        .stButton button {
            background-color: #00aaff;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: fadeButtonLight 0.6s ease-in-out;
        }
        .stButton button:hover {
            background-color: #008ecc;
        }
        </style>
        """

# Apply the styles
st.markdown(get_styles(), unsafe_allow_html=True)

# Create animated heading using HTML/CSS
def animated_heading(text):
    html = f"""
    <style>
    #animatedHeading {{
        font-size: 28px;
        font-weight: bold;
        display: inline-block;
        white-space: pre-wrap;
        margin-bottom: 10px;
    }}
    .letter {{
        opacity: 0;
        transform: translateY(10px);
        display: inline-block;
        animation: fadeInUp 0.4s forwards;
    }}
    @keyframes fadeInUp {{
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    </style>
    <div id="animatedHeading">
    """
    
    for i, char in enumerate(text):
        if char == ' ':
            html += f'<span class="letter" style="animation-delay:{i*50}ms">&nbsp;</span>'
        else:
            html += f'<span class="letter" style="animation-delay:{i*50}ms">{char}</span>'
    
    html += "</div>"
    return html

# Function to create animated message
def create_animated_message(message, class_name=""):
    html = f"""
    <p class="{class_name}">
    """
    
    for i, char in enumerate(message):
        if char == ' ':
            html += f'<span class="letter" style="animation-delay:{i*30}ms">&nbsp;</span>'
        else:
            html += f'<span class="letter" style="animation-delay:{i*30}ms">{char}</span>'
    
    html += "</p>"
    return html

# Toggle dark mode with improved button
col1, col2 = st.columns([1, 9])
with col1:
    theme_icon = "🌒" if st.session_state.dark_mode else "🌔"
    theme_text = f"{theme_icon} {('Light Mode' if st.session_state.dark_mode else 'Dark Mode')}"
    if st.button(theme_text):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Display animated heading
st.markdown(animated_heading("Malicious Code Detector"), unsafe_allow_html=True)
st.markdown("Paste your code below to check for potentially dangerous patterns:")

# Define suspicious patterns (directly from original HTML)
suspicious_patterns = [
    {"pattern": r"eval\s*\(", "message": "⚠️ Use of eval() can execute arbitrary code"},
    {"pattern": r"document\.write\s*\(", "message": "⚠️ Use of document.write() is risky"},
    {"pattern": r"new Function\s*\(", "message": "⚠️ Use of Function constructor is dangerous"},
    {"pattern": r"setTimeout\s*\(.+?,\s*[\"']?\d{3,}[\"']?\)", "message": "⚠️ setTimeout with long delay can hide malicious actions"},
    {"pattern": r"fetch\s*\(.+?http", "message": "⚠️ External fetch call detected"},
    {"pattern": r"navigator\.clipboard", "message": "⚠️ Access to clipboard detected"},
    {"pattern": r"addEventListener\s*\(\s*['\"]key", "message": "⚠️ Possible keylogger using key events"},
    {"pattern": r"XMLHttpRequest", "message": "⚠️ Use of XMLHttpRequest may be used for hidden network requests"},
    {"pattern": r"WebSocket", "message": "⚠️ WebSocket connection detected (could be used for data exfiltration)"},
    {"pattern": r"window\.location\s*=", "message": "⚠️ Script redirect detected via window.location"},
    {"pattern": r"document\.cookie", "message": "⚠️ Access to cookies detected"},
    {"pattern": r"localStorage\.setItem", "message": "⚠️ LocalStorage modification detected (may be used for persistence)"},
    {"pattern": r"window\.onerror", "message": "⚠️ Global error handler detected (may hide errors maliciously)"},
    {"pattern": r"atob\s*\(", "message": "⚠️ Use of atob() - often used to decode encoded payloads"},
    {"pattern": r"btoa\s*\(", "message": "⚠️ Use of btoa() - often used to encode data"},
    {"pattern": r"innerHTML\s*=", "message": "⚠️ Direct innerHTML assignment - risk of XSS"},
    {"pattern": r"fetch\s*\(.*document\.cookie", "message": "⚠️ Possible cookie stealing via fetch detected"},
    {"pattern": r"\\x[0-9a-f]{2}", "message": "⚠️ Hex-encoded escape sequences detected (often used for obfuscation)"},
    {"pattern": r"serviceWorker\.register\s*\(", "message": "⚠️ Service worker registration detected (persistent background code)"},
    {"pattern": r"RTCPeerConnection", "message": "⚠️ WebRTC detected (possible local IP leaking)"},
    {"pattern": r"\\u[0-9a-f]{4}", "message": "⚠️ Unicode escape sequences detected (possible obfuscation)"},
    {"pattern": r"eval\s*\(\s*function\s*\(", "message": "⚠️ Self-invoking eval function detected (common in obfuscated code)"},
    {"pattern": r"while\s*\(true\)", "message": "⚠️ Infinite loop detected (could freeze or crash browser)"},
    {"pattern": r"setInterval\s*\(\s*eval", "message": "⚠️ eval inside setInterval (persistent malicious execution)"},
    {"pattern": r"document\.createElement\s*\(\s*['\"]script['\"]\s*\)", "message": "⚠️ Dynamic script creation detected"},
    {"pattern": r"appendChild\s*\(\s*document\.createTextNode", "message": "⚠️ Dynamic code injection via appendChild and createTextNode"},
    {"pattern": r"Object\.prototype\.", "message": "⚠️ Prototype manipulation detected (can alter fundamental JS behavior)"},
    {"pattern": r"new Function\s*\(\s*(['\"(`])(?:\\.|[^\\])*?\1\s*\)", "message": "⚠️ Dynamic function constructor with obfuscated string detected"},
    {"pattern": r"window\.atob\s*\(", "message": "⚠️ Use of atob() often seen in decoding malicious payloads"},
    {"pattern": r"window\.btoa\s*\(", "message": "⚠️ Use of btoa() often seen in encoding data for exfiltration"},
    {"pattern": r"CryptoJS|crypto\.subtle", "message": "⚠️ Use of CryptoJS or Web Crypto API (may be encrypting/decrypting malicious payloads)"},
    {"pattern": r"document\.documentElement\.innerHTML\s*=", "message": "⚠️ Overwriting entire document HTML - common in defacement or phishing"},
    {"pattern": r"window\.open\s*\(\s*['\"]about:blank['\"]\s*\)", "message": "⚠️ Opening blank popup window (used to hide malicious activity)"},
    {"pattern": r"indexedDB\.open", "message": "⚠️ IndexedDB access detected (can be used for stealthy local persistence)"},
    {"pattern": r"serviceWorker\.register", "message": "⚠️ Service Worker registration detected (can persist background malicious scripts)"},
    {"pattern": r"element\.innerHTML\s*=", "message": "⚠️ Direct innerHTML assignment on element (risk of DOM-based XSS)"},
    {"pattern": r"setTimeout\s*\(\s*['\"(`]", "message": "⚠️ String argument in setTimeout can be used to run code dynamically"},
    {"pattern": r"['\"(`]([A-Za-z0-9+/=]{50,})['\"(`]", "message": "⚠️ Long base64 strings detected - may hide payloads"},
    {"pattern": r"var\s+iframe\s*=\s*document\.createElement\(['\"(`]iframe['\"(`]\)", "message": "⚠️ Creation of iframe element detected"},
    {"pattern": r"iframe\.style\.width\s*=\s*[\"']0px[\"']", "message": "⚠️ Invisible iframe detected (width=0px)"},
    {"pattern": r"iframe\.style\.height\s*=\s*[\"']0px[\"']", "message": "⚠️ Invisible iframe detected (height=0px)"},
    {"pattern": r"iframe\.style\.border\s*=\s*[\"']none[\"']", "message": "⚠️ Invisible iframe detected (border=none)"},
    {"pattern": r"iframe\.src\s*=\s*[\"']https?:\/\/[^\"']+[\"']", "message": "⚠️ iframe loading external URL detected"},
    {"pattern": r"document\.body\.appendChild\(iframe\)", "message": "⚠️ Appending iframe to body detected"},
    {"pattern": r"location\.href\s*=", "message": "⚠️ Redirecting via location.href"},
    {"pattern": r"location\.replace\s*\(", "message": "⚠️ Redirecting via location.replace()"},
    {"pattern": r"document\.referrer", "message": "⚠️ Accessing referrer information"},
    {"pattern": r"\.click\s*\(", "message": "⚠️ Programmatic click simulation"},
    {"pattern": r"\.submit\s*\(", "message": "⚠️ Programmatic form submission"},
    {"pattern": r"['\"]javascript:['\"]", "message": "⚠️ JavaScript URI scheme detected"},
    {"pattern": r"navigator\.sendBeacon", "message": "⚠️ Using sendBeacon API (could send data without user knowledge)"},
    {"pattern": r"\.postMessage", "message": "⚠️ Cross-window communication with postMessage"},
    {"pattern": r"window\.parent", "message": "⚠️ Accessing parent window (potential frame communication)"},
    {"pattern": r"console\.clear", "message": "⚠️ Clearing console (potential attempt to hide messages)"},
    {"pattern": r"debugger;", "message": "⚠️ Debugger statement detected"},
    {"pattern": r"encodeURIComponent\s*\(\s*document\.cookie", "message": "⚠️ Encoding cookie data (potential exfiltration)"},
    {"pattern": r"window\.name", "message": "⚠️ Accessing window.name (can be used for cross-origin data passing)"},
    {"pattern": r"Math\.random\s*\(\s*\)\s*\.\s*toString\s*\(\s*36\s*\)", "message": "⚠️ Random string generation (often for obfuscation)"}
]

# Code input
code_input = st.text_area("", height=250, placeholder="Paste your code here...")

# Check button
if st.button("Check Code"):
    if code_input.strip():
        # Create a container for the results
        results_container = st.container()
        
        with results_container:
            # Clear existing content
            st.empty()
            
            # Check for suspicious patterns
            found = False
            pattern_results = []
            
            # Add a small delay for animation effect
            time.sleep(0.3)
            
            # Show loading animation while scanning
            with st.spinner('Scanning for suspicious patterns...'):
                for item in suspicious_patterns:
                    pattern = re.compile(item["pattern"], re.IGNORECASE)
                    if pattern.search(code_input):
                        found = True
                        pattern_results.append(create_animated_message(item["message"], "danger"))
            
            # Display results with animation
            if found:
                for result in pattern_results:
                    st.markdown(result, unsafe_allow_html=True)
                    # Add a small delay between messages for nicer appearance
                    time.sleep(0.1)
            else:
                st.markdown(create_animated_message("✅ No known malicious patterns detected.", "safe"), unsafe_allow_html=True)
    else:
        st.warning("Please enter some code to check!")

# Add information about the tool
with st.expander("About this tool"):
    st.markdown("""
    **Malicious Code Detector** is a tool that helps identify potentially dangerous JavaScript patterns that could 
    indicate malicious code. It scans for known techniques used in:
    
    - Code injection attacks
    - Cross-site scripting (XSS)
    - Data exfiltration
    - Obfuscated malicious code
    - DOM manipulation attacks
    
    *This tool provides a first-pass analysis and shouldn't replace a thorough security review.*
    """)

# Add footer
st.markdown("---")
st.markdown("Created for code security analysis, You dont have to be strict on this tool, but it can help you to find some issues. But if you find a website that looks suspicious, please report it to microsoft. Thank you for reading this.")
