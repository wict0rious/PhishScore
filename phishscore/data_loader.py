"""Load and clean the survey CSVs into analysis-ready DataFrames."""
import pandas as pd
from phishscore.config import VALUES_CSV, LABELS_CSV


def _parse_multi_select(value):
    if pd.isna(value) or str(value).strip() == "":
        return []
    return [int(x.strip()) for x in str(value).split(",") if x.strip().isdigit()]


def load_raw_data():
    df_values = pd.read_csv(VALUES_CSV, skiprows=[1, 2])
    df_labels = pd.read_csv(LABELS_CSV, skiprows=[1, 2])
    return df_values, df_labels


def clean_data(df):
    df = df.copy()
    df = df[df["Finished"] == 1].reset_index(drop=True)

    multi_select_cols = ["Q2", "Q3", "Q4", "Q5", "Q7", "Q11", "Q12", "Q13", "Q20"]
    for col in multi_select_cols:
        df[col] = df[col].apply(_parse_multi_select)

    int_cols = ["Q1", "Q8", "Q10", "Q18"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    float_cols = ["Q9", "Q14"]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_clean_data():
    df_values, df_labels = load_raw_data()
    return clean_data(df_values), df_labels
