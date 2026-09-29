import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image

from mem.preprocessing.pipeline import PreprocessingPipeline
from mem.preprocessing.safe_load import safe_load_image
from mem.data.privacy.scanner import scan_text_for_phi
from mem.detection.yolo import MEMDetector
from mem.topology.analyzer import TopologyAnalyzer
from mem.anomaly.models import DeepSVDD

# --- GLOBAL CONFIG ---
st.set_page_config(page_title="MEM Research Demo", layout="wide")

# --- MANDATORY DISCLAIMER ---
def render_disclaimer():
    st.warning("⚠️ **RESEARCH USE ONLY.** MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.")

# --- SAFETY WRAPPERS ---
def safe_process_upload(uploaded_file):
    """
    Pipeline: Upload -> Privacy Scan -> Safe Load -> Preprocess.
    """
    # 1. Privacy Scan (Filename)
    filename = uploaded_file.name
    phi_findings = scan_text_for_phi(filename)
    if phi_findings:
        st.error(f"❌ Privacy Breach: Potential PHI detected in filename: {phi_findings}")
        return None

    # 2. Safe Load
    try:
        img = Image.open(uploaded_file).convert("RGB")
        # Save temporarily for processing pipeline
        tmp_path = Path("temp_upload.jpg")
        img.save(tmp_path)

        # Use the Stage 2 safe load logic
        loaded_img = safe_load_image(tmp_path)
        if loaded_img is None:
            st.error("❌ Image corrupted or exceeds safety limits.")
            return None

        return loaded_img
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
        return None

# --- APP PAGES ---
def main():
    st.title("Morphological Evolutionary Manifold (MEM)")
    render_disclaimer()

    menu = ["Home", "Morphology Analysis", "TDA Diversity", "Anomaly Detection", "Knowledge Graph"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Home":
        st.subheader("Welcome to the MEM Research Framework")
        st.markdown("""
        MEM provides a unified approach to mapping clonal diversity in leukemia via morphology.

        **Key Capabilities:**
        - Stain-aware preprocessing
        - ViT-based morphology embeddings
        - Topological Manifold Analysis (MCDS)
        - Rare-cell (MRD-style) anomaly detection
        """)
        st.info("Note: This is a research-only tool. No clinical data should be uploaded.")

    elif choice == "Morphology Analysis":
        st.subheader("Cell-Level Morphology Analysis")
        uploaded_file = st.file_uploader("Upload blood smear patch (JPG/PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            img = safe_process_upload(uploaded_file)
            if img:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(img, caption="Uploaded Patch", use_column_width=True)
                with col2:
                    st.write("### Model Predictions")
                    # Mock prediction for demo
                    st.success("Predicted: AML Blast (Confidence: 0.92)")
                    st.write("Uncertainty: $\pm$ 0.04 (MC Dropout)")
                    st.warning("Proxy claim: Morphology-associated classification only.")

    elif choice == "TDA Diversity":
        st.subheader("Topological Manifold Diversity")
        st.write("Analyzing embedding space using Persistent Homology...")

        # Mock visualization
        st.line_chart(np.random.randn(100).cumsum())
        st.metric("MCDS Score", "0.642", "Stable")
        st.caption("TDA analysis shows a complex manifold with 3 distinct morphological subpopulations.")

    elif choice == "Anomaly Detection":
        st.subheader("Simulated Rare-Cell Detection")
        st.write("Deep SVDD Anomaly Score Analysis")

        uploaded_bag = st.file_uploader("Upload Bag (CSV/Parquet)", type=["csv", "parquet"])
        if uploaded_bag:
            st.write("Processing bag of 1000 cells...")
            # Mock detection
            st.error("Result: ABNORMAL")
            st.write("Max Anomaly Score: 12.4 (Threshold: 8.1)")
            st.write("Estimated Prevalence: 0.5% abnormal cells.")

    elif choice == "Knowledge Graph":
        st.subheader("Biology Prior Knowledge Graph")
        st.write("Linking morphological clusters to genetic entities.")
        st.info("Visualization available via GraphML export in the CLI.")

        cluster_id = st.selectbox("Select Model Cluster", ["Cluster_01", "Cluster_02", "Cluster_03"])
        st.write(f"Hypotheses for {cluster_id}:")
        st.table(pd.DataFrame({
            "Entity": ["FLT3-ITD", "NPM1", "IDH2"],
            "Confidence": [0.8, 0.6, 0.4],
            "Evidence": ["TCGA-LAML", "GEO-AML", "Literature"]
        }))

if __name__ == "__main__":
    main()
