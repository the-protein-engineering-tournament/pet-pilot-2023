from typing import Union
import re
from scipy.stats import median_abs_deviation
import pandas as pd


def unique_elements(s):
    v = s.values
    if isinstance(v[0], list):
        v = map(lambda x: "-".join(x), v)
    return len(set(v))


def drop_constant(df: pd.DataFrame) -> pd.DataFrame:
    constant = df.apply(unique_elements).loc[lambda d: d == 1].index.values
    return df.drop(columns=list(constant))


def match_sequence_to_first_pattern(sequence: str, patterns: list[str]):
    for p in patterns:
        if re.match(p.removesuffix("*"), sequence):
            return p
    return None


def plate_median_normalize(
    df: pd.DataFrame,
    controls: Union[int, list[int]],
    mad_scale: bool = False
) -> pd.DataFrame:
    """
    Normalize by median of plates

    (1) find the plate medians for each plate, find the median of the plate medians,
        record this as the overall effect.

    (2) subtract each element in a plate by its plate median, do this for all plates.
    """
    if isinstance(controls, int):
        controls = [controls]
    controls = df.loc[lambda d: (d.objectid.isin(controls))][["plate_name", "output"]]
    plate_effect = controls.groupby("plate_name").median(numeric_only=True).output
    plate_scale = controls.groupby("plate_name").apply(median_abs_deviation)
    for plate in controls.plate_name.unique():
        df.loc[lambda d: d.plate_name == plate, "output"] -= plate_effect[plate]
        if mad_scale:
            df.loc[lambda d: d.plate_name == plate, "output"] /= plate_scale[plate]
    return df.assign(output=lambda d: d.output + abs(d.output.min()))


def summary_to_training(
    df: pd.DataFrame,
    ref: str = None,
    pi_stat: str = None,
    normalizer: str = None,
    unstressed_min: float = 5.0,
    concentration_min: float = 100.0,
) -> pd.DataFrame:
    [protocol] = list(df["data_analysis_protocol"].unique())
    if protocol in {"ACTIVITYASSAY", "ACTIVITYASSAY-NOWT", "ACTIVITYASSAY-SRI"}:
        dd = summary_to_training_activity_assay(df, pi_stat=pi_stat).loc[
            lambda d: d["well_statistics.in_reference_to"] == ref
        ]
        if normalizer is not None:
            dd = dd.loc[lambda d: d["well_statistics.relative_to"] == normalizer]

    elif protocol == "ACTIVITYASSAY-DILUTION":
        dd = summary_to_training_activity_assay_dilution(df).loc[
            lambda d: d["well_statistics.in_reference_to"] == ref
        ]
        if normalizer is not None:
            dd = dd.loc[lambda d: d["well_statistics.relative_to"] == normalizer]
    elif protocol.startswith("RESIDUALACTIVITYASSAY"):
        dd = summary_to_training_residual(
            df, unstressed_min=unstressed_min, pi_stat=pi_stat or "residual_activity"
        )
    elif protocol.startswith("SPECIFICACTIVITYASSAY"):
        dd = summary_to_training_specific_activity(df, pi_stat=pi_stat)
    elif protocol.startswith("CONCENTRATIONASSAY"):
        dd = summary_to_training_expression(df, pi_stat=pi_stat)
        if normalizer is not None:
            dd = dd.loc[lambda d: d["well_statistics.relative_to"] == normalizer]
    else:
        raise NotImplementedError()

    return (
        dd.drop_duplicates()
        .loc[lambda d: d.analysis_role.isin({"NO_ROLE", "CONTROL"})]
        .pipe(filter_low_well_concentration, threshold=concentration_min)
        .drop(
            columns=["well_statistics.in_reference_to", "batch_id", "well_statistics"]
        )
        .rename(columns={"well_statistics.value": "output"})
    )


base_cols = [
    "testset",
    "row",
    "column",
    "plate_name",
    "well_location",
    "objectid",
    "team",
    "batch_id",
    "analysis_role",
    "sequence",
    "well_concentration",
    "well_statistics",
    "well_statistics.value",
    "well_statistics.in_reference_to",
    "well_statistics.relative_to",
]


def filter_low_well_concentration(
    df: pd.DataFrame, threshold: float = 100
) -> pd.DataFrame:
    max_concentration = (
        df.loc[lambda d: d.analysis_role != "STANDARD"][
            ["testset", "plate_name", "well_location", "well_concentration"]
        ]
        .drop_duplicates()
        .groupby(["testset", "plate_name", "well_location"], as_index=False)
        .max()
        .assign(_not_low=lambda d: d.well_concentration > threshold)
        .drop(columns=["well_concentration"])
    )
    return (
        df.merge(max_concentration)
        .loc[lambda d: d["_not_low"]]
        .drop(columns=["_not_low"])
    )


def filter_low_activity(df: pd.DataFrame, threshold: float = 5) -> pd.DataFrame:
    unstressed = (
        df.loc[
            lambda d: d["well_statistics"] == "blank_corrected_unstressed_result_mean"
        ][["testset", "plate_name", "well_location", "well_statistics.value"]]
        .drop_duplicates()
        .groupby(["testset", "plate_name", "well_location"], as_index=False)
        .mean()
        .assign(_not_low=lambda d: d["well_statistics.value"] > threshold)
        .drop(columns=["well_statistics.value"])
    )
    return df.merge(unstressed).loc[lambda d: d["_not_low"]].drop(columns=["_not_low"])


def resolve_batch_id(df: pd.DataFrame) -> pd.DataFrame:
    batch_to_object = df.set_index("batch_id").objectid.to_dict()
    df = df.copy()
    for c in df.columns:
        if c.endswith("in_reference_to") or c.endswith("relative_to"):
            df[c] = df[c].map(batch_to_object)
    return df


def activity_assay_select_statistic(
    df: pd.DataFrame, pi_stat: str = "activity_pi"
) -> pd.DataFrame:
    return df.loc[lambda d: d["well_statistics"].isin([pi_stat])]


def residual_assay_select_statistic(
    df: pd.DataFrame, pi_stat: str = "residual_activity"
) -> pd.DataFrame:
    return df.loc[lambda d: d["well_statistics"].isin([pi_stat])]


def specific_activity_select_statistic(
    df: pd.DataFrame, pi_stat="specific_activity_pi"
) -> pd.DataFrame:
    return df.loc[lambda d: d["well_statistics"].isin([pi_stat])]


def expression_assay_select_statistic(
    df: pd.DataFrame, pi_stat: str = "expression_pi"
) -> pd.DataFrame:
    return df.loc[lambda d: d["well_statistics"].isin([pi_stat])]


def activity_assay_dilution_select_statistic(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[lambda d: d["well_statistics"].isin(["auc_ratio"])]


def summary_to_training_activity_assay(
    df: pd.DataFrame, pi_stat: str = "activity_pi"
) -> pd.DataFrame:
    return (
        df[base_cols]
        .pipe(resolve_batch_id)
        .pipe(activity_assay_select_statistic, pi_stat=pi_stat)
    )


def summary_to_training_residual(
    df: pd.DataFrame,
    unstressed_min: float = 5,
    pi_stat: str = "residual_activity",
) -> pd.DataFrame:
    return (
        df[base_cols]
        .pipe(filter_low_activity, threshold=unstressed_min)
        .pipe(residual_assay_select_statistic, pi_stat=pi_stat)
    )


def summary_to_training_specific_activity(
    df: pd.DataFrame,
    pi_stat="specific_activity_pi",
) -> pd.DataFrame:
    return df[base_cols].pipe(specific_activity_select_statistic, pi_stat=pi_stat)


def summary_to_training_expression(
    df: pd.DataFrame, pi_stat: str = "expression_pi"
) -> pd.DataFrame:
    return df[base_cols].pipe(expression_assay_select_statistic, pi_stat=pi_stat)


def summary_to_training_activity_assay_dilution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[base_cols]
        .pipe(resolve_batch_id)
        .pipe(activity_assay_dilution_select_statistic)
    )
