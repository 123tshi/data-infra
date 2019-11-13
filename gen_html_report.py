import pandas as pd
import glob
import re
import pdfkit

q_dirs = fs_files = glob.glob('figs/LAPoll/*')
df = pd.read_csv('data/sg/LA Poll/la_poll_results_data.csv')
cb = pd.read_csv('data/sg/LA Poll/la_ky_codebook.csv')

pd.set_option('display.width', 1000)
pd.set_option('colheader_justify', 'center')

html_string = '''
<html>
  <head><title>Report</title></head>
    <div id="content">
    <img src="logos/logo_transparent.png" weight="192" height="15"/>
  </div>
  <link rel="stylesheet" type="text/css" href="df_style.css"/>
  <body>
  	NB: subgroups with a n-size less than 50 (<50) are not shown on these cross-tabs. We choose not to display N<50 subgroups because the sample is too small to have statistical significance. We did, however, take samples of these subgroups for representational and weighting purposes to accurately reflect the electorate makeup.
  	<br>
  	<br>
    {questions}
  </body>
</html>.
'''

q_divs = []
for v in cb["Variable"].unique():
	d = "figs/LAPoll/" + v
	base_files = glob.glob(d + '/csv/*base.csv')
	if len(base_files) == 0:
		continue
	base_file = base_files[0]
	fs_files = glob.glob(d + '/csv/*fs.csv')
	tab = pd.read_csv(base_file)
	if tab.sum(numeric_only=True)[0] < 95 or tab.shape[0] > 20:
		continue
	fs_files.sort()
	for f in fs_files:
		print("    " + f)
		xtab = pd.read_csv(f)
		xtab = xtab[xtab[xtab.columns[0]].apply(lambda x: int(x.split("n=")[-1][:-1]) > 50)]
		label, index, value = xtab.columns
		tab = tab.join(xtab.pivot(index=index, columns=label)[value], on=index)

	if index == "sean_medicaid_expand_know":
		continue
	wording = re.sub(r" ?\<[^>]+\>", " ", cb[cb["Variable"] == index]["Full"].iloc[0])
	# tab = tab.append(tab.sum(numeric_only=True), ignore_index=True)
	tab = tab.rename(columns={"Response": "Response\n(n={n})".format(n=(~pd.isna(df[index])).sum()), index: ""})
	table = tab.to_html(classes='mystyle', na_rep="Sum", float_format="{:0.0f}%".format, index=False)
	div = '<div><p>{wording}</p>\n{table}</div><br>'.format(wording=wording, table=table.replace("\\n", "<br>"))
	q_divs.append(div)


# OUTPUT AN HTML FILE
with open('reports/html/lapoll.html', 'w') as f:
	f.write(html_string.format(questions="\n".join(q_divs)))

pdfkit.from_file('reports/html/lapoll.html', 'reports/pdf/lapoll.pdf')
