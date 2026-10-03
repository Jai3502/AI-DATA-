import pandas as pd
import numpy as np

file_path = "storage/datasets/175a7c5c-213d-43e3-bb0d-2ed9afc3a70c/9541336d-f6e1-49d1-bf9e-3bc1cb6ac364.csv"

df = pd.read_csv(file_path)

data = df[["Date", "Weekly_Sales", "Holiday_Flag"]].copy()

data["Date"] = pd.to_datetime(
    data["Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

data["Weekly_Sales"] = pd.to_numeric(
    data["Weekly_Sales"],
    errors="coerce"
)

data["Holiday_Flag"] = pd.to_numeric(
    data["Holiday_Flag"],
    errors="coerce"
)

data = (
    data.dropna()
    .sort_values("Date")
    .groupby("Date", as_index=False)
    .agg({
        "Weekly_Sales": "sum",
        "Holiday_Flag": "max"
    })
)

trend_values = []

for i in range(4, len(data)):
    y = data["Weekly_Sales"].iloc[i-4:i].to_numpy()
    x = np.arange(4)

    slope = np.polyfit(x, y, 1)[0]

    trend_values.append({
        "Date": data["Date"].iloc[i],
        "Weekly_Sales": data["Weekly_Sales"].iloc[i],
        "trend_4w": slope
    })

trend_diagnostic = pd.DataFrame(trend_values)

print(trend_diagnostic.tail(30).to_string(index=False))