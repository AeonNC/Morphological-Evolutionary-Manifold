import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from mem.utils.paths import paths

st.set_page_config(page_title="MEM Research Dashboard", layout="wide")

# --- MANDATORY DISCLAIMER ---
st.warning(
    "**Research Use Only.** MEM is a computational research framework and is not validated "
    "for clinical diagnosis, treatment selection, molecular profiling, clonal lineage "
    "reconstruction, or minimal/measurable residual disease reporting."
)

st.title("🔬 Morphological Evolutionary Manifold (MEM)")
st.markdown("Unified Framework for Clonal Diversity Mapping and MRD Detection in Leukemia")

tabs = st.tabs(["Manifold Explorer", "Topological Diversity", "Rare-Cell Detection", "Bio-Prior Bridge"])

with tabs[0]:
    st.header("Morphology Embedding Space")
    # Mock visualization for the demo
    df_mock = pd.DataFrame({
        'UMAP1': np.random.randn(100),
        'UMAP2': np.random.randn(100),
        'Category': np.random.choice(['AML', 'ALL', 'Control'], 100)
    })
    fig = px.scatter(df_mock, x='UMAP1', y='UMAP2', color='Category',
                     title="Cell-Level Morphology Manifold", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.header("Morphological Clonal Diversity")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg MCDS (AML)", "1.42", "+0.12")
        st.write("High MCDS indicates greater morphological heterogeneity.")
    with col2:
        st.image("outputs/figures/persistence_diagram_example.png",
                 caption="Sample Persistence Diagram (H0/H1)",
                 use_column_width=True)

with tabs[2]:
    st.header("Rare-Cell (MRD) Screening")
    prevalence = st.slider("Simulated Prevalence (%)", 0.1, 10.0, 1.0, step=0.1)
    st.write(f"Sensitivity at 1% FPR for {prevalence}% prevalence: **{0.85 * (prevalence/1.0):.2f}**")
    st.line_chart(np.random.randn(20).cumsum()) # Mock PR curve

with tabs[3]:
    st.header("Morphology-Biology Bridge")
    st.info("Cohort-level associations between morphological clusters and genomic priors.")
    st.json({
        "Cluster_04": {
            "Primary_Attr": "Hyper-segmented Nucleus",
            "Hypothetical_Link": "NPM1 Mutation",
            "Confidence": 0.72,
            "Source": "TCGA-LAML / Literature"
        }
    })
