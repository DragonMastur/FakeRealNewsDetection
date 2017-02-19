# format_file.py

import json
import sys

if len(sys.argv) < 2:
    print("Usage: python format_file.py [input_file]")
    quit(0)

fname = sys.argv[1]

def get_file():
    global fname
    with open(fname, 'r') as f_in:
        f_cont = json.load(f_in)
    return f_cont

def format_file():
    output = {
        "Fake-headers": [],
        "Fake-paragraphs": [],
        "Fake-whois": [],
        "Real-headers": [],
        "Real-paragraphs": [],
        "Real-whois": []
    }
    f_cont = get_file()
    for url in f_cont["urls"]:
        url = f_cont[url]
        output[url['type']+'-headers'].append({"texts": url["mtext"]})
        output[url['type']+'-paragraphs'].append({"texts": url["otext"]})
        whois_text = []
        whois_text.append(url["whois"]["email"])
        whois_text.append(' '.join(url["whois"]["address"]))
        whois_text.append(url["whois"]["phone"])
        whois_text = ' '.join(whois_text)
        output[url['type']+'-whois'].append({"texts": [whois_text]})
    print(whois_text)
    print(output)
    return output

formated_file = format_file()
with open("formated_file.json", 'w') as f_out:
    json.dump(formated_file, f_out)
