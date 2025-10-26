import pandas as pd

# Replace with your public Google Sheet link or just the ID
sheet_id = "1lhytKIPUvE3vhRggAbM_T1I3nJDGA_zBI7pfvMVs2oo"
sheet_name = "sales_data_sample_Kaggle"  # Change if your sheet name is different

# Construct the CSV export URL
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Read the sheet into a DataFrame
df = pd.read_csv(url)

# Normalize ORDERDATE to MM/DD/YYYY
if 'ORDERDATE' in df.columns:
    # Try to parse various common formats; invalid parsing -> NaT
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce', infer_datetime_format=True)
    # Format dates as MM/DD/YYYY; NaT values remain NaT and become empty strings if needed
    df['ORDERDATE'] = df['ORDERDATE'].dt.strftime('%m/%d/%Y')
else:
    print("WARNING: 'ORDERDATE' column not found in the sheet.")

# Print the contents
print(df)