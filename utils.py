import streamlit as st
import peptacular as pt
import requests

# app_utils.py
from urllib.parse import quote_plus

def apply_centering_ccs(table_div_id: str) -> None:
    st.markdown(
    """
    <style>
    /* Target only the table inside the stMarkdownContainer within the specific div */
    .st-key-{table_div_id} [data-testid="stMarkdownContainer"] table {
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

def apply_expanded_sidebar():
    st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 600px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
    )



def display_header():
    st.markdown(f"""
        <div style='text-align: center; padding: 15px; top-margin: 0px'>
            <h3 style='margin: 0; font-size: 1.5em; color: #333;'>PepFrag 💣</h3>
            <p style='font-size: 1.1em; line-height: 1.6; color: #555;'>
                A Proforma2.0-Compliant Peptide Fragment Ion Calculator. 
            </p>
            <p style='font-size: 1.0em; line-height: 1.6; color: #555;'>
                See the 
                <a href="https://peptacular.readthedocs.io/en/latest/modules/getting_started.html#proforma-notation" 
                target="_blank" style='color: #007BFF; text-decoration: none;'>
                    Proforma Notation Docs
                </a> for supported peptide syntax. To report any issues or suggest improvements, please visit the 
                <a href="https://github.com/pgarrett-scripps/pep-frag" 
                target="_blank" style='color: #007BFF; text-decoration: none;'>
                    PepFrag Github Repo. 
                </a>
                Powered by 
                <a href="https://github.com/pgarrett-scripps/peptacular" target="_blank" style='color: #007BFF; text-decoration: none;'>
                    <strong>Peptacular</strong>
                </a>. 
            </p>
        </div>
    """, unsafe_allow_html=True)

def validate_peptide(peptide_sequence: str) -> None:
    """Parse and validate peptide sequence"""
    try:
        annotation = pt.parse(peptide_sequence)
    except pt.ProFormaFormatError as e:
        st.error(f'Error parsing peptide sequence: {e}')
        st.stop()

    # Validate peptide
    if annotation.has_charge():
        st.error('Peptide sequence cannot contain charge state!')
        st.stop()

    if len(annotation) > 1000:
        st.error(f'Peptide length cannot exceed 1000 amino acids')
        st.stop()

    if annotation.has_charge_adducts():
        st.error('Peptide sequence cannot contain adduct!')
        st.stop()


    if annotation.contains_sequence_ambiguity() or annotation.contains_residue_ambiguity() or annotation.contains_mass_ambiguity():
        st.error('Sequence cannot contain ambiguity!')
        st.stop()

    if len(annotation) == 0:
        st.error('Peptide sequence cannot be empty')
        st.stop()


def create_caption_vertical(params):

    # Calculate sequence mz with and without labile mods
    sequence_mz = pt.mz(params.peptide_sequence, monoisotopic=params.is_monoisotopic, ion_type='p', charge=params.charge)
    sequence_neutral_mass = pt.mass(params.peptide_sequence, monoisotopic=params.is_monoisotopic, ion_type='p', charge=0)  

    mz_min, mz_max = params.min_mz, params.max_mz
    
    use_mass_bounds = mz_min is not None and mz_max is not None

    mass_bounds_label, mass_bounds_value = "", ""
    if use_mass_bounds:
        mass_bounds_label = f"""
            <div style='font-weight: bold; color: #333;'>
                M/z Bounds
            </div>"""
        
        mass_bounds_value = f"""
            <div style='color: #333;'>
                {mz_min:.1f} - {mz_max:.1f}
            </div>"""

    caption = f"""
    <div style='text-align: center; padding: 20px; margin: 5px 0; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;'>
        <div style='font-size: 1.2em; font-weight: bold; margin-bottom: 5px; color: #333;'>
            {params.peptide_sequence}   
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 2px; margin-top: 5px; font-size: 0.95em;'>
            <div style='font-weight: bold; color: #333;'>
                Mass Type
            </div>
            <div style='color: #333;'>
                {"Monoisotopic" if params.is_monoisotopic else "Average"}
            </div>
            <div style='font-weight: bold; color: #333;'>
                Charge
            </div>
            <div style='color: #333;'>
                {params.charge}+
            </div>
            <div style='font-weight: bold; color: #333;'>
                M/z
            </div>
            <div style='color: #333;'>
                {sequence_mz:.{params.precision}f}
            </div>
            <div style='font-weight: bold; color: #333;'>
                Neutral Mass
            </div>
            <div style='color: #333;'>
                {sequence_neutral_mass:.{params.precision}f}
            </div>{mass_bounds_label}{mass_bounds_value}
        </div>
    </div>
    """

    return caption


def create_caption_horizontal(params):


    # Calculate sequence mz with and without labile mods
    sequence_mz = pt.mz(params.peptide_sequence, monoisotopic=params.is_monoisotopic, ion_type='p', charge=params.charge)
    sequence_neutral_mass = pt.mass(params.peptide_sequence, monoisotopic=params.is_monoisotopic, ion_type='p', charge=0)  

    mz_min, mz_max = params.min_mz, params.max_mz
    
    use_mass_bounds = mz_min is not None and mz_max is not None

    mass_bounds_label, mass_bounds_value = "", ""
    if use_mass_bounds:
        mass_bounds_label = f"""
            <div style='font-weight: bold; color: #333;'>
                M/z Bounds
            </div>"""
        
        mass_bounds_value = f"""
            <div style='color: #333;'>
                {mz_min:.1f} - {mz_max:.1f}
            </div>"""

    caption = f"""
    <div style='text-align: center; padding: 20px; margin: 5px 0; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;'>
        <div style='font-size: 1.2em; font-weight: bold; margin-bottom: 5px; color: #333;'>
            {params.peptide_sequence}   
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr 1fr{" 1fr" if use_mass_bounds else ""}; gap: 2px; margin-top: 5px; font-size: 0.95em;'>
            <div style='font-weight: bold; color: #333;'>
                Mass Type
            </div>
            <div style='font-weight: bold; color: #333;'>
                Charge
            </div>
            <div style='font-weight: bold; color: #333;'>
                M/z
            </div>
            <div style='font-weight: bold; color: #333;'>
                Neutral Mass
            </div>{mass_bounds_label}
            <div style='color: #333;'>
                {"Monoisotopic" if params.is_monoisotopic else "Average"}
            </div>
            <div style='color: #333;'>
                {params.charge}+
            </div>
            <div style='color: #333;'>
                {sequence_mz:.{params.precision}f}
            </div>
            <div style='color: #333;'>
                {sequence_neutral_mass:.{params.precision}f}
            </div>{mass_bounds_value}
        </div>
    </div>
    """

    return caption




def get_query_params_url(params_dict):
    """
    Create url params from alist of parameters and a dictionary with values.

    Args:
        params_list (str) :
            A list of parameters to get the value of from `params_dict`
        parmas_dict (dict) :
            A dict with values for the `parmas_list .
        **kwargs :
            Extra keyword args to add to the url
    """
    return "?" + "&".join(
        [
            f"{key}={quote_plus(str(value))}"
            for key, values in params_dict.items()
            for value in listify(values)
        ]
    )

def listify(o=None):
    if o is None:
        res = []
    elif isinstance(o, list):
        res = o
    elif isinstance(o, str):
        res = [o]
    else:
        res = [o]
    return res


def shorten_url(url: str) -> str:
    """Shorten a URL using TinyURL."""
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error: {e}"
    

def display_results(style_df, params):
    """Display the results of fragment calculation"""


    # Display the fragment table
    html = style_df.to_html()

    # Update the column headers to include the superscript charge state
    for col in ["A", "B", "C", "X", "Y", "Z"]:
        html = html.replace(f'{col}</th>', f'{col}<sup>{params.charge}+</sup></th>')

    st.markdown(html,
        unsafe_allow_html=True
    )