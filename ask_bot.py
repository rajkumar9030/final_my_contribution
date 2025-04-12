import streamlit as st
import google.generativeai as genai
from graphviz import Digraph
import textwrap
import re

# 🔐 Gemini API key
GEMINI_API_KEY = "AIzaSyDJ1tewK5Hpt-DrLhT67NLCmj7AcvXnRHc"

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"❌ Failed to configure Gemini: {str(e)}")
    st.stop()

# 🌳 Enhanced Tree Diagram Generator
def create_tree_diagram(title, points):
    try:
        dot = Digraph(comment='AgriBot Diagram')
        dot.attr(rankdir='TB', size='12,14')
        dot.attr('node', shape='box', style='filled', 
                fillcolor='#E8F5E9', fontname='Arial', 
                fontsize='14', margin='0.3', width='1.5', height='0.5')
        
        wrapped_title = "\n".join(textwrap.wrap(title, 18))
        dot.node('A', wrapped_title, fontsize='16', fillcolor='#81C784', 
                penwidth='2', color='#2E7D32')
        
        for i, point in enumerate(points, start=1):
            node_id = f"N{i}"
            clean_point = re.sub(r'^[-•*]\s*', '', point).strip()
            label = "\n".join(textwrap.wrap(clean_point, 20))
            dot.node(node_id, label, fontsize='13', fillcolor='#F1F8E9')
            dot.edge('A', node_id, arrowsize='0.8', penwidth='1.2')
        
        return dot
    except Exception as e:
        st.error(f"Diagram creation error: {str(e)}")
        return None

# 🌿 Streamlit App
def main():
    st.set_page_config(page_title="AgriBot", page_icon="🌿", layout="centered")
    
    st.markdown("""
    <h1 style='text-align: center; color: green; font-size: 2.5rem;'>
        🌿 Beginner's Agriculture Guide
    </h1>
    <p style='text-align: center; font-size: 1.1rem;'>
        Simple answers with visual diagrams for new farmers
    </p>
    """, unsafe_allow_html=True)
    
    st.divider()

    # 💡 FAQ Section
    st.subheader("💬 Try These Common Questions")
    faqs = [
        "How to start a small vegetable garden?",
        "Natural ways to remove pests?",
        "Best crops for beginners?",
        "How often should I water plants?",
        "Easy composting methods?",
        "When to harvest vegetables?"
    ]
    
    cols = st.columns(2)
    for i, faq in enumerate(faqs):
        btn = cols[i % 2].button(
            faq, 
            use_container_width=True,
            help=f"Click to ask: {faq}"
        )
        if btn:
            st.session_state.question = faq

    # 📝 Question Input
    st.subheader("📝 Ask Your Farming Question")
    question = st.text_area(
        "Type your question here:",
        value=st.session_state.get("question", ""),
        height=120,
        placeholder="Example: How to grow tomatoes in pots?",
        label_visibility="visible"
    )

    if st.button("Generate Explanation 🌱", use_container_width=True, type="primary"):
        if not question.strip():
            st.warning("Please enter a question")
        else:
            with st.spinner("Creating explanation..."):
                try:
                    # Generate structured explanation first
                    desc_prompt = f"""Provide a beginner-friendly explanation for: '{question}'
                    Format with 4-5 subheadings (##) and 1-2 bullet points each.
                    Keep language simple (max 8 words per point).
                    Example format:
                    
                    ## Getting Started
                    - Choose sunny location
                    - Prepare soil properly
                    
                    ## Planting
                    - Space plants appropriately"""
                    
                    desc_response = model.generate_content(desc_prompt).text
                    
                    # Generate tree diagram points
                    tree_prompt = f"""Extract 5 key action steps for: '{question}'
                    - Each must start with '-'
                    - Max 8 words per point
                    - Simple verbs only"""
                    
                    tree_response = model.generate_content(tree_prompt).text
                    points = [line.strip() for line in tree_response.split('\n') 
                            if line.strip().startswith('-')][:5]
                    
                    # Display structured explanation first
                    st.subheader("📋 Step-by-Step Guide")
                    st.markdown(desc_response)
                    
                    # Then display visual diagram last
                    st.subheader("🌳 Quick Visual Summary")
                    if points:
                        tree = create_tree_diagram(question, points)
                        if tree:
                            st.graphviz_chart(tree, use_container_width=True)
                    
                except Exception as e:
                    st.error("Couldn't generate answer. Please try again.")
                    st.write("Tip: Keep questions simple for best results")

if __name__ == "__main__":
    main()