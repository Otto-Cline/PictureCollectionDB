from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import pandas as pd
import re

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
DBNAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"
engine = create_engine(DATABASE_URL)

# Makes path to excel file because it was looking through src for some reason
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_root, "assets", "PCIndex.xlsx")

print("Reading Excel from:", file_path)
df = pd.read_excel(file_path, sheet_name="Subjects oneCell", header=None)
df.columns = ["Heading", "Call Symbol"]


# Turns first column of excel sheet into a heading, subheading, subsubheading, and year
# First line is saying "split the heading part of the row into an array"
def parse_heading(row):
    parts = row["Heading"].split("--")

    main = None
    sub = None
    subsub = None
    year = None

    if len(parts) == 1:
        main = parts[0]
    elif len(parts) == 2 and parts[1][0].isnumeric() and parts[1][1].isnumeric():
        main, year = parts
    elif len(parts) == 2:
        main, sub = parts
    elif len(parts) == 3:
        main, sub, subsub = parts
        if re.search(r"\d{4}s|1899 and earlier", subsub):
            year = subsub
            subsub = None

    elif len(parts) == 4:
        main, sub, subsub, year = parts

    return pd.Series([main, sub, subsub, year])


# Applies parse_heading to every row of the dataframe, and tells it to put each part in the new
# columns that we specify
df[["Main Heading", "Subheading", "Sub-subheading", "Year"]] = df.apply(parse_heading, axis=1)


# Does the same to the call symbol column as we did to the heading column
def parse_call_symbol(row):
    call_symbol = row["Call Symbol"]
    if pd.isna(call_symbol):
        return pd.Series([None, None, None])

    # Split by - unless it is followed by a closing paranthesis one character away
    segments = re.split(r"-(?![^()]*\))", call_symbol)

    main_call = None
    sub_call = None
    year_call = None

    if len(segments) == 1:
        main_call = segments[0]
    elif len(segments) == 2 and segments[1][0].isnumeric():
        main_call, year_call = segments
    elif len(segments) == 2:
        main_call, sub_call = segments
    elif len(segments) == 3:
        main_call, sub_call, year_call = segments
    return pd.Series([main_call, sub_call, year_call])


df[["Call Symbol", "Subheading Call Symbol", "Year Call Symbol"]] = df.apply(parse_call_symbol, axis=1)

# Takes the dataframe and puts it into the sql database
with engine.begin() as conn:
    for _, row in df.iterrows():
        conn.execute(text("""
                          INSERT INTO subjects (main_heading, subheading, sub_subheading, year,
                                                        call_symbol, subheading_call_symbol, year_call_symbol)
                          VALUES (:main, :sub, :subsub, :year,
                                  :call, :subcall, :yearcall)
                          """), {
                         "main": row["Main Heading"],
                         "sub": row["Subheading"],
                         "subsub": row["Sub-subheading"],
                         "year": row["Year"],
                         "call": row["Call Symbol"],
                         "subcall": row["Subheading Call Symbol"],
                         "yearcall": row["Year Call Symbol"]
                     })

print("Done.")