import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def render_connections(memories):
    """
    Render the connections between memories.
    
    Args:
        memories (list): List of memory dictionaries
    """
    st.markdown("<h2 class='timeline-header'>Memory Connections</h2>", unsafe_allow_html=True)
    
    if not memories:
        st.info("No memories to display in connections view. Try indexing some content or modifying your search.")
        return
    
    # Create a graph
    G = nx.Graph()
    
    # Add nodes for each memory
    memory_limit = min(20, len(memories))  # Limit to 20 for performance
    
    for i, memory in enumerate(memories[:memory_limit]):
        if 'title' not in memory:
            continue
            
        memory_type = memory.get('type', 'document')
        G.add_node(i, type=memory_type, title=memory.get('title', f"Memory {i}"))
    
    # Add connections based on content similarity, entities, or dates
    # This is a simplified example - in a real implementation, you would use 
    # semantic similarity to create meaningful connections
    
    # For demo purposes, create connections between memories of the same type
    # and between memories with close dates
    memory_types = {}
    for i, memory in enumerate(memories[:memory_limit]):
        if i not in G:
            continue
            
        memory_type = memory.get('type', 'document')
        if memory_type not in memory_types:
            memory_types[memory_type] = []
        memory_types[memory_type].append(i)
        
        # Connect by date proximity if date exists
        if 'date' in memory:
            try:
                current_date = pd.to_datetime(memory['date'])
                for j, other_memory in enumerate(memories[:memory_limit]):
                    if i != j and j in G and 'date' in other_memory:
                        other_date = pd.to_datetime(other_memory['date'])
                        # If memories are within 7 days of each other
                        if abs((current_date - other_date).days) <= 7:
                            G.add_edge(i, j, weight=1, relationship="time")
            except (ValueError, AttributeError):
                continue
    
    # Connect memories of the same type
    for memory_type, indices in memory_types.items():
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                G.add_edge(indices[i], indices[j], weight=2, relationship="type")
    
    # Visualize the graph if it has nodes
    if G.number_of_nodes() > 0:
        # Generate positions for nodes
        pos = nx.spring_layout(G, seed=42)
        
        # Create edge traces
        edge_trace = go.Scatter(
            x=[], y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)
        
        # Create node traces
        node_traces = []
        
        # Different node trace for each memory type
        node_colors = {
            'document': '#3E7CB9',
            'image': '#FF924C',
            'audio': '#8867CA',
            'web': '#71D999'
        }
        
        # Create a trace for each node
        for node in G.nodes():
            node_type = G.nodes[node]['type']
            node_color = node_colors.get(node_type, '#3E7CB9')
            
            node_trace = go.Scatter(
                x=[pos[node][0]],
                y=[pos[node][1]],
                mode='markers',
                marker=dict(
                    size=15,
                    color=node_color,
                    line_width=2,
                    line=dict(color='white')
                ),
                text=[G.nodes[node]['title']],
                hoverinfo='text'
            )
            
            node_traces.append(node_trace)
        
        # Create the figure
        fig = go.Figure(
            data=[edge_trace] + node_traces,
            layout=go.Layout(
                title='Memory Connections Network',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600,
                plot_bgcolor='rgba(0,0,0,0)'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No connections to display with the current memories.")