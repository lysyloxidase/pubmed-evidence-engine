import streamlit as st
import httpx
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="PubMed Evidence Engine", layout="wide")

API_URL = "http://localhost:8000/api/query"

st.title("🧬 PubMed Evidence Engine")
st.markdown("Search biomedical literature, extract entities with Europe PMC, rerank, and generate answers with a local LLM.")

with st.sidebar:
    st.header("Settings")
    llm_model = st.text_input("LLM Model Name (Ollama)", value="llama3")
    fetch_limit = st.slider("Documents to fetch from APIs", min_value=10, max_value=100, value=20)
    top_k = st.slider("Top K to Rerank & Use in Context", min_value=1, max_value=20, value=5)

query = st.text_input("Enter your clinical/biological question:")

if st.button("Search & Generate"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Pipeline running (Fetch -> Rerank -> Extract -> Generate)..."):
            payload = {
                "query": query,
                "limit": fetch_limit,
                "top_k": top_k,
                "llm_model": llm_model
            }
            try:
                response = httpx.post(API_URL, json=payload, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                
                st.subheader("💡 Generated Report")
                st.write(data["report"])
                
                st.divider()
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📚 Top Retrieved Sources")
                    for i, doc in enumerate(data["documents"]):
                        source = doc.get("source", "MED")
                        pmid = doc.get("pmid", doc.get("id"))
                        link = f"https://europepmc.org/article/{source}/{pmid}"
                        
                        st.markdown(f"**[{i+1}] {doc.get('title')}**")
                        with st.expander(f"Abstract & Annotations ({source}:{pmid})"):
                            st.write(doc.get("abstractText"))
                            anns = doc.get("annotations", [])
                            if anns:
                                st.markdown("**Found Entities:**")
                                for a in anns[:5]:
                                    st.caption(f"- {a.get('exact')} ({a.get('type')})")
                            st.markdown(f"[View on Europe PMC]({link})")
                            
                with col2:
                    st.subheader("🕸️ Knowledge Graph")
                    graph_data = data.get("graph_data", {"nodes": [], "edges": []})
                    
                    nodes = []
                    edges = []
                    
                    for n in graph_data["nodes"]:
                        color = "#97c2fc"
                        if n["group"] == "Gene_Proteins": color = "#ff9999"
                        elif n["group"] == "Diseases": color = "#ffcc99"
                        elif n["group"] == "Chemicals": color = "#99ccff"
                        elif n["group"] == "Document": color = "#e2e2e2"
                        
                        nodes.append(Node(id=n["id"], label=n["label"], color=color, size=20))
                        
                    for e in graph_data["edges"]:
                        edges.append(Edge(source=e["source"], target=e["target"]))
                        
                    config = Config(
                        width=500,
                        height=500,
                        directed=True, 
                        physics=True, 
                        hierarchical=False,
                    )
                    
                    if nodes:
                        agraph(nodes=nodes, edges=edges, config=config)
                    else:
                        st.info("No connections found to build a graph.")
                    
            except httpx.ReadTimeout:
                st.error("Request timed out. The local LLM might be taking too long to generate (or backend is cold).")
            except Exception as e:
                st.error(f"Error communicating with API: {e}")
