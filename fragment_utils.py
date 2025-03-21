from typing import List, Tuple, Optional, Dict
import pandas as pd
import peptacular as pt


def create_fragment_table(sequence: str, ion_types: List[str], charges: List[int], monoisotopic: bool) -> Tuple[
    List, pd.DataFrame]:
    """
    Create a fragment table for a given peptide sequence

    Args:
        sequence: The peptide sequence
        ion_types: List of ion types to generate (a, b, c, x, y, z)
        charges: List of charge states
        monoisotopic: Whether to use monoisotopic masses

    Returns:
        Tuple containing list of fragment objects and DataFrame of fragments
    """
    fragments = pt.fragment(sequence=sequence,
                            ion_types=ion_types,
                            charges=charges,
                            monoisotopic=monoisotopic)

    # convert list of dataclasses to list of dicts
    frag_df = pd.DataFrame([fragment.to_dict() for fragment in fragments])

    frag_df['number'] = None
    # for forward ions (a,b,c) set number to frag.end
    frag_df['number'] = frag_df.apply(lambda row: row['end'] if row['ion_type'] in 'abc' else row['number'], axis=1)

    # for reverse ions (x,y,z) set number to frag.start
    frag_df['number'] = frag_df.apply(lambda row: row['start'] if row['ion_type'] in 'xyz' else row['number'], axis=1)

    return fragments, frag_df


def style_fragment_table(
        sequence: str,
        fragment_types: List[str],
        charge: int,
        is_monoisotopic: bool,
        color_map: Optional[Dict[str, str]] = None,
        show_borders: bool = True,
        aa_col: Optional[str] = "Seq",
        pos_col: Optional[str] = "#>",
        neg_col: Optional[str] = "<#",
        caption: Optional[str] = None,
        decimal_places: int = 4,
        row_padding: int = 4,
        column_padding: int = 10,
        min_mass: Optional[float] = None,
        max_mass: Optional[float] = None,
):
    """
    Style a fragment table for display

    Args:
        sequence: The peptide sequence
        fragment_types: List of ion types to generate (a, b, c, x, y, z)
        charge: Charge state
        is_monoisotopic: Whether to use monoisotopic masses
        color_map: Dictionary mapping ion types to colors
        show_borders: Whether to show borders
        aa_col: Column name for amino acid sequence
        pos_col: Column name for position index (forward)
        neg_col: Column name for position index (reverse)
        caption: Caption for the table
        decimal_places: Number of decimal places to display
        row_padding: Padding for rows
        column_padding: Padding for columns
        min_mass: Minimum mass to highlight
        max_mass: Maximum mass to highlight

    Returns:
        Styled DataFrame for display
    """
    # Define default colors
    default_colors = {
        "A": "#8B4513",  # Brown
        "B": "#1f77b4",  # Blue
        "C": "#2ca02c",  # Green
        "X": "#ff7f0e",  # Orange
        "Y": "#d62728",  # Red
        "Z": "#9467bd",  # Purple
    }

    # If the user provides a color map, update defaults
    if color_map:
        color_map = {k.upper(): v for k, v in color_map.items()}
        default_colors.update(color_map)

    # Generate fragment data
    fragments, frag_df = create_fragment_table(sequence, fragment_types, [charge], is_monoisotopic)

    if frag_df.empty:
        import streamlit as st
        st.warning("No fragments found. Please check your input and try again.")
        st.stop()

    # Drop unnecessary columns
    frag_df = frag_df.drop(columns=['isotope', 'loss', 'parent_sequence'])
    frag_df.sort_values(by=['charge', 'ion_type', 'start'], inplace=True)
    frag_df.drop_duplicates(subset=['charge', 'ion_type', 'start', 'end'], inplace=True)

    components = pt.split(sequence, include_plus=True)
    data = {aa_col: components} if aa_col else {}

    # Process fragment ions
    for ion_type in sorted(fragment_types):
        if ion_type not in 'abcxyz':
            continue

        ion_df = frag_df[(frag_df['ion_type'] == ion_type) & (frag_df['charge'] == charge)]
        # fix copy warning
        ion_df = ion_df.copy()

        ion_df.sort_values(by=['number'], inplace=True)
        frags = ion_df['mz'].tolist()
        if ion_type in 'XYZ':
            frags = frags[::-1]
        data[ion_type.upper()] = frags

    # Create DataFrame
    df = pd.DataFrame(data)
    

    forward_cols = [col for col in df.columns if 'A' == col or 'B' == col or 'C' == col]
    reverse_cols = [col for col in df.columns if 'X' == col or 'Y' == col or 'Z' == col]

    df = df[forward_cols + [aa_col] + reverse_cols]

    # Add positional columns
    if pos_col and forward_cols:
        df.insert(0, pos_col, list(range(1, len(df) + 1)))
    if neg_col and reverse_cols:
        df[neg_col] = list(range(len(df), 0, -1))

    # Apply styling
    return apply_table_styling(
        df=df,
        forward_cols=forward_cols,
        reverse_cols=reverse_cols,
        default_colors=default_colors,
        show_borders=show_borders,
        caption=caption,
        decimal_places=decimal_places,
        row_padding=row_padding,
        column_padding=column_padding,
        min_mass=min_mass,
        max_mass=max_mass,
    ), fragments


def apply_table_styling(
        df: pd.DataFrame,
        forward_cols: List[str],
        reverse_cols: List[str],
        default_colors: Dict[str, str],
        show_borders: bool,
        caption: Optional[str],
        decimal_places: int,
        row_padding: int,
        column_padding: int,
        min_mass: Optional[float],
        max_mass: Optional[float],
):
    """
    Apply styling to the fragment table

    Args:
        df: DataFrame to style
        forward_cols: List of forward ion columns (A, B, C)
        reverse_cols: List of reverse ion columns (X, Y, Z)
        default_colors: Dictionary mapping ion types to colors
        show_borders: Whether to show borders
        caption: Caption for the table
        decimal_places: Number of decimal places to display
        row_padding: Padding for rows
        column_padding: Padding for columns
        min_mass: Minimum mass to highlight
        max_mass: Maximum mass to highlight

    Returns:
        Styled DataFrame for display
    """
    border = "1px solid #999" if show_borders else "none"

    styles = [
        {'selector': 'table', 'props': [
            ('border-collapse', 'collapse'),
            ('border-spacing', '0'),
            ('border', border),
        ]},
        {'selector': 'th, td', 'props': [
            ('text-align', 'center'),
            ('padding', f'{row_padding}px {column_padding}px'),
            ('line-height', '1'),
            ('border', border),
        ]},
        {'selector': 'tr', 'props': [
            ('border', border),
        ]},
        {'selector': 'th', 'props': [
            ('border-bottom', '1px solid'),
            ('font-weight', 'bold'),
        ]},
    ]

    styled_df = df.style \
        .hide(axis='index') \
        .set_table_styles(styles)

    def highlight_columns(val, color):
        return f'color: {color}; font-weight: bold;' if val else ''

    # Apply column colors - FIXED
    if 'A' in df.columns:
        styled_df = styled_df.map(lambda val: highlight_columns(val, default_colors['A']), subset=['A'])
    if 'B' in df.columns:
        styled_df = styled_df.map(lambda val: highlight_columns(val, default_colors['B']), subset=['B'])
    if 'C' in df.columns:
        styled_df = styled_df.map(lambda val: highlight_columns(val, default_colors['C']), subset=['C'])
    if 'X' in df.columns:
        styled_df = styled_df.map(lambda val: highlight_columns(val, default_colors['X']), subset=['X'])
    if 'Y' in df.columns:
        styled_df = styled_df.map(lambda val: highlight_columns(val, default_colors['Y']), subset=['Y'])
    if 'Z' in df.columns:
        styled_df = styled_df.map(lambda val: highlight_columns(val, default_colors['Z']), subset=['Z'])

    # Highlight mass bounds
    if min_mass and max_mass:
        styled_df = styled_df.map(
            lambda val: 'background-color: #ffcccc' if isinstance(val, (int, float)) and (
                        val > max_mass or val < min_mass) else '',
            subset=forward_cols + reverse_cols
        )

    if caption:
        styled_df = styled_df.set_caption(f'{caption}')

    # Get indices of the max values in 'C' and 'X' columns
    max_index_C = df['C'].idxmax() if 'C' in df.columns else None
    max_index_X = df['X'].idxmax() if 'X' in df.columns else None

    # Apply styling to hide max values - FIXED
    if 'C' in df.columns and max_index_C is not None:
        # Create a closure to capture the current value of max_index_C
        def hide_max_value_C(val):
            return 'color: transparent; background-color: transparent;' if df.loc[max_index_C, 'C'] == val else ''

        styled_df = styled_df.map(hide_max_value_C, subset=['C'])

    if 'X' in df.columns and max_index_X is not None:
        # Create a closure to capture the current value of max_index_X
        def hide_max_value_X(val):
            return 'color: transparent; background-color: transparent;' if df.loc[max_index_X, 'X'] == val else ''

        styled_df = styled_df.map(hide_max_value_X, subset=['X'])

    styled_df = styled_df.format(precision=decimal_places)

    return styled_df