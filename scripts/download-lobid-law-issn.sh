# construct URL
LOBID_ENDPOINT="http://lobid.org/resources/search"
P_Q='inCollection.id:"http://lobid.org/resources/HT014846970#!" AND _exists_:issn AND language.label:deutsch'
P_NESTED='subject:subject.notation:340 AND subject.source.id:"https://d-nb.info/gnd/4149423-4"'
LOBID_URL="${LOBID_ENDPOINT}?q=$(jq -nr --arg str "${P_Q}" '$str|@uri')&nested=$(jq -nr --arg str "${P_NESTED}" '$str|@uri')"

# execute http request if file hasn't been already downloaded
[ -f data/zdb-ger-law-issn-all.json ] || curl -H "Accept: application/x-jsonlines" $LOBID_URL > data/zdb-ger-law-issn-all.json
