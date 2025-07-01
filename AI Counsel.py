import streamlit as st
import datetime
import fitz  # PyMuPDF library

# --- SESSION STATE INITIALIZATION ---
def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'home_dashboard'
    if 'cases' not in st.session_state:
        st.session_state.cases = {}
    if 'active_case_id' not in st.session_state:
        st.session_state.active_case_id = None

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Counsel",
    page_icon="âš–ï¸",
    layout="wide"
)

# --- HOME DASHBOARD: Case creation and listing ---
def display_home_dashboard():
    st.title("âš–ï¸ My Cases")
    st.write("---")
    st.subheader("Start a New Case")
    new_case_title = st.text_input("Enter a title for your new case (e.g., 'Traffic Stop - Jan 5th')")

    if st.button("âž• Create New Case", type="primary"):
        if new_case_title:
            case_id = f"AIC-{len(st.session_state.cases) + 1:03d}"
            st.session_state.cases[case_id] = {
                "title": new_case_title,
                "case_id": case_id,
                "created_at": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat(),
                "facts": [],
                "evidence": {},
                "persons": [],
                "notes": [],
                "tasks": [],
                "sources": [],
                "incident_log": [],
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
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.markdown("**Case Title**")
        col2.markdown("**Case ID**")
        col3.markdown("**Action**")
        for case_id, case_data in st.session_state.cases.items():
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(case_data['title'])
            c2.write(case_data['case_id'])
            if c3.button("Open", key=f"open_{case_id}"):
                st.session_state.active_case_id = case_id
                st.session_state.page = 'case_workspace'
                st.experimental_rerun()

# --- CASE WORKSPACE: Main navigation and tab logic ---
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

    # Sidebar navigation for the case modules
    with st.sidebar:
        st.title("AI Counsel")
        st.subheader("Toolbox")
        options_list = [
            "ðŸ“Š Dashboard",
            "â³ Factual Timeline",
            "ðŸ—„ï¸ Evidence Locker",
            "ðŸ‘¥ Persons & Entities",
            "âš–ï¸ Sources & Statutes",
            "âœï¸ Documents & Drafts",
            "ðŸ“ˆ Incident Log",
            "ðŸ“ Case Notes",
        ]
        selected_tab = st.radio("Navigation", options=options_list, key="navigation_radio")

    # Main content area based on selected tab
    if selected_tab == "ðŸ“Š Dashboard":
        display_dashboard_tab(active_case_data)
    elif selected_tab == "â³ Factual Timeline":
        display_timeline_tab(active_case_data)
    elif selected_tab == "ðŸ—„ï¸ Evidence Locker":
        display_evidence_tab(active_case_data)
    elif selected_tab == "ðŸ‘¥ Persons & Entities":
        display_persons_tab(active_case_data)
    elif selected_tab == "âš–ï¸ Sources & Statutes":
        display_sources_tab(active_case_data)
    elif selected_tab == "âœï¸ Documents & Drafts":
        display_documents_tab(active_case_data)
    elif selected_tab == "ðŸ“ˆ Incident Log":
        display_incident_log_tab(active_case_data)
    elif selected_tab == "ðŸ“ Case Notes":
        display_case_notes_tab(active_case_data)
    else:
        st.header(f"ðŸ“ You are in the {selected_tab} tab.")
        st.info("This content has not been built yet.")
        st.subheader("Current Case Data (For Debugging)")
        st.json(active_case_data)

# --- DASHBOARD TAB: File upload ---
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
                            "extracted_text": extracted_text,
                            "uploaded_at": datetime.datetime.now().isoformat(),
                        }
                        st.success(f"âœ… Successfully processed {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

        if case_data["evidence"]:
            st.write("---")
            st.subheader("Processed Evidence")
            for file_name, file_data in case_data["evidence"].items():
                with st.expander(f"View Extracted Text from '{file_name}'"):
                    st.text_area("", value=file_data["extracted_text"], height=300, disabled=True, key=f"text_{file_name}")

# --- FACT TIMELINE TAB: Manual fact entry and display ---
def display_timeline_tab(case_data):
    st.header("â³ Factual Timeline (Manual Fact Entry)")

    st.info("Enter key facts or events for your case below. Future: This can be automated using open-source AI models.")

    # Show existing timeline
    if case_data["facts"]:
        st.subheader("Current Timeline")
        for i, fact in enumerate(case_data["facts"]):
            with st.expander(f"{i+1}. {fact['event'][:60]}..."):
                st.markdown(f"**Date:** {fact.get('date', 'N/A')}")
                st.markdown(f"**People:** {', '.join(fact.get('people', [])) or 'N/A'}")
                st.markdown(f"**Evidence:** {', '.join(fact.get('evidence', [])) or 'N/A'}")
                st.markdown("> " + fact.get('source_text', ''))
                if st.button("Delete", key=f"del_fact_{i}"):
                    case_data["facts"].pop(i)
                    st.experimental_rerun()
    else:
        st.info("No timeline facts added yet.")

    st.write("---")
    st.subheader("Add a New Fact/Event")
    with st.form("manual_fact_entry"):
        event = st.text_input("Event / Fact (short description)")
        date = st.text_input("Date (YYYY-MM-DD or leave blank)", value="")
        people = st.text_input("People/entities involved (comma separated)")
        evidence = st.text_input("Evidence (file names, comma separated)")
        source_text = st.text_area("Relevant excerpt / notes (optional)")
        submit = st.form_submit_button("Add Fact")
        if submit:
            if event:
                fact = {
                    "event": event,
                    "date": date if date else None,
                    "people": [p.strip() for p in people.split(",")] if people else [],
                    "evidence": [e.strip() for e in evidence.split(",")] if evidence else [],
                    "source_text": source_text
                }
                case_data["facts"].append(fact)
                st.success("Fact added!")
                st.experimental_rerun()
            else:
                st.warning("Event/Fact description is required.")

# --- PLACEHOLDER FUNCTIONS FOR ALL OTHER TABS ---

def display_evidence_tab(case_data):
    st.header("ðŸ—„ï¸ Evidence Locker")
    st.info("View, manage, and link evidence files here. (Feature coming soon!)")

def display_persons_tab(case_data):
    st.header("ðŸ‘¥ Persons & Entities")
    st.info("All people and organizations involved in your case will be listed here. (Feature coming soon!)")

def display_sources_tab(case_data):
    st.header("âš–ï¸ Sources & Statutes")
    st.info("Your case's library of statutes, laws, and court cases will appear here. (Feature coming soon!)")

def display_documents_tab(case_data):
    st.header("âœï¸ Documents & Drafts")
    st.info("Draft, review, and export court documents here. (Feature coming soon!)")

def display_incident_log_tab(case_data):
    st.header("ðŸ“ˆ Incident Log")
    st.info("Keep a log of important post-filing incidents and deadlines here. (Feature coming soon!)")

def display_case_notes_tab(case_data):
    st.header("ðŸ“ Case Notes")
    st.info("Your private notepad for thoughts, theories, and findings. (Feature coming soon!)")

# --- MAIN APP LOGIC ---
def main():
    initialize_session_state()
    if st.session_state.page == 'home_dashboard':
        display_home_dashboard()
    elif st.session_state.page == 'case_workspace':
        display_case_workspace()
    else:
        st.session_state.page = 'home_dashboard'
        st.experimental_rerun()

if __name__ == "__main__":
    main()
