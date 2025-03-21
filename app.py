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

    st.title('PepFrag :bomb:')
    # ([ProForma 2.0 compliant](https://github.com/HUPO-PSI/ProForma/blob/master/SpecDocument/ProForma_v2_draft15_February2022.pdf)).
    st.caption(f"""
    A peptide fragment ion calculator. Made with [peptacular {pt.__version__}](https://github.com/pgarrett-scripps/peptacular): [![DOI](https://zenodo.org/badge/591504879.svg)](https://doi.org/10.5281/zenodo.15054278)""")

    st.caption('''If you use this in a publication, 
               please cite: [![DOI](https://zenodo.org/badge/591504879.svg)](https://doi.org/10.5281/zenodo.15054278)''')
    

    peptide_help_msg = """
    **Peptide Sequence**: Enter the peptide sequence to fragment. Include modifications in square brackets.
    """

    params = get_params()

top_window, bottom_window = st.container(), st.container()

with bottom_window:
    page_loc = get_page_location()
    apply_centering_ccs(TABLE_DIV_ID)

    st.markdown(
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 25px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

with top_window:

    title_c, _, button_c = st.columns([2, 1, 1])
    title_c.header("PepFrag Results")
    st.caption(f'''**This pages URL automatically updates with your input, and can be shared with others. 
               You can optionally use the Generate TinyURL button to create a shortened URL.**''', unsafe_allow_html=True)

    validate_peptide(params.peptide_sequence)
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
            # Show mass bounds if enabled
            if params.use_mass_bounds:
                st.markdown(f'**M/z Bounds:** {params.min_mz} - {params.max_mz} *m/z*')


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
