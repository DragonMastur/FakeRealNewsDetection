import copy
import datetime
import json
import PiConsole
import requests
import sys
import string

help_msg = """
Usage: python seml_logic.py [type] [*args]
Types:
- getpage   : get a pages content and put it in file. Use args [API Key], [URL], [News Type**]
- format    : format a file after geting page contents. Use args [Input File]
- prob      : find probibility of data after formating file. Use args [Input File] [Output File Name]
Args:
- API Key           : the api key for Monkey Learn's API
- URL               : the url of a web page, include the "http://" or "https://"
- News Type         : the type of news, can be "Real" or "Fake"
- Input File        : the file path for an input file
- Output File Name  : the name of an output file.

** optional argument.
"""

console = PiConsole.PiConsole("SEML Logic")

class SEML:
    def __init__(self):
        self.api_key = "None"
    def change_api_key(self, api_key):
        self.api_key = "Token " + api_key

    def get_page(self, url, news_type="FIND"):
        console.log("Trying to gather page {url}...".format(url=url))
        res = [str(self.send_request(url))]
        console.log("DONE!\nAccessing Monkey Learn API...")
        response = self.monkey_learn(res)
        console.log("DONE!\nSaving data do file...")
        norm = self.normalize_words([response])
        self.save({"url": url, "headers": norm["headers"], "paragraphs": norm["paragraphs"]}, news_type)
        console.log("DONE!")

    def monkey_learn(self, text):
        mlurl = "https://api.monkeylearn.com/v2/extractors/ex_RK5ApHnN/extract/"
        DATA = {"text_list": text}
        HEADERS = {"Authorization": self.api_key, "Content-Type": "application/json"}
        res = requests.post(mlurl, data=json.dumps(DATA), headers=HEADERS)
        try:
            return json.loads(res.text)["result"][0]
        except:
            console.logerror("Error in Monkey Learn API access.")
            console.log("Request got: {res}".format(res=res.text))
            return False

    def send_request(self, url):
        try:
            response = requests.get(url=url, headers={})
            console.log('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            return response.content
        except requests.exceptions.RequestException:
            console.logerror('HTTP Request failed')
            return False

    def normalize_words(self, array):
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
        return {"headers": headers, "paragraphs": paragraphs}

    def save(self, data, news_type):
        try:
            with open("sites.json", 'r') as f_in:
                f_cont = json.load(f_in)
        except:
            with open("sites.json", 'w') as f_in:
                f_cont = {"urls": []}
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
        with open("sites.json", 'w') as f_out:
            json.dump(f_cont, f_out)

    def format_file(self, filename):
        console.log("Getting file contents...")
        with open(filename, 'r') as f_in:
            f_cont = json.load(f_in)
        console.log("DONE! Formatting file...")
        output = {
            "Fake-headers": [],
            "Fake-paragraphs": [],
            "Fake-whois": [],
            "Real-headers": [],
            "Real-paragraphs": [],
            "Real-whois": []
        }
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
        console.log("DONE! Writing data to file 'formated_file.json'...")
        with open("formated_file.json", 'w') as f_out:
            json.dump(output, f_out)
        console.log("DONE!")

    def get_prob(self, filename, outname, infile=None):
        types = []
        docs = []
        probs = {}
        words = {}
        totals = {}
        if infile != None:
            with open(infile, 'r') as f_in:
                words = json.load(f_in)
            for type in words["Types"]:
                totals[type] = words["Types"][type]
            words.pop("Types")
        console.log("Getting file contents...")
        with open(filename, 'r') as f_in:
            f_cont = json.load(f_in)
        for type in f_cont:
            types.append(type)
            for doc in f_cont[type]:
                doc["type"] = type
                docs.append(doc)
        console.log("DONE! Calculating words...")
        if infile == None:
            for type in types:
                words[type] = {};
                totals[type] = 0;
        console.log("DONE! Calculating probiblities...")
        for doc in docs:
            type = doc["type"];
            for text in doc["texts"]:
                for word in text.split():
                    if word.startswith('http://'):
                        continue
                    word = ''.join(ch for ch in word.lower() if ch not in set(string.punctuation));
                    if word in words[type]:
                        words[type][word] += 1;
                    else:
                        words[type][word] = 1;
                    totals[type] += 1;
        console.log("DONE! Saving data to files '{fname}0.json' and '{fname}1.json'...".format(fname=outname))
        words2 = copy.deepcopy(words)
        for type in words2:
            for word in words2[type]:
                words2[type][word] = words[type][word] / float(totals[type])
        words["Types"] = {}
        for type in types:
            words["Types"][type] = totals[type]
        with open(outname+"0.json",'w') as f_out:
            json.dump(words, f_out)
        with open(outname+"1.json",'w') as f_out:
            json.dump(words2, f_out)
        console.log("DONE!")

def main():
    starttime = datetime.datetime.now()
    seml_inst = SEML()
    if len(sys.argv) < 2:
        print(help_msg)
        quit(0)
    stype = sys.argv[1]
    if stype.lower() == "getpage":
        if len(sys.argv) < 4:
            print(help_msg)
            quit(0)
        try:
            sa = sys.argv[4]
        except:
            sa = "FIND"
        seml_inst.change_api_key(sys.argv[2])
        seml_inst.get_page(sys.argv[3], sa)
    if stype.lower() == "format":
        if len(sys.argv) < 3:
            print(help_msg)
            quit(0)
        seml_inst.format_file(sys.argv[2])
    if stype.lower() == "prob":
        if len(sys.argv) < 4:
            print(help_msg)
            quit(0)
        try:
            sa = sys.argv[4]
        except:
            sa = None
        seml_inst.get_prob(sys.argv[2], sys.argv[3], sa)
    endtime = datetime.datetime.now()
    totaltime = (endtime-starttime).total_seconds()
    console.log("Took {seconds} seconds to run.".format(seconds=totaltime))

if __name__ == "__main__":
    main()
