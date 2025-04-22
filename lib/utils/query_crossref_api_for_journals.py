from crossref.restful import Journals

def check_issn(issn):
    journals = Journals()
    result = journals.journal(issn)

    if result:
        return True
    else:
        return False


# Beispiel-Verwendung
issn_to_check = "0102-311X"
if check_issn(issn_to_check):
    print(f"Die ISSN {issn_to_check} ist in Crossref enthalten.")
else:
    print(f"Die ISSN {issn_to_check} ist nicht in Crossref enthalten.")