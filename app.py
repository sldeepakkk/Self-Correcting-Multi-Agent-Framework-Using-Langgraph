import streamlit as st
import sys
import os

# Page config
st.set_page_config(
    page_title="NSE Research Agent",
    page_icon="📈",
    layout="wide"
)

st.title("📈 NSE Research Agent")
st.caption("Self-correcting multi-agent research pipeline · LangGraph · CRAG · Episodic Memory")

# Sidebar — system info
with st.sidebar:
    st.header("System Status")
    
    try:
        from retrieval.vector_store import VectorStore
        vs = VectorStore()
        st.success(f"✅ Vector store: {vs.size} documents")
    except Exception as e:
        st.error(f"❌ Vector store: {e}")

    try:
        from cache.semantic_cache import SemanticCache
        cache = SemanticCache()
        st.info(f"🗄️ Cache: {cache.size} entries")
    except Exception as e:
        st.warning(f"⚠️ Cache: {e}")

    try:
        from memory.episodic import get_lesson_count
        counts = get_lesson_count()
        st.info(f"🧠 Episodic memory: {counts['active']} active lessons")
    except Exception as e:
        st.warning(f"⚠️ Memory: {e}")

    st.divider()
    st.header("Example Queries")
    examples = [
        "What are the fundamentals and analyst view for Infosys?",
        "Compare TCS and Wipro on profit margins and analyst consensus",
        "Given RBI rate decisions, which banking stocks have strongest CASA ratios?",
        "Analyze BEL and Zen Technologies on defence sector tailwinds",
        "What is the 52-week range and PE ratio for Reliance Industries?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["query_input"] = example

# Main area
query = st.text_area(
    "Enter your NSE research query:",
    value=st.session_state.get("query_input", ""),
    height=80,
    placeholder="e.g. Compare HDFC Bank and ICICI Bank on analyst targets and NIM outlook..."
)

col1, col2 = st.columns([1, 5])
with col1:
    run_button = st.button("🔍 Research", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("Clear", use_container_width=True)

if clear_button:
    st.session_state["query_input"] = ""
    st.rerun()

if run_button and query.strip():
    with st.spinner("Running research pipeline..."):
        try:
            from main import run_query
            result = run_query(query.strip(), verbose=False)
            
            # Path badge
            path_colors = {
                "fast": "🟢",
                "medium": "🔵", 
                "slow": "🟡",
                "slow_failed": "🔴"
            }
            path = result.get("path_taken", "unknown")
            emoji = path_colors.get(path, "⚪")
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Path", f"{emoji} {path}")
            with col2:
                st.metric("Latency", f"{result.get('latency_ms', 0)}ms")
            with col3:
                st.metric("Cache Hit", "Yes" if result.get("cache_hit") else "No")
            with col4:
                st.metric("CRAG", "Triggered" if result.get("crag_triggered") else "Not needed")
            
            st.divider()
            
            # Response
            st.markdown(result.get("response", "No response generated."))
            
            st.divider()
            
            # Trace expander
            with st.expander("🔍 Execution Trace", expanded=False):
                trace_nodes = result.get("trace", [])
                if trace_nodes:
                    for i, entry in enumerate(trace_nodes):
                        if not isinstance(entry, dict):
                            continue
                        node = entry.get("node", "unknown")
                        # Build display lines excluding node key
                        details = {k: v for k, v in entry.items() if k != "node"}
                        with st.container():
                            st.markdown(f"**`{i+1}. {node.upper()}`**")
                            if details:
                                st.json(details, expanded=False)
                else:
                    st.info("Fast path — served from cache, no graph execution.")

            # Run ID
            st.caption(f"Run ID: {result.get('run_id', 'unknown')} · "
                      f"Lessons applied: {result.get('lessons_applied', 0)}")

        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.exception(e)

elif run_button and not query.strip():
    st.warning("Please enter a query.")