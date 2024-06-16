from abc import ABC, abstractmethod

import pandas as pd
import streamlit as st


class PickerFactory:
    @staticmethod
    def create(pd_series, label=None, value=None):
        name = pd_series.name
        print(name, pd_series.dtype)

        if pd_series.dtype == "bool":
            return BoolPicker(name, label, value)

        elif pd_series.dtype in ("category", "object"):
            return MultiselectPicker(name, label, value)

        elif pd.api.types.is_numeric_dtype(pd_series):
            min_val, max_val = pd_series.min(), pd_series.max()
            value = value or (min_val, max_val)
            return NumericPicker(name, label, min_val, max_val, value)

        elif pd.api.types.is_datetime64_any_dtype(pd_series):
            min_val, max_val = pd_series.dt.date.min(), pd_series.dt.date.max()
            value = value or (min_val, max_val)
            return DatePicker(name, label, pd_series.dt.date.min(), pd_series.dt.date.max(), value)

        else:
            raise ValueError("Unsupported data type for picker creation")


class Picker(ABC):
    def __init__(self, name, label, value=None):
        self.name = name
        self.value = value
        self.label = label or f"{name}:"

    def __eq__(self, o):
        if not isinstance(o, Picker):
            return False
        return self.label == o.label and self.value == o.value and self.name == o.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.label=}, {self.value=})"

    def __bool__(self):
        return bool(self.value)

    def update(self, value):
        if self.value == value:
            return False

        self.value = value
        return True

    @abstractmethod
    def render_and_update(self):
        pass

    @property
    @abstractmethod
    def filter(self):
        pass


class BoolPicker(Picker):
    def render_and_update(self, *args, **kwargs):
        selected = st.checkbox(self.label.strip(":"), value=self.value)
        return self.update(selected)

    @property
    def filter(self):
        return f"`{self.name}` == {self.value}"


class MultiselectPicker(Picker):
    def render_and_update(self, pd_series, *args, **kwargs):
        selected = self.value or []
        options = sorted(set(pd_series.dropna().to_list() + selected))
        selected = st.multiselect(self.label, options, default=selected)
        return self.update(selected)

    @property
    def filter(self):
        return f"`{self.name}`.isin({self.value})"


class NumericPicker(Picker):
    def __init__(self, name, label, min_value, max_value, value):
        super().__init__(name, label, value)
        self.min_value = min_value
        self.max_value = max_value

    def render_and_update(self, *args, **kwargs):
        selected = st.slider(self.label, self.min_value, self.max_value, self.value)
        return self.update(selected)

    @property
    def filter(self):
        return f"{self.value[0]} <= `{self.name}` <= {self.value[1]}"


class DatePicker(Picker):
    def __init__(self, name, label, min_date, max_date, value):
        super().__init__(name, label, value)
        self.min_date = min_date
        self.max_date = max_date

    def render_and_update(self, *args, **kwargs):
        selected = st.date_input(self.label, self.value, self.min_date, self.max_date)
        return self.update(selected)

    @property
    def filter(self):
        dt_col = f"`{self.name}`.dt.strftime('%Y-%m-%d')"
        filter_str = f"{dt_col}.ge('{self.value[0]}')"

        if len(self.value) > 1:
            return f"({filter_str} and {dt_col}.le('{self.value[1]}'))"

        return filter_str
