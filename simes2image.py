# ==============================================================================
#  SMILES to Image Converter for Google Colab
# ==============================================================================
# This script performs the following actions:
# 1. Installs the RDKit library.
# 2. Takes a multiline string input of chemical data.
# 3. Processes each line, generating a 2D image from the SMILES string.
# 4. Displays the generated images directly in the notebook output.
# 5. Creates a single ZIP file containing all the images for easy download.
# ==============================================================================

# Step 1: Install RDKit
# The '-q' flag suppresses verbose installation output.
!pip install -q rdkit-pypi

# Step 2: Import necessary libraries
import io
import zipfile
import re
import base64
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Draw
from google.colab import files
from IPython.display import display, HTML

# Step 3: Input Data
# --- EDIT THIS VARIABLE WITH YOUR DATA ---
# Enter your chemical data below, one per line.
# Format: Chemical Name,SMILES_String

# test data set
# chemical_data_input = """
# Aspirin,CC(=O)OC1=CC=CC=C1C(=O)O
# Caffeine,CN1C=NC2=C1C(=O)N(C(=O)N2C)C
# Ethanol,CCO
# Vanillin,COC1=C(C=C(C=C1)C=O)O
# 3-Amino-1,2,4-triazole,NC1=NC=NN1
# Invalid Molecule,this-is-not-a-valid-smiles
# 4-Amino-1,2,4-triazole,N1=CN=CN1N
# """

chemical_data_input ="""
3-Amino-1,2,4-triazole, NC1=NC=NN1
4-Amino-1,2,4-triazole, N1=CN=CN1N
2-Aminothiazole, NC1=NC=CS1
3-Aminopyrazole, NC1=CC=NN1
5-Amino-1H-tetrazole, NC1=NNN=N1
"""

# Step 4: Define Helper and Core Functions

def sanitize_filename(name):
    """Replaces spaces with underscores and removes invalid filename characters."""
    name = name.strip().replace(' ', '_')
    return re.sub(r'[\\/*?:"<>|]', '', name)

def process_chemicals(data):
    """
    Parses the input string, generates images, and returns a list of results.
    """
    print("Processing chemical data...")
    lines = data.strip().split('\n')
    generated_images = []
    
    for line in lines:
        if not line.strip():
            continue

        # Use rsplit to correctly handle names that might contain commas
        parts = line.strip().rsplit(',', 1)
        if len(parts) != 2:
            print(f"--> Skipping malformed line: {line}")
            continue
            
        name, smiles = parts[0].strip(), parts[1].strip()
        filename = f"{sanitize_filename(name)}.png"
        mol = None
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError("Invalid SMILES string resulted in null molecule.")
                
            img = Draw.MolToImage(mol, size=(300, 300))
            
            # Save image to an in-memory bytes buffer
            bio = io.BytesIO()
            img.save(bio, format='PNG')
            
            generated_images.append({
                'name': name,
                'filename': filename,
                'image_bytes': bio.getvalue(),
                'error': None
            })
            
        except Exception as e:
            print(f"--> Failed to process '{name}': Invalid SMILES string '{smiles}'")
            generated_images.append({
                'name': name,
                'filename': filename,
                'image_bytes': None,
                'error': f"Invalid SMILES: {smiles}"
            })
        
    print(f"Processing complete. {len(generated_images)} entries handled.\n")
    return generated_images

def display_results(results):
    """
    Displays the generated images (or error messages) in a grid.
    """
    print("Displaying Results:")
    html_content = "<div style='display: flex; flex-wrap: wrap; gap: 20px;'>"
    
    for result in results:
        card = "<div style='width: 200px; text-align: center; border: 1px solid #ddd; padding: 10px; border-radius: 8px;'>"
        card += f"<h4 style='font-family: sans-serif; margin: 0 0 10px 0;'>{result['name']}</h4>"
        
        if result['image_bytes']:
            # FIX: Use the standard base64 library for cleaner encoding
            b64_string = base64.b64encode(result['image_bytes']).decode('utf-8')
            card += f"<img src='data:image/png;base64,{b64_string}' style='width: 100%; height: auto;'/>"
        else:
            card += f"<div style='height: 200px; display: flex; align-items: center; justify-content: center; background: #fee; color: #a00; border-radius: 4px;'>{result['error']}</div>"
        
        card += "</div>"
        html_content += card
        
    html_content += "</div>"
    display(HTML(html_content))

def create_and_download_zip(results):
    """
    Creates a ZIP file, saves it to the Colab filesystem, and triggers a download.
    """
    valid_images = [r for r in results if r['image_bytes']]
    if not valid_images:
        print("\nNo valid images were generated to download.")
        return
        
    zip_filename = "chemical_structures.zip"
    print(f"\nPreparing '{zip_filename}' for download...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for result in valid_images:
            zf.writestr(result['filename'], result['image_bytes'])
            
    # FIX: Trigger the download by providing the filename of the file
    # that now exists in the Colab environment.
    files.download(zip_filename)
    print(f"Download of '{zip_filename}' should start automatically.")

# --- Main Execution ---
if __name__ == "__main__":
    results = process_chemicals(chemical_data_input)
    if results:
        display_results(results)
        create_and_download_zip(results)
