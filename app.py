import pandas as pd
import streamlit as st
import streamlit_permalink as stp
import peptacular as pt
from app_input import get_params

from fragment_utils import style_fragment_table
from utils import (apply_centering_ccs, apply_expanded_sidebar,
                   create_caption_vertical,
                   create_caption_horizontal, display_header,
                   validate_peptide,
                   display_results)

TABLE_DIV_ID = 'custom-table-id'

st.set_page_config(page_title="PepFrag", page_icon=":bomb:",
                   layout="centered", initial_sidebar_state="expanded")


apply_expanded_sidebar()

with st.sidebar:

    display_header()
    params = get_params()

top_window, bottom_window = st.container(), st.container()

with bottom_window:
    apply_centering_ccs(TABLE_DIV_ID)

with top_window:

    @st.fragment
    def url_fragment():

        st.header("PepFrag Results")

        st.caption(
            '''**This pages URL automatically updates with your input, and can be shared with others.**''',
            unsafe_allow_html=True,
        )


    url_fragment()

    validate_peptide(params.peptide_sequence)

    if params.use_carbamidomethyl:
        params.peptide_sequence = pt.condense_static_mods(
            pt.add_mods(params.peptide_sequence, {'static': '[Carbamidomethyl]@C'}), include_plus=True)

    if params.condense_to_mass_notation:
        params.peptide_sequence = pt.condense_to_mass_mods(params.peptide_sequence, include_plus=True,
                                                           precision=params.precision)

    annotation = pt.parse(params.peptide_sequence)

    # ensure that mass can be calculated
    try:
        _ = pt.mass(annotation, monoisotopic=True, ion_type='p', charge=0)
    except Exception as err:
        st.error(f'Error calculating peptide mass: {err}')
        st.stop()

    annot_without_labile_mods = annotation.copy()
    annot_without_labile_mods.pop_labile_mods()

    # Calculate fragment table based on inputs
    style_df, fragments = style_fragment_table(
        sequence=annotation.serialize(include_plus=True),
        fragment_types=params.fragment_types,
        charge=params.charge,
        is_monoisotopic=params.is_monoisotopic,
        show_borders=params.show_borders,
        decimal_places=params.precision,
        row_padding=params.row_padding,
        column_padding=params.column_padding,
        min_mass=params.min_mz if params.use_mass_bounds else None,
        max_mass=params.max_mz if params.use_mass_bounds else None,
        color_map=params.frag_colors,
        caption=create_caption_horizontal(
            params) if params.is_horizontal_caption else create_caption_vertical(params),
    )

    frag_df = pd.DataFrame([fragment.to_dict() for fragment in fragments])

    frag_tab, data_tab, copy_tab = st.tabs(['Table', 'Data', 'Copy'])

    with frag_tab:

        # within container to allow for custom table id
        with st.container(key=TABLE_DIV_ID):
            display_results(style_df, params)

    with data_tab:

        st.caption('Fragment Data')
        frag_df['in_bounds'] = True

        if params.use_mass_bounds:
            frag_df.loc[frag_df['mz'] < params.min_mz, 'in_bounds'] = False
            frag_df.loc[frag_df['mz'] > params.max_mz, 'in_bounds'] = False

        st.dataframe(frag_df, hide_index=True)

        st.download_button(label='Download Data',
                           data=frag_df.to_csv(index=False),
                           file_name=f'{annotation._sequence}_fragment_data.csv',
                           use_container_width=True,
                           type='primary',
                           on_click='ignore',
                           key='download_data')

    with copy_tab:
        st.caption('Copy Data')
        st.data_editor(style_df, hide_index=True)

    st.divider()

    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-top: 0px solid #ddd;'>
            <div style='text-align: left; font-size: 1.1em; color: #555;'>
                <a href="https://github.com/pgarrett-scripps/pep-frag" target="_blank" 
                   style='text-decoration: none; color: #007BFF; font-weight: bold;'>
                    PepFrag
                </a>
                <a href="https://doi.org/10.5281/zenodo.15061824" target="_blank" style="margin-left: 12px;">
                    <img src="https://zenodo.org/badge/948720227.svg" alt="DOI" 
                         style="vertical-align: middle; height: 20px;">
                </a>
            </div>
            <div style='text-align: right; font-size: 1.1em; color: #555;'>
                <a href="https://github.com/pgarrett-scripps/peptacular" target="_blank" 
                   style='text-decoration: none; color: #007BFF; font-weight: bold;'>
                    Peptacular
                </a>
                <a href="https://doi.org/10.5281/zenodo.15054278" target="_blank" style="margin-left: 12px;">
                    <img src="https://zenodo.org/badge/591504879.svg" alt="DOI" 
                         style="vertical-align: middle; height: 20px;">
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
