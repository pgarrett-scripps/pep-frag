from dataclasses import dataclass
from typing import Literal, Optional
import streamlit as st
import streamlit as st
import streamlit_permalink as stp

from constants import (DEFAULT_PEPTIDE, DEFAULT_CHARGE, DEFAULT_MASS_TYPE, DEFAULT_FRAGMENT_TYPES,
    DEFAULT_USE_MASS_BOUNDS, DEFAULT_MIN_MZ, DEFAULT_MAX_MZ, DEFAULT_PRECISION,
    DEFAULT_ROW_PADDING, DEFAULT_COLUMN_PADDING, DEFAULT_SHOW_BORDERS,
    DEFAULT_A_COLOR, DEFAULT_B_COLOR, DEFAULT_C_COLOR,
    DEFAULT_X_COLOR, DEFAULT_Y_COLOR, DEFAULT_Z_COLOR
)

FRAGMENT_TYPES = Literal['a', 'b', 'c', 'x', 'y', 'z']
CAPTION_TYPES = Literal['horizontal', 'vertical']


@dataclass
class FragmentParams:
    peptide_sequence: str
    charge: int
    fragment_types: list[FRAGMENT_TYPES]
    mass_type: bool
    use_carbamidomethyl: bool
    condense_to_mass_notation: bool
    min_mz: Optional[float]
    max_mz: Optional[float]
    precision: int
    row_padding: int
    column_padding: int
    show_borders: bool
    display_type: CAPTION_TYPES 
    a_color: str
    b_color: str
    c_color: str
    x_color: str
    y_color: str
    z_color: str

    @property
    def frag_colors(self) -> dict[str, str]:
        return {
            'a': self.a_color,
            'b': self.b_color,
            'c': self.c_color,
            'x': self.x_color,
            'y': self.y_color,
            'z': self.z_color
        }

    @property
    def is_monoisotopic(self) -> bool:
        return self.mass_type == 'monoisotopic'
    
    @property
    def use_mass_bounds(self) -> bool:
        return self.min_mz is not None and self.max_mz is not None
    
    @property
    def is_horizontal_caption(self) -> bool:
        return self.display_type == 'horizontal'


def get_params() -> FragmentParams:
    st.subheader('Options', divider='grey')
    peptide_help_msg = """
    **Peptide Sequence**: Enter the peptide sequence to fragment. Include modifications in square brackets.
    """
    peptide_sequence = stp.text_input('Peptide Sequence (Proforma2.0 Notation)',
                                        value=DEFAULT_PEPTIDE,
                                        max_chars=2000,
                                        help=peptide_help_msg,
                                        key='peptide')
    charge = stp.number_input('Charge State',
                                min_value=0,
                                value=DEFAULT_CHARGE,
                                help='Charge state of the peptide',
                                key='charge')

    fragment_pills = stp.pills('Fragment Ions',
                            selection_mode='multi',
                            options=list('abcxyz'),
                            default=list(DEFAULT_FRAGMENT_TYPES),  # Use default fragment types from constants
                            help='Select fragment ion types to display',
                            key='fragment_types')

    mass_type = stp.radio(label='Mass Type',
                        options=['monoisotopic', 'average'],
                        help='Mass type to use for fragment calculation',
                        index=['monoisotopic', 'average'].index(DEFAULT_MASS_TYPE),
                        horizontal=True,
                        key='mass_type')

    # Additional options
    st.subheader('Additional Options', divider='grey')

    c1, c2 = st.columns(2)
    with c1:
        use_carbamidomethyl = stp.checkbox('Use carbamidomethyl C',
                                           value=False,
                                           help='Apply carbamidomethylation to cysteine residues',
                                           key='use_carbamidomethyl')
    with c2:
        condense_to_mass_notation = stp.checkbox('Condense to mass notation',
                                                 value=False,
                                                 help='Condense fragment ions to mass notation',
                                                 key='condense_to_mass_notation')
    use_mass_bounds = stp.toggle('Use Mass Bounds',
                                   value=DEFAULT_USE_MASS_BOUNDS,
                                   help='Use mass bounds for fragment ions',
                                   key='mass_bounds')

    min_mz, max_mz = None, None
    if use_mass_bounds:
        c1, c2 = stp.columns(2)
        with c1:
            min_mz = stp.number_input('Min m/z',
                                      value=DEFAULT_MIN_MZ,
                                      key='min_mz',
                                      help='Minimum m/z for fragment ions',
                                      step=100.0)
        with c2:
            max_mz = stp.number_input('Max m/z',
                                      value=DEFAULT_MAX_MZ,
                                      key='max_mz',
                                      help='Maximum m/z for fragment ions',
                                      step=100.0)

    with st.expander('Display Options'):
        # Format options
        precision = stp.number_input('Decimal Places',
                                     value=DEFAULT_PRECISION,
                                     min_value=0,
                                     max_value=10,
                                     help='Number of decimal places to display',
                                     url_key='decimal_places')

        c1, c2 = st.columns(2)
        with c1:
            row_padding = stp.number_input('Row Padding (px)',
                                           value=DEFAULT_ROW_PADDING,
                                           min_value=0,
                                           max_value=100,
                                           help='Padding for rows in the table',
                                           url_key='row_padding')
        with c2:
            column_padding = stp.number_input('Column Padding (px)',
                                              value=DEFAULT_COLUMN_PADDING,
                                              min_value=0,
                                              max_value=100,
                                              help='Padding for columns in the table',
                                              url_key='column_padding')

        show_borders = stp.checkbox('Show Borders',
                                    value=DEFAULT_SHOW_BORDERS,
                                    help='Show borders in the table',
                                    url_key='show_borders')
        #horizontal or vertical
        display_type = stp.radio('Caption Type',
                                 options=['vertical', 'horizontal'],
                                 index=0,
                                 horizontal=True,
                                 help='Select caption type for the table',
                                 key='display_type')
    
    with st.expander('Fragment Colors'):
        c1, c2, c3 = st.columns(3)
        with c1:
            a_color = stp.color_picker('a color', DEFAULT_A_COLOR, url_key='a_color')
            x_color = stp.color_picker('x color', DEFAULT_X_COLOR, url_key='x_color')

        with c2:
            b_color = stp.color_picker('b color', DEFAULT_B_COLOR, url_key='b_color')
            y_color = stp.color_picker('y color', DEFAULT_Y_COLOR, url_key='y_color')

        with c3:
            c_color = stp.color_picker('c color', DEFAULT_C_COLOR, url_key='c_color')
            z_color = stp.color_picker('z color', DEFAULT_Z_COLOR, url_key='z_color')

    params = FragmentParams(
        peptide_sequence=peptide_sequence,
        charge=charge,
        fragment_types=fragment_pills,
        mass_type=mass_type,
        use_carbamidomethyl=use_carbamidomethyl,
        condense_to_mass_notation=condense_to_mass_notation,
        min_mz=min_mz,
        max_mz=max_mz,
        precision=precision,
        row_padding=row_padding,
        column_padding=column_padding,
        show_borders=show_borders,
        display_type=display_type,
        a_color=a_color,
        b_color=b_color,
        c_color=c_color,
        x_color=x_color,
        y_color=y_color,
        z_color=z_color
    )

    return params