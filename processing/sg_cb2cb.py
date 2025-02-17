from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
import numpy as np

survey_doc = "sg/surveylegend.doc"

with open(survey_doc, 'r') as file:
    data = file.read()

type_map = {
    "TABLE": "TABLE",
    "INSTRUCTIONS": "INSTRUCTIONS",
    "MENU": "numeric",
    "RADIO": "categorical",
    "TEXTBOX": "text"
}

table_list = {}

soup = BeautifulSoup(data, 'html.parser')
qids = soup.find_all('h4')
qids = [qid for qid in qids if "QID" in qid.contents[0]]


cb = pd.DataFrame(columns=["Response", "Value", "Variable", "Full", "Name", "Type", "Summary", "Aliases", "Rows"])

for qid in qids:
    qs = pd.DataFrame(
        columns=["Response", "Value", "Variable", "Full", "Name", "Type", "Summary", "Aliases", "Rows"]
    )
    variable_h4 = qid
    variable = variable_h4.contents[0].split(":")[-1].strip().replace(" ", "_").replace(":", "")
    wording_h4 = qid.find_next("h4")
    wording = wording_h4.contents[0]
    table_div = wording_h4.find_next("div")

    r = re.compile("Type: (.*)</div>")
    qtype = type_map[r.search(str(table_div)).group(1)]

    if qtype == "INSTRUCTIONS":
        continue
    if variable == "hash":
        continue

    try:
        table = table_div.find_next("table")
        table = pd.read_html(str(table))[0][1:]
        qs["Response"] = table[0]
        qs["Value"] = table.index
    except ValueError:
        pass

    if qtype == "TABLE":
        table_list.update({variable: wording})
        continue
    elif variable in table_list.keys():
        qtype = "categorical_array"
        alias = wording.lower().replace(" ", "_") + variable
        qs["Aliases"] = alias
        qs["Rows"] = wording
        wording = table_list[variable]

    qs["Variable"] = variable
    qs["Name"] = variable
    qs["Full"] = wording
    qs["Type"] = qtype

    cb = cb.append(qs)


cb.to_csv("sg/Louisiana Poll/surveylegend_codebook.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)