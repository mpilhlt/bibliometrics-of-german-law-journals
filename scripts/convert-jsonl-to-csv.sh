# convert JSONLines into json and select wanted fields
JQ_CMD='
[ .[] | {
  id: .id,
  title: .title,
  issn: (.issn | join(" ")),
  alternativeTitle: (if .alternativeTitle then (.alternativeTitle | join("; ")) else null end),
  otherTitleInformation: (if .otherTitleInformation then (.otherTitleInformation | join("; ")) else null end),
  shortTitle: (if .shortTitle then (.shortTitle | join("; ")) else null end),
}]'
cat data/zdb-ger-law-issn-all.json | jq -cs '.' | jq -r "${JQ_CMD}" > data/zdb-ger-law-issn.json

# convert JSON array into CSV
JQ_JSON_TO_CSV='(map(keys) | add | unique) as $cols | map(. as $row | $cols | map($row[.])) as $rows | $cols, $rows[] | @csv'
cat data/zdb-ger-law-issn.json | jq -r "${JQ_JSON_TO_CSV}" > data/zdb-ger-law-issn.csv

