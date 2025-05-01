import streamlit as st

def render_search_box():
    """
    Render the search box and return the search query.
    
    Returns:
        str: The search query or None if no search was performed
    """
    col1, col2 = st.columns([5,1])
    
    with col1:
        search_query = st.text_input("", 
                                     placeholder="Ask me anything about your digital memories...", 
                                     label_visibility="collapsed", 
                                     key="search_box")
    
    with col2:
        search_button = st.button("🔍 Search")
    
    if search_button and search_query:
        return search_query
    
    return None