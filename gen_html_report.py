import pandas as pd
import glob
import re

q_dirs = fs_files = glob.glob('figs/LAPoll/*')
df = pd.read_csv('sg/LA Poll/la_poll_results_data.csv')
cb = pd.read_csv('sg/LA Poll/la_ky_codebook.csv')

pd.set_option('display.width', 1000)
pd.set_option('colheader_justify', 'center')

html_string = '''
<html>
  <head><title>Report</title></head>
  <link rel="stylesheet" type="text/css" href="df_style.css"/>
  <body>
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
	wording = re.sub(r" ?\<[^>]+\>", " ", cb[cb["Variable"]==index]["Full"].iloc[0])
	# tab = tab.append(tab.sum(numeric_only=True), ignore_index=True)
	tab = tab.rename(columns={"Response": "Response\n(n={n})".format(n=(~pd.isna(df[index])).sum()),
							  index: ""})
	table = tab.to_html(classes='mystyle', na_rep="Sum", float_format="{:0.0f}%".format, index=False)
	div = '<div><p>{wording}</p>\n{table}</div><br>'.format(wording=wording, table=table.replace("\\n", "<br>"))
	q_divs.append(div)


# OUTPUT AN HTML FILE
with open('lapoll.html', 'w') as f:
	f.write(html_string.format(questions="\n".join(q_divs)))

