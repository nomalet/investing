import imp
import py_compile
from re import L
from site import execsitecustomize
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


# Extract most recent closing price from yahoo
def price(ticker):
    # TODO: Implement forex calculations
    try:
        company = yf.Ticker(ticker)
        df = company.history(period="1day")
        df.reset_index(drop=True, inplace=True)
        price = df.loc[0, "Close"]

    except:
        print(ticker)

    return price


# Load the raw income statement data and convert to dataframe
def data_loader(file_path, sheet_name, statement_type):
    # Set number of rows to skip
    skiprows = 1

    # Set index column
    if statement_type == "cashflow":
        index_label = "Cash Flow Statement"
        target_col = "cash flow per share"
        renamed_col = "fcf_share"
    elif statement_type == "income":
        index_label = "Income Statement"
        target_col = "dividends per share"
        renamed_col = "div_share"
    elif statement_type == "ratios":
        index_label = "Ratios"
        target_col = "Return On Equity %"
        renamed_col = "roe"
    elif statement_type == "multiples":
        index_label = "Multiples"
        target_col = "LTM Book Value per Share"
        renamed_col = "bv_share"
        skiprows = 0  # For some reason copy/paste is different here
    else:
        raise ("Unexpected financial statement")

    # Open the file
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl", skiprows=skiprows)

    df.set_index(index_label, inplace=True)
    # Drop LTM if it exists and set the index to years
    df.drop("LTM", axis=1, errors="ignore", inplace=True)
    # Set the index to years
    df.columns = pd.to_datetime(df.columns).year
    df = df.T
    # Drop NaN column names and then set all column names to lower case
    mask = pd.isna(df.columns)
    df = df.loc[:, ~mask]
    df.columns = [c.lower() for c in df.columns]
    # Rename column
    col_name = target_col.lower()
    df = df.loc[:, [col_name]]
    df.columns = [renamed_col]

    return df


def sensitivity_plot(data_dict, company_name, high, mid, low, forecast_type, start_at=None):
    """
    Sensitivity plot for either fcf or dividend growth
    """
    df = data_dict[company_name]

    # Trim leading NaN in fcf so that plots start from non-nan date
    if start_at is None:
        start_date = df.first_valid_index()
    else:
        start_date = start_at

    df = df.loc[df.index >= start_date].copy()

    # Select FCF or Dividends forecasts
    if forecast_type == "fcf":
        tag = "fcf_share"
    elif forecast_type == "div":
        tag = "div_share"
    elif forecast_type == "bv":
        tag = "bv_share"
        df = df.groupby(df.index).mean()  # Multiples only quarterly for some reason
    else:
        raise ("Incorrect forecast type")

    # Generate curves for growth at P10, P50, P90 rates (in percentage)
    df["high"] = df.loc[df.index[0], tag] * (1 + high / 100) ** (df.index - df.index[0])
    df["mid"] = df.loc[df.index[0], tag] * (1 + mid / 100) ** (df.index - df.index[0])
    df["low"] = df.loc[df.index[0], tag] * (1 + low / 100) ** (df.index - df.index[0])

    plotting_cols = [tag, "high", "mid", "low"]

    fig, ax = plt.subplots(1, 2, figsize=(15, 5))

    df[plotting_cols].plot(style=["-", "-.", "-.", "-."], ax=ax[0])
    df[plotting_cols].plot(style=["-", "-.", "-.", "-."], ax=ax[1], logy=True)

    ax[0].set_ylabel("$/share")
    ax[1].set_ylabel("log $/share")

    plt.suptitle(f"{company_name}\n High:{high}   Mid:{mid}   Low:{low}")

    plt.show()


def plot_financials(data, ticker):
    fig, ax = plt.subplots(1, 2, figsize=(15, 5))

    data["book_value"].plot(ax=ax[0])
    data["return_equity"].plot(ax=ax[1])

    ax[0].set_title("Book Value per Share")
    ax[1].set_title("Return on Equity")

    plt.suptitle(f"{ticker}")

    plt.show()


def growth_calc(starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate):
    # Set a range for first 5 years
    years = np.arange(1, 6)

    # Reset rates as fraction from percentage
    discount_rate /= 100
    growth_rate1 /= 100
    growth_rate2 /= 100
    perpetual_rate /= 100

    # Calculate FCF for first stage
    fcf_stage1 = starting_fcf * (1 + growth_rate1) ** years
    # Calculate FCF for second stage
    fcf_stage2 = fcf_stage1[-1] * (1 + growth_rate2) ** (years)
    # Set to dataframes
    df1 = pd.DataFrame(data=fcf_stage1, index=years, columns=["value"])
    df2 = pd.DataFrame(data=fcf_stage2, index=years + 5, columns=["value"])
    # Add a terminal value
    terminal_value = fcf_stage2[-1] * (1 + perpetual_rate) / (discount_rate - perpetual_rate)
    # Concatenate the dataframes and set last row as terminal value
    df = pd.concat([df1, df2])
    # Reset index to create a years column
    df = df.reset_index().rename(columns={"index": "years"})
    df.loc[11] = 10, terminal_value

    return df


def cash_to_investor(data, payout_ratio):
    df = data.copy()

    # Reset rates as fraction from percentage
    payout_ratio /= 100

    # Add a payout ratio to generate dividends
    df["dividends"] = df["value"] * payout_ratio
    # Set dividends as cash to investor during period of holding asset
    df["cash_to_investor"] = df["dividends"]
    # Set terminal value to cash to investor (do not reduce by payout ratio)
    mask = df.last_valid_index()
    df.loc[mask, "cash_to_investor"] = df.loc[mask, "value"]

    return df


def pv_calc(data, discount_rate):
    df = data.copy()

    # Reset rate as fraction from percentage
    discount_rate /= 100
    # Calculate present value
    df["PV"] = df["cash_to_investor"] * (1 + discount_rate) ** (
        df.loc[df["years"] == 1, "years"].values - df["years"].values - 1
    )

    return df


def pv_full_output(
    starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate, payout_ratio
):
    # Calculate the FCF growth
    df_fcf = growth_calc(starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate)
    # Calculate cash to investor while holding asset (dividends)
    df_div = cash_to_investor(df_fcf, payout_ratio)
    # Calculate the Present Value
    df_pv = pv_calc(df_div, discount_rate)
    # Set the PV dataframe to a dictionary for ease of manipulation later
    pv_dict = {"full_pv": df_pv}
    return pv_dict


def npv_calc(starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate, payout_ratio):
    # Calculate the Present Value and set to a dictionary
    pv_dict = pv_full_output(
        starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate, payout_ratio
    )
    # Exctract the dataframe and sum the PV
    df_pv = pv_dict["full_pv"]
    npv = df_pv["PV"].sum()

    return npv


def npv_financials(book_value_per_share, return_on_equity, discount_rate, perpetual_rate):
    # Use Excess Returns??? for financial and insurance companies
    excess = (return_on_equity - discount_rate) * book_value_per_share
    terminal_value = excess / (discount_rate - perpetual_rate)
    npv = book_value_per_share + terminal_value

    return npv
