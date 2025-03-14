import streamlit_permalink as st
import peptacular as pt
from typing import Dict, Any

from constants import (
    DEFAULT_PEPTIDE, DEFAULT_CHARGE, DEFAULT_MASS_TYPE, DEFAULT_FRAGMENT_TYPES,
    DEFAULT_USE_MASS_BOUNDS, DEFAULT_MIN_MZ, DEFAULT_MAX_MZ, DEFAULT_PRECISION,
    DEFAULT_ROW_PADDING, DEFAULT_COLUMN_PADDING, DEFAULT_SHOW_BORDERS,
    DEFAULT_A_COLOR, DEFAULT_B_COLOR, DEFAULT_C_COLOR,
    DEFAULT_X_COLOR, DEFAULT_Y_COLOR, DEFAULT_Z_COLOR
)


def setup_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        st.image('images/yateslogo.png', width=200, use_container_width=True)

        st.title('PepFrag :bomb:')
        st.caption("""
        A peptide fragment ion calculator ([ProForma 2.0 compliant](https://github.com/HUPO-PSI/ProForma/blob/master/SpecDocument/ProForma_v2_draft15_February2022.pdf)).""")

        st.caption('''**This pages URL automatically updates with your input, and can be shared with others.**''')

        peptide_help_msg = """
        **Peptide Sequence**: Enter the peptide sequence to fragment. Include modifications in square brackets.
        """

        st.subheader('Options', divider='grey')
  
        peptide_sequence = st.text_input('Peptide',
                                          value=DEFAULT_PEPTIDE,
                                          max_chars=2000,
                                          help=peptide_help_msg,
                                          key='peptide')
        original_peptide_sequence = peptide_sequence

        # Charge and adduct inputs

        charge = st.number_input('Charge',
                                    min_value=0,
                                    value=DEFAULT_CHARGE,
                                    help='Charge state of the peptide',
                                    key='charge')
        # charge_adduct = st.text_input('Adduct',
                                        # value='+H',
                                        # help='Adduct to use for charge state calculation',
                                        # key='adduct', disabled=True)
        fragment_types = setup_fragment_pills()


        mass_type = st.radio(label='Mass Type',
                            options=['monoisotopic', 'average'],
                            help='Mass type to use for fragment calculation',
                            index=['monoisotopic', 'average'].index(DEFAULT_MASS_TYPE),
                            horizontal=True,
                            key='mass_type')

        is_monoisotopic = mass_type == 'monoisotopic'

        # Additional options
        st.subheader('Additional Options', divider='grey')
        
        use_carbamidomethyl = st.checkbox('Use carbamidomethyl C', value=False, key='use_carbamidomethyl')
        condense_to_mass_notation = st.checkbox('Condense to mass notation', value=False, key='condense_to_mass_notation')
        
        if use_carbamidomethyl:
            peptide_sequence = pt.condense_static_mods(pt.add_mods(peptide_sequence, {'static': '[Carbamidomethyl]@C'}))
            
        if condense_to_mass_notation:
            peptide_sequence = pt.condense_to_mass_mods(peptide_sequence, include_plus=True, precision=4)


        use_mass_bounds = st.checkbox('Use Mass Bounds', value=DEFAULT_USE_MASS_BOUNDS, key='mass_bounds')

        min_mz, max_mz = None, None
        if use_mass_bounds:
            c1, c2 = st.columns(2)
            with c1:
                min_mz = st.number_input('Min m/z', value=DEFAULT_MIN_MZ, key='min_mz', step=100.0)
            with c2:
                max_mz = st.number_input('Max m/z', value=DEFAULT_MAX_MZ, key='max_mz', step=100.0)

        # Format options
        precision, row_padding, column_padding, show_borders = setup_format_options()
        frag_colors = setup_fragment_colors()

        # Fragment colors

    # Return all parameters=
    return {
        'peptide_sequence': peptide_sequence,
        'charge': charge,
        'is_monoisotopic': is_monoisotopic,
        'fragment_types': fragment_types,
        'use_mass_bounds': use_mass_bounds,
        'min_mz': min_mz,
        'max_mz': max_mz,
        'precision': precision,
        'row_padding': row_padding,
        'column_padding': column_padding,
        'show_borders': show_borders,
        'frag_colors': frag_colors
    }



def setup_fragment_checkboxes():
    """Setup fragment ion type checkboxes"""
    st.subheader('Fragment Ions', divider='grey')
    c1, c2, c3 = st.columns(3)

    with c1:
        a = st.checkbox('a', value='a' in DEFAULT_FRAGMENT_TYPES, key='a')
        x = st.checkbox('x', value='x' in DEFAULT_FRAGMENT_TYPES, key='x')

    with c2:
        b = st.checkbox('b', value='b' in DEFAULT_FRAGMENT_TYPES, key='b')
        y = st.checkbox('y', value='y' in DEFAULT_FRAGMENT_TYPES, key='y')

    with c3:
        c = st.checkbox('c', value='c' in DEFAULT_FRAGMENT_TYPES, key='c')
        z = st.checkbox('z', value='z' in DEFAULT_FRAGMENT_TYPES, key='z')

    fragment_types = [ft for ft, flag in zip('abcxyz', [a, b, c, x, y, z]) if flag]
    return fragment_types

def setup_fragment_pills():
    """Setup fragment pill options"""
    fragment_pills = st.pills('Fragment Ions',
                              selection_mode='multi',
                              options=list('abcxyz'),
                              default=list(DEFAULT_FRAGMENT_TYPES),  # Use default fragment types from constants
                              key='fragment_types')

    return fragment_pills

def setup_nterm_fragment_pills():
    """Setup fragment pill options"""
    fragment_pills = st.segmented_control('N-Term Fragments',
                              selection_mode='multi',
                              options=list('abc'),
                              default=list('ab'),  # Use default fragment types from constants
                              key='nterm_fragment_types')

    return fragment_pills

def setup_cterm_fragment_pills():
    """Setup fragment pill options"""
    fragment_pills = st.segmented_control('C-Term Fragments',
                              selection_mode='multi',
                              options=list('xyz'),
                              default=list('xy'),  # Use default fragment types from constants
                              key='cterm_fragment_types')

    return fragment_pills

def setup_term_split_fragment_types():
    """Setup fragment pill options"""
    abc_frags = setup_nterm_fragment_pills()
    xyz_frags = setup_cterm_fragment_pills()

    return abc_frags + xyz_frags

def setup_format_options():
    """Setup format options"""
    with st.expander('Format Options'):
        precision = st.number_input('Decimal Places', value=DEFAULT_PRECISION, min_value=0, max_value=10,
                                     url_key='decimal_places')

        c1, c2 = st.columns(2)
        with c1:
            row_padding = st.number_input('Row Padding (px)', value=DEFAULT_ROW_PADDING, min_value=0, max_value=100,
                                           url_key='row_padding')
        with c2:
            column_padding = st.number_input('Column Padding (px)', value=DEFAULT_COLUMN_PADDING, min_value=0,
                                              max_value=100,
                                              url_key='column_padding')

        show_borders = st.checkbox('Show Borders', value=DEFAULT_SHOW_BORDERS, url_key='show_borders')

    return precision, row_padding, column_padding, show_borders


def setup_fragment_colors():
    """Setup fragment color options"""
    with st.expander('Fragment Colors'):
        c1, c2, c3 = st.columns(3)
        with c1:
            a_color = st.color_picker('a color', DEFAULT_A_COLOR, url_key='a_color')
            x_color = st.color_picker('x color', DEFAULT_X_COLOR, url_key='x_color')

        with c2:
            b_color = st.color_picker('b color', DEFAULT_B_COLOR, url_key='b_color')
            y_color = st.color_picker('y color', DEFAULT_Y_COLOR, url_key='y_color')

        with c3:
            c_color = st.color_picker('c color', DEFAULT_C_COLOR, url_key='c_color')
            z_color = st.color_picker('z color', DEFAULT_Z_COLOR, url_key='z_color')

    return {
        'a': a_color,
        'b': b_color,
        'c': c_color,
        'x': x_color,
        'y': y_color,
        'z': z_color
    }


def display_results(style_df, params):
    """Display the results of fragment calculation"""

    st.caption(f'Made with [peptacular {pt.__version__}](https://pypi.org/project/peptacular/)')

    # Display the fragment table
    html = style_df.to_html()
    # Update the column headers to include the superscript charge state
    for col in ["A", "B", "C", "X", "Y", "Z"]:
        html = html.replace(f'{col}</th>', f'{col}<sup>{params["charge"]}+</sup></th>')

    st.markdown(html, unsafe_allow_html=True)

    # Show mass bounds if enabled
    if params['use_mass_bounds']:
        st.markdown(f'**Bounds:** {params["min_mz"]} - {params["max_mz"]} *m/z*')

    # Show peptacular version
