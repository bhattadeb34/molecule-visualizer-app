# app.py
import streamlit as st
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw
from io import StringIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Molecule Pair Visualizer",
    page_icon="🔬",
    layout="wide"
)

# --- App Title and Description ---
st.title("🔬 Neutral & Protonated Molecule Visualizer")
st.write(
    "This app visualizes neutral molecules and their corresponding protonated forms "
    "from a CSV file. Upload your `dft_input_pairs.csv` to begin."
)

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose your CSV file", type="csv")

# --- Main App Logic ---
if uploaded_file is not None:
    # Use StringIO to decode the file as a string, then read with pandas
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    df = pd.read_csv(stringio)

    # --- Data Validation ---
    if 'Neutral_smiles' not in df.columns or 'Protonated_smiles' not in df.columns:
        st.error("Error: The CSV file must contain 'Neutral_smiles' and 'Protonated_smiles' columns.")
    else:
        # --- Interactive Dropdown ---
        neutral_smiles_list = sorted(df['Neutral_smiles'].unique())
        selected_neutral = st.selectbox(
            'Select a Neutral Molecule to Visualize:',
            options=neutral_smiles_list
        )

        # --- Visualization Section ---
        if selected_neutral:
            col1, col2 = st.columns(2)

            # --- Column 1: Display the Neutral Molecule ---
            with col1:
                st.header("Neutral Molecule")
                st.code(selected_neutral, language='smiles')
                
                mol_neutral = Chem.MolFromSmiles(selected_neutral)
                if mol_neutral:
                    svg_neutral = Draw.MolToSVG(mol_neutral, size=(400, 400))
                    st.image(svg_neutral, use_column_width='always')
                else:
                    st.warning("Could not generate image for this neutral SMILES.")

            # --- Column 2: Display the Protonated Forms ---
            with col2:
                st.header("Corresponding Protonated Forms")
                
                protonated_smiles_list = df[df['Neutral_smiles'] == selected_neutral]['Protonated_smiles'].tolist()
                
                # Create an expander for each protonated form
                for i, prot_smiles in enumerate(protonated_smiles_list):
                    with st.expander(f"Protonated Form #{i+1}", expanded=(i==0)):
                        st.code(prot_smiles, language='smiles')
                        mol_prot = Chem.MolFromSmiles(prot_smiles)
                        
                        if mol_prot:
                            # Find the protonated atom (charge=+1) to highlight it
                            highlight_idx = next((atom.GetIdx() for atom in mol_prot.GetAtoms() if atom.GetFormalCharge() == 1), None)
                            
                            svg_prot = Draw.MolToSVG(
                                mol_prot, 
                                size=(400, 400), 
                                highlightAtoms=[highlight_idx] if highlight_idx is not None else []
                            )
                            st.image(svg_prot, use_column_width='always')
                        else:
                            st.warning("Could not generate image for this protonated SMILES.")
else:
    st.info("Awaiting your CSV file upload...")