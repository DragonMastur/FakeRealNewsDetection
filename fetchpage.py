#from monkeylearn import MonkeyLearn
from ast import literal_eval
import json
import sys
import requests

help_msg = """
Fetch Page Usage:
    Api Key - the api key for monkeylearn.
    Url - the url for a page.
    News Type* - the type of news, Fake or Real.
    *optional
"""

if len(sys.argv) < 2:
    print(help_msg)
    quit(0)

api_key = "Token " + sys.argv[1]
url = sys.argv[2]
try:
    news_type = sys.argv[3]
except:
    news_type = "FIND"

def monkey_learn(text):
    global ml
    global api_key
#    ml = MonkeyLearn(api_key)
    mlurl = "https://api.monkeylearn.com/v2/extractors/ex_RK5ApHnN/extract/"
    DATA = {"text_list": text}
    HEADERS = {"Authorization": api_key, "Content-Type": "application/json"}
    res = requests.post(mlurl, data=json.dumps(DATA), headers=HEADERS)
#    res = ml.extractors.extract(module_id, text)
    try:
        return json.loads(res.text)["result"][0]
    except:
        print("Error in Monkey Learn API access.")
        print("Request got: {res}".format(res=res.text))
        return False

def send_request():
    global url
    try:
        response = requests.get(url=url, headers={})
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        return response.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        return False

def normalize_words(array):
    headers = []
    paragraphs = []
    for doc in array:
        for par in doc:
            par["paragraph_text_new"] = ""
            skip_next = 0
            for c in range(len(par["paragraph_text"])):
                if skip_next != 0:
                    skip_next -= 1
                    continue
                if par["paragraph_text"][c] == "\\" and par["paragraph_text"][c+1] == "x":
                    pp = par["paragraph_text"][c+2:c+4]
                    par["paragraph_text_new"] += chr(int(pp, 16))
                    skip_next = 6
                elif par["paragraph_text"][c] == "\\":
                    skip_next = 1
                else:
                    par["paragraph_text_new"] += par["paragraph_text"][c]
            if par["paragraph_text_new"] == "":
                continue
            if par["is_header"]:
                headers.append(par["paragraph_text_new"].strip())
            else:
                paragraphs.append(par["paragraph_text_new"].strip())
#    print("Headers: {head}".format(head=headers))
#    print("Paragraphs: {par}".format(par=paragraphs))
    return {"headers": headers, "paragraphs": paragraphs}

def save(data):
    with open("sites2.json", 'r') as f_in:
        f_cont = json.load(f_in)
    if data["url"] in f_cont["urls"]:
        f_cont[data["url"]]["mtext"] = data["headers"]
        f_cont[data["url"]]["otext"] = data["paragraphs"]
    else:
        f_cont[data["url"]] = {
            "url": data["url"],
            "mtext": data["headers"],
            "otext": data["paragraphs"],
            "whois": {
                "email": "FIND",
                "address": [
                    "FIND",
                    "FIND",
                    "FIND",
                    "FIND"
                ],
                "phone": "FIND"
            },
            "type": news_type
        }
        f_cont["urls"].append(data["url"])
    with open("sites2.json", 'w') as f_out:
        json.dump(f_cont, f_out)

print("Trying to gather page...")
res = [str(send_request())]
print("DONE!\nAccessing Monkey Learn API...")
response = monkey_learn(res)
print("DONE!\nSaving data do document...")
norm = normalize_words([response])
save({"url": url, "headers": norm["headers"], "paragraphs": norm["paragraphs"]})
print("DONE!")
