import streamlit as st
import peptacular as pt

from constants import (
    DEFAULT_PEPTIDE, DEFAULT_CHARGE, DEFAULT_MASS_TYPE, DEFAULT_FRAGMENT_TYPES,
    DEFAULT_USE_MASS_BOUNDS, DEFAULT_MIN_MZ, DEFAULT_MAX_MZ, DEFAULT_PRECISION,
    DEFAULT_ROW_PADDING, DEFAULT_COLUMN_PADDING, DEFAULT_SHOW_BORDERS,
    DEFAULT_A_COLOR, DEFAULT_B_COLOR, DEFAULT_C_COLOR,
    DEFAULT_X_COLOR, DEFAULT_Y_COLOR, DEFAULT_Z_COLOR
)
from ui_components import setup_sidebar, display_results
from fragment_utils import style_fragment_table

def validate_peptide(peptide_sequence):
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

        # if contains labile mods, give warning that they will be removed
    if annotation.has_labile_mods():
        st.warning('Labile mods will be removed from fragment table')

    # pop labile mods from peptide sequence
    labile_mods = annotation.pop_labile_mods()

    if annotation.contains_sequence_ambiguity() or annotation.contains_residue_ambiguity() or annotation.contains_mass_ambiguity():
        st.error('Sequence cannot contain ambiguity!')
        st.stop()

    if len(annotation) == 0:
        st.error('Peptide sequence cannot be empty')
        st.stop()

    # Calculate and validate mass
    try:
        _ = pt.mass(annotation, monoisotopic=True, ion_type='p', charge=0)
    except Exception as err:
        st.error(f'Error calculating peptide mass: {err}')
        st.stop()

    return annotation, labile_mods

def main():
    st.set_page_config(page_title="PepFrag", page_icon=":bomb:", layout="wide", initial_sidebar_state="expanded")

    # Initialize query parameters if they don't exist
    #initialize_query_params()

    previous_params = st.session_state.get('previous_params', None)
    
    # Setup sidebar and get current params
    params = setup_sidebar()
    # Parse and validate peptide sequence
    
    annotation, labile_mods = validate_peptide(params['peptide_sequence'])
    annot_with_labile_mods = annotation.copy()
    annot_with_labile_mods.add_labile_mods(labile_mods)

    # Calculate sequence mz with and without labile mods
    sequence_mz = pt.mz(annot_with_labile_mods, monoisotopic=params['is_monoisotopic'], ion_type='p', charge=params['charge'])
    sequence_neutral_mass = pt.mass(annot_with_labile_mods, monoisotopic=params['is_monoisotopic'], ion_type='p', charge=0)

    #st.caption(annot_with_labile_mods.serialize(include_plus=True))

    precision = params['precision']
    caption = f"""
    <div style='text-align: center; padding: 10px; margin: 10px 0;'>
        <div style='font-size: 1.0em; font-weight: bold; margin-bottom: 8px;'>
            {annot_with_labile_mods.serialize(include_plus=True)}
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 8px;'>
            <div>
                <span style='font-weight: bold;'>Mass Type:</span> 
                {"Monoisotopic" if params["is_monoisotopic"] else "Average"}
            </div>
            <div>
                <span style='font-weight: bold;'>Charge:</span> 
                {params["charge"]}+
            </div>
            <div>
                <span style='font-weight: bold;'>M/z:</span> 
                {sequence_mz:.{precision}f}
            </div>
            <div>
                <span style='font-weight: bold;'>Neutral Mass:</span> 
                {sequence_neutral_mass:.{precision}f}
            </div>
        </div>
    </div>
    """

    # Calculate fragment table based on inputs
    try:
        style_df = style_fragment_table(
            sequence=annotation.serialize(include_plus=True),
            fragment_types=params['fragment_types'],
            charge=params['charge'],
            is_monoisotopic=params['is_monoisotopic'],
            mz=sequence_mz,
            show_borders=params['show_borders'],
            decimal_places=params['precision'],
            row_padding=params['row_padding'],
            column_padding=params['column_padding'],
            min_mass=params['min_mz'] if params['use_mass_bounds'] else None,
            max_mass=params['max_mz'] if params['use_mass_bounds'] else None,
            color_map=params['frag_colors'],
            caption=caption,
            )

        # Display results
        display_results(style_df, params)

    except Exception as e:
        st.error(f"Error generating fragment table: {e}")


def initialize_query_params():
    """Initialize default query parameters if they don't exist"""
    if not st.query_params:
        st.query_params.clear()
        st.query_params['peptide'] = DEFAULT_PEPTIDE
        st.query_params['charge'] = DEFAULT_CHARGE
        st.query_params['mass_type'] = DEFAULT_MASS_TYPE
        for ft in DEFAULT_FRAGMENT_TYPES:
            st.query_params[ft] = True
        st.query_params['mass_bounds'] = DEFAULT_USE_MASS_BOUNDS
        st.query_params['min_mass'] = DEFAULT_MIN_MZ
        st.query_params['max_mass'] = DEFAULT_MAX_MZ
        st.query_params['decimal_places'] = DEFAULT_PRECISION
        st.query_params['row_padding'] = DEFAULT_ROW_PADDING
        st.query_params['column_padding'] = DEFAULT_COLUMN_PADDING
        st.query_params['show_borders'] = DEFAULT_SHOW_BORDERS
        st.query_params['a_color'] = DEFAULT_A_COLOR
        st.query_params['b_color'] = DEFAULT_B_COLOR
        st.query_params['c_color'] = DEFAULT_C_COLOR
        st.query_params['x_color'] = DEFAULT_X_COLOR
        st.query_params['y_color'] = DEFAULT_Y_COLOR
        st.query_params['z_color'] = DEFAULT_Z_COLOR
        st.rerun()


if __name__ == "__main__":
    main()