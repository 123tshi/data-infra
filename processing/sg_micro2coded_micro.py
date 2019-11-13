import pandas as pd
import numpy as np


cb = pd.read_csv("data/sg/la_gov_results_data.csv")
df = pd.read_csv("data/sg/LA Poll/la_ky_codebook.csv")

cbc = cb[(cb["Type"] == "categorical") | (cb["Type"] == "categorical_array")]
all_vars = np.append(cbc[pd.isna(cbc["Aliases"])]["Variable"].unique(), cbc["Aliases"].unique())
all_vars = all_vars[~pd.isna(all_vars)]


def get_response_dict(variable):
    resps = cbc[cbc["Variable"] == variable]
    if len(resps) == 0:
        resps = cb[cb["Aliases"] == variable]
    return {r: v for i, (v, r) in resps[["Value", "Response"]].iterrows()}


for variable in all_vars:
    try:
        resps = get_response_dict(variable)
        #b print(resps)
        df[variable] = df[variable].apply(lambda x: resps.get(str(x)))
    except KeyError as e:
        print(e)


df.to_csv("sg/VA Poll/va_poll_results_data.csv", index=False)
