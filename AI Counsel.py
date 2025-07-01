import streamlit as st
import io
import fitz  # PyMuPDF library, requires 'pip install PyMuPDF'

# --- SESSION STATE INITIALIZATION ---
# This must be at the top level of the script to initialize variables.
def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'home_dashboard'
    if 'cases' not in st.session_state:
        st.session_state.cases = {}
    if 'active_case_id' not in st.session_state:
        st.session_state.active_case_id = None

# --- PAGE CONFIGURATION ---
# This sets the browser tab's title and icon.
st.set_page_config(
    page_title="AI Counsel",
    page_icon="⚖️",
    layout="wide"
)

# --- HELPER FUNCTIONS (The App's Tools) ---

def display_home_dashboard():
    st.title("⚖️ My Cases")
    st.write("---")

    st.subheader("Start a New Case")
    new_case_title = st.text_input("Enter a title for your new case (e.g., 'Traffic Stop - Jan 5th')")
    
    if st.button("➕ Create New Case", type="primary"):
        if new_case_title:
            case_id = f"AIC-{len(st.session_state.cases) + 1:03d}"
            st.session_state.cases[case_id] = {
                "title": new_case_title, "case_id": case_id, "timeline": [],
                "evidence": {}, "persons": []
            }
            st.success(f"Successfully created case '{new_case_title}' with ID {case_id}")
            st.experimental_rerun()
        else:
            st.warning("Please enter a title for your case.")

    st.write("---")
    st.subheader("Existing Cases")

    if not st.session_state.cases:
        st.info("You have no cases yet. Create one above to get started.")
    else:
        # Display headers for the case list
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.markdown("**Case Title**")
        col2.markdown("**Case ID**")
        col3.markdown("**Action**")

        # Loop through all cases and display them
        for case_id, case_data in st.session_state.cases.items():
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(case_data['title'])
            c2.write(case_data['case_id'])
            if c3.button("Open", key=f"open_{case_id}"):
                st.session_state.active_case_id = case_id
                st.session_state.page = 'case_workspace'
                st.experimental_rerun()

def display_case_workspace():
    if not st.session_state.active_case_id:
        st.session_state.page = 'home_dashboard'
        st.experimental_rerun()
        return

    active_case_data = st.session_state.cases[st.session_state.active_case_id]

    # Top bar with case info and back button
    col1, col2 = st.columns([4, 1])
    col1.title(f"Case: {active_case_data['title']}")
    col1.caption(f"Internal ID: {active_case_data['case_id']}")
    if col2.button("<-- Back to My Cases"):
        st.session_state.active_case_id = None
        st.session_state.page = 'home_dashboard'
        st.experimental_rerun()
    st.write("---")

    # Sidebar for navigation within the case
    with st.sidebar:
        st.title("AI Counsel")
        st.subheader("Toolbox")
        options_list = ["📊 Dashboard", "⏳ Factual Timeline", "🗄️ Evidence Locker", "👥 Persons & Entities", "⚖️ Sources & Statutes", "✍️ Documents & Drafts", "📈 Incident Log", "📝 Case Notes"]
        selected_tab = st.radio("Navigation", options=options_list, key="navigation_radio")

    # Main content area based on sidebar selection
    if selected_tab == "📊 Dashboard":
        display_dashboard_tab(active_case_data)
    else:
        st.header(f"📍 You are in the {selected_tab} tab.")
        st.info("This content has not been built yet.")
        st.subheader("Current Case Data (For Debugging)")
        st.json(active_case_data)

def display_dashboard_tab(case_data):
    st.header("Module A: Case Genesis")
    st.info("Begin by uploading your case files (e.g., Police Reports). PDF format is supported.")

    uploaded_files = st.file_uploader(
        "Upload documents here", type=['pdf'], accept_multiple_files=True,
        key=f"uploader_{case_data['case_id']}"
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in case_data["evidence"]:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        pdf_document = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
                        extracted_text = "".join([page.get_text() for page in pdf_document])
                        pdf_document.close()

                        case_data["evidence"][uploaded_file.name] = {
                            "file_name": uploaded_file.name,
                            "file_type": uploaded_file.type,
                            "file_size": uploaded_file.size,
                            "extracted_text": extracted_text
                        }
                        st.success(f"✅ Successfully processed {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")
        
        if case_data["evidence"]:
            st.write("---")
            st.subheader("Processed Evidence")
            for file_name, file_data in case_data["evidence"].items():
                with st.expander(f"View Extracted Text from '{file_name}'"):
                    st.text_area("", value=file_data["extracted_text"], height=300, disabled=True, key=f"text_{file_name}")

# --- MAIN APPLICATION LOGIC ---
# This is the "traffic cop" that decides which page to show.

def main():
    initialize_session_state()
    if st.session_state.page == 'home_dashboard':
        display_home_dashboard()
    elif st.session_state.page == 'case_workspace':
        display_case_workspace()
    else:
        # Default to home if state is corrupted
        st.session_state.page = 'home_dashboard'
        st.experimental_rerun()

if __name__ == "__main__":
    main()
              
