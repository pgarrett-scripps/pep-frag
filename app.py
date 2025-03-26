import pandas as pd
import streamlit as st
import peptacular as pt
from streamlit_js_eval import get_page_location

from app_input import get_params

from fragment_utils import style_fragment_table
from utils import (apply_centering_ccs, 
                   create_caption_vertical, 
                   create_caption_horizontal, 
                   get_query_params_url, 
                   shorten_url, 
                   validate_peptide, 
                   display_results)

TABLE_DIV_ID = 'custom-table-id'

st.set_page_config(page_title="PepFrag", page_icon=":bomb:", layout="centered", initial_sidebar_state="expanded")

with st.sidebar:

    st.markdown(f"""
        <div style='text-align: center; padding: 15px; top-margin: 0px'>
            <h3 style='margin: 0; font-size: 1.5em; color: #333;'>PepFrag: Proforma2.0-Compliant Peptide Fragment Ion Calculator</h3>
            <p style='font-size: 1.1em; line-height: 1.6; color: #555;'>
                Powered by 
                <a href="https://github.com/pgarrett-scripps/peptacular" target="_blank" style='color: #007BFF; text-decoration: none;'>
                    <strong>Peptacular</strong>
                </a>. 
                See the 
                <a href="https://peptacular.readthedocs.io/en/latest/modules/getting_started.html#proforma-notation" 
                target="_blank" style='color: #007BFF; text-decoration: none;'>
                    Proforma Notation Docs
                </a> for supported peptide syntax. To report any issues or suggest improvements, please visit the 
                <a href="https://github.com/pgarrett-scripps/pep-frag" 
                target="_blank" style='color: #007BFF; text-decoration: none;'>
                    PepFrag Github Repo.
                </a>
            </p>
        </div>
    """, unsafe_allow_html=True)

    peptide_help_msg = """
    **Peptide Sequence**: Enter the peptide sequence to fragment. Include modifications in square brackets.
    """

    params = get_params()

top_window, bottom_window = st.container(), st.container()

with bottom_window:
    page_loc = get_page_location()
    apply_centering_ccs(TABLE_DIV_ID)

with top_window:

    title_c, _, button_c = st.columns([2, 1, 1])
    title_c.header("PepFrag Results")
    st.caption(f'''**This pages URL automatically updates with your input, and can be shared with others. 
               You can optionally use the Generate TinyURL button to create a shortened URL.**''', unsafe_allow_html=True)

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
        caption=create_caption_horizontal(params) if params.is_horizontal_caption else create_caption_vertical(params),
        )
    
    frag_df = pd.DataFrame([fragment.to_dict() for fragment in fragments])
    
    frag_tab, data_tab = st.tabs(['Table', 'Data'])

    with frag_tab:

        # within container to allow for custom table id
        with st.container(key=TABLE_DIV_ID):
            display_results(style_df, params)

        if page_loc and 'origin' in page_loc:
            url_origin = page_loc['origin']
            if button_c.button("Generate TinyURL", key="generate_tinyurl", type="primary"):
                url_params = {k: st.query_params.get_all(k) for k in st.query_params.keys()}
                page_url = f"{url_origin}{get_query_params_url(url_params)}"
                short_url = shorten_url(page_url)


                @st.dialog(title="Share your results")
                def url_dialog(url):
                    st.write(f"Shortened URL: {url}")

                url_dialog(short_url)

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

