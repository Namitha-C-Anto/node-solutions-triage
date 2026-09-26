import streamlit as st
from triage import triage_request

MOCK_REQUESTS = {
    "01 - Automation inquiry": "Our team has 40 employees entering the same customer details into three systems. Could you show us how this might be automated? We would like to speak next week.",
    "02 - Portal outage": "The client portal has been unavailable since this morning and our staff cannot access active customer records. Please help as soon as possible.",
    "03 - Duplicate invoice charge": "Invoice NS-1048 appears to include the same implementation charge twice. Can someone review it before payment is processed Friday?",
    "04 - Dark mode feature request": "Can you add dark mode and change the dashboard font? There is no deadline. I am collecting ideas for a future update.",
    "05 - Accidental data exposure": "We accidentally uploaded a spreadsheet containing customer contact information to the wrong workspace. We need immediate help removing access.",
    "06 - Pricing inquiry": "I saw your company online and am interested in a custom AI reporting system. What would pricing and a typical timeline look like?",
}

PRIORITY_COLORS = {
    "Urgent": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
}

st.set_page_config(page_title="AI Request Triage Assistant", page_icon="📥", layout="centered")

st.title("📥 AI Request Triage Assistant")
st.caption("Paste an incoming client request to get a summary, priority, routing, and a draft first response.")

with st.sidebar:
    st.header("Try a mock request")
    selected = st.selectbox("Pick one to load into the box:", ["-- none --"] + list(MOCK_REQUESTS.keys()))
    if selected != "-- none --":
        st.session_state["request_text"] = MOCK_REQUESTS[selected]

request_text = st.text_area(
    "Incoming request",
    key="request_text",
    height=150,
    placeholder="Paste or type the client's request here...",
)

if st.button("Triage request", type="primary", disabled=not request_text.strip()):
    with st.spinner("Analyzing request..."):
        try:
            result = triage_request(request_text)
            st.session_state["result"] = result
        except Exception as e:
            st.error(f"Something went wrong while triaging this request: {e}")
            st.session_state["result"] = None

if st.session_state.get("result"):
    result = st.session_state["result"]

    st.divider()
    st.subheader("Summary")
    st.write(result.summary)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Category", result.category)
    with col2:
        st.metric("Priority", f"{PRIORITY_COLORS.get(result.priority, '')} {result.priority}")
    with col3:
        st.metric("Routed to", result.routed_to)

    st.caption(f"**Why this priority:** {result.priority_reason}")

    st.subheader("Draft first response")
    st.text_area("Editable draft — review before sending", value=result.draft_response, height=200)