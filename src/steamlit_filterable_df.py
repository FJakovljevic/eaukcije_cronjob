from enum import Enum

import streamlit as st
from streamlit_column_pickers import PickerFactory


class FilterLocations(Enum):
    SIDEBAR = 1


class StreamlitFilterableDF:
    def __init__(self, df, columns_to_filter, session_key="default", filter_location=FilterLocations.SIDEBAR) -> None:
        self.original_df = df
        self.filter_location = filter_location
        self.columns_to_filter = columns_to_filter

        # create session state that fill save active filters
        self.session_key = session_key
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {col: PickerFactory.create(df[col]) for col in columns_to_filter}

    @property
    def active_filters(self):
        return st.session_state[self.session_key]

    def display(self, **kwargs):
        self.display_filters()
        st.dataframe(self.filtered_df(), **kwargs)

    def display_filters(self):
        if self.filter_location == FilterLocations.SIDEBAR:
            with st.sidebar:
                self.display_sidebar_filters()

    def display_sidebar_filters(self):
        filter_change = False
        for column, picker in self.active_filters.items():
            pd_series = self.filtered_df(exclude_col=column)[column]
            filter_change = filter_change or picker.render_and_update(pd_series)

        if filter_change:
            st.rerun()

    def filtered_df(self, exclude_col=None):
        filters = (picker.filter for col, picker in self.active_filters.items() if picker and col != exclude_col)
        filter = " and ".join(filters)
        return self.original_df.query(filter) if filter else self.original_df
