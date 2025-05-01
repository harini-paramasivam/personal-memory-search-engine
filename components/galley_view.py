import streamlit as st

def render_gallery(memories):
    """
    Render the gallery view of memories.
    
    Args:
        memories (list): List of memory dictionaries
    """
    st.markdown("<h2 class='timeline-header'>Memory Gallery</h2>", unsafe_allow_html=True)
    
    if not memories:
        st.info("No memories to display in gallery. Try indexing some content or modifying your search.")
        return
    
    # Display memories in a grid
    memory_limit = min(9, len(memories))  # Limit to 9 for the gallery view
    
    for i, memory in enumerate(memories[:memory_limit]):
        if i % 3 == 0:
            cols = st.columns(3)
        
        with cols[i % 3]:
            # Default to document type if not specified
            memory_type = memory.get('type', 'document')
            memory_class = f"memory-card memory-{memory_type}"
            
            # Create a card for the memory
            st.markdown(f"<div class='{memory_class}'>", unsafe_allow_html=True)
            
            st.markdown(f"#### {memory.get('title', 'Untitled Memory')}")
            
            # Format date if available
            if 'date' in memory:
                try:
                    if isinstance(memory['date'], str):
                        date_str = memory['date']
                    else:
                        date_str = memory['date'].strftime('%B %d, %Y')
                    
                    st.markdown(f"*{date_str}*")
                except (ValueError, AttributeError):
                    pass
            
            # Show content excerpt
            content = memory.get('content', '')
            if content:
                if len(content) > 200:
                    content = content[:200] + "..."
                st.markdown(content)
            
            # Display entity tags if available
            if 'entities' in memory and memory['entities']:
                for entity in memory['entities']:
                    entity_type = entity.get('type', 'unknown')
                    entity_text = entity.get('text', entity)
                    if isinstance(entity, str):
                        entity_type = entity
                        entity_text = entity
                        
                    st.markdown(f"<span class='entity-pill entity-{entity_type}'>{entity_text}</span>", 
                               unsafe_allow_html=True)
            
            # Show image preview for image type
            if memory_type == 'image' and 'file_path' in memory:
                try:
                    st.image(memory['file_path'], use_column_width=True)
                except:
                    st.warning("Image preview not available")
            
            st.markdown("</div>", unsafe_allow_html=True)