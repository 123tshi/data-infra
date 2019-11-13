import pandas as pd
import numpy as np

cb = pd.read_csv("sg/LA Poll/la_ky_codebook.csv")
df = pd.read_csv("sg/VITMS_ LA Gov Run Off - 11-12-19.csv")


cbc = cb[(cb["Type"] == "categorical") | (cb["Type"] == "categorical_array")]
all_vars = np.append(cbc[pd.isna(cbc["Aliases"])]["Variable"].unique(), cbc["Aliases"].unique())
all_vars = all_vars[~pd.isna(all_vars)]

for variable in all_vars:
    try:
        df[variable] = df[variable].apply(lambda x: str(x).split(" - ")[0])
    except KeyError as e:
        print(e)


df.to_csv("sg/LA Poll/la_poll_results_data.csv", index=False, na_rep="")
