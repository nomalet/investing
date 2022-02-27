import imp

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


# Extract most recent closing price from yahoo
def price(ticker):
    try:
        company = yf.Ticker(ticker)
        df = company.history(period="1day")
        df.reset_index(drop=True, inplace=True)
        price = df.loc[0, "Close"]

    except:
        print(ticker)

    return price


# Load the raw cashflow data and convert to dataframe
def cashflow_loader(file_path, sheet_name):
    # Open the file
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl", skiprows=1)
    # Set index column,
    df.set_index("Cash Flow Statement", inplace=True)
    # Drop LTM if it exists and set the index to years
    df.drop("LTM", axis=1, errors="ignore", inplace=True)
    # Set the index to years
    df.columns = pd.to_datetime(df.columns).year
    df = df.T
    # Rename column
    df = df.loc[:, ["Cash Flow per Share"]]
    df.columns = ["FCF_share"]

    return df


def sensitivity_plot(data_dict, company_name, high, mid, low, start_at=None):
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

    tag = "FCF_share"

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


def pv_calc(data, discount_rate):
    df = data.copy()

    # Reset rate as fraction from percentage
    discount_rate /= 100
    # Calculate present value
    df["PV"] = df["value"] * (1 + discount_rate) ** (
        df.loc[df["years"] == 1, "years"].values - df["years"].values - 1
    )

    return df


def pv_full_output(starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate):
    # Calculate the FCF growth
    df_fcf = growth_calc(starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate)
    # Calculate the Present Value
    df_pv = pv_calc(df_fcf, discount_rate)
    # Set the PV dataframe to a dictionary for ease of manipulation later
    pv_dict = {"full_pv": df_pv}
    return pv_dict


def npv_calc(starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate):
    # Calculate the Present Value and set to a dictionary
    pv_dict = pv_full_output(
        starting_fcf, discount_rate, growth_rate1, growth_rate2, perpetual_rate
    )
    # Exctract the dataframe and sum the PV
    df_pv = pv_dict["full_pv"]
    npv = df_pv["PV"].sum()

    return npv
