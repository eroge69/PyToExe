import streamlit as st
import threading
import time
import os
from key_monitor import KeyMonitor
from browser_controller import BrowserController

# Set page title and favicon
st.set_page_config(
    page_title="Google Search Assistant",
    page_icon="🔍",
    layout="centered"
)

# Initialize session state variables if they don't exist
if 'monitor_running' not in st.session_state:
    st.session_state.monitor_running = False
if 'status_message' not in st.session_state:
    st.session_state.status_message = "Waiting to start..."
if 'browser_controller' not in st.session_state:
    st.session_state.browser_controller = None
if 'key_monitor' not in st.session_state:
    st.session_state.key_monitor = None

def update_status(message):
    """Update the status message and trigger a rerun"""
    st.session_state.status_message = message
    st.rerun()

def start_monitoring():
    """Start the key monitoring process"""
    if st.session_state.monitor_running:
        return
    
    try:
        # Initialize browser controller
        st.session_state.browser_controller = BrowserController()
        
        # Initialize key monitor
        st.session_state.key_monitor = KeyMonitor(
            callback=st.session_state.browser_controller.click_search_button
        )
        
        # Start monitoring
        st.session_state.key_monitor.start()
        st.session_state.monitor_running = True
        update_status("Monitoring active: Press 'Trigger Search' to click the Google search button")
    except Exception as e:
        update_status(f"Error starting monitor: {str(e)}")

def stop_monitoring():
    """Stop the key monitoring process"""
    if not st.session_state.monitor_running:
        return
    
    try:
        # Stop the key monitor
        if st.session_state.key_monitor:
            st.session_state.key_monitor.stop()
        
        # Close the browser controller
        if st.session_state.browser_controller:
            st.session_state.browser_controller.close()
        
        st.session_state.monitor_running = False
        st.session_state.key_monitor = None
        st.session_state.browser_controller = None
        update_status("Monitoring stopped")
    except Exception as e:
        update_status(f"Error stopping monitor: {str(e)}")
        
def trigger_search():
    """Manually trigger the search button click"""
    if not st.session_state.monitor_running or not st.session_state.key_monitor:
        update_status("Start monitoring first before triggering search")
        return
        
    if st.session_state.key_monitor.trigger_manually():
        update_status("Search button click triggered!")
    else:
        update_status("Could not trigger search. Please ensure monitoring is active.")

# App header
st.title("Google Search Assistant")
st.markdown("""
This application helps you automatically click the Google search button when you press the 'Trigger Search' button.
""")

# Status indicator
st.subheader("Status")
status_indicator = st.empty()
status_indicator.info(st.session_state.status_message)

# Control buttons
col1, col2, col3 = st.columns(3)
with col1:
    if not st.session_state.monitor_running:
        if st.button("Start Monitoring", use_container_width=True):
            start_monitoring()
with col2:
    if st.session_state.monitor_running:
        if st.button("Trigger Search", use_container_width=True):
            trigger_search()
with col3:
    if st.session_state.monitor_running:
        if st.button("Stop Monitoring", use_container_width=True):
            stop_monitoring()

# Instructions
st.subheader("How to use")
st.markdown("""
1. Click **Start Monitoring** to begin the process
2. Open Google Chrome and navigate to Google.com
3. Type your search query in the search box
4. Click **Trigger Search** and the application will automatically click the Google search button
5. Click **Stop Monitoring** when you're done
""")

# Technical information
with st.expander("Technical Information"):
    st.markdown("""
    - This application uses Selenium WebDriver to control Chrome browser.
    - Make sure Chrome browser is installed on your system.
    - The application communicates with Chrome to find and click the search button.
    """)

# Always display a footer
st.markdown("---")
st.caption("This application requires Chrome browser to function properly.")

# Clean up when the app is closed
def cleanup():
    if st.session_state.monitor_running:
        stop_monitoring()

# Register cleanup function for when the app is closed
import atexit
atexit.register(cleanup)
