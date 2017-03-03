import json

import copy
import datetime
import logging
import requests
import string

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class PiConsole:
    def __init__(self, name="Pi Console"):
        self.name = name
        self.filename = "log.txt"

    def configure(self, **kwargs):
        if kwargs != None:
            for key, value in kwargs.iteritems():
                if key == "filename":
                    self.filename = value

    def printf(self, text, end="", name=None):
        if name == None:
            name = self.name
        logger.info("[{name}] ".format(name=name) + text + end)

    def log(self, text, end="", name=None):
        time = datetime.datetime.now().isoformat()
        if name == None:
            name = self.name
        name = "LOG "+time+" "+name
        logger.debug("[{name}] ".format(name=name) + text + end)

    def logerror(self, text, end=""):
        time = datetime.datetime.now().isoformat()
        if name == None:
            name = self.name
        name = "ERROR "+time+" "+name
        logger.error("[{name}] ".format(name=name) + text + end)

    def filelog(self, text, end=""):
        try:
            with open(self.filename, 'rb') as f_in:
                f_cont = str(f_in.read())
        except:
            f_cont = ""
        f_cont += text + end
        with open(self.filename, 'w') as f_out:
            f_out.write(f_cont)

# console for logging based on a name.
console = PiConsole("SEML Logic")

class SEML:
    def __init__(self):
        self.api_key = "None"

    def change_api_key(self, api_key):
        self.api_key = "Token " + api_key

    def get_page(self, url, news_type="FIND"):
        '''
        Getting a page from an actual URL. This saves as a file called 'sites.json'. Format is supposed to be "human readable"...
        '''
        console.log("Trying to gather page {url}...".format(url=url))
        res = [str(self.send_request(url))] # response of the page content.
        console.log("DONE! Accessing Monkey Learn API...")
        response = self.monkey_learn(res) # accessing the Monkey Learn API to find words.
        console.log("DONE! Saving data do file...")
        norm = self.normalize_words([response]) # save the data to a file with a "human-readable" format.
        s = self.save({"url": url, "headers": norm["headers"], "paragraphs": norm["paragraphs"]}, news_type)
        console.log("DONE!")
        return s # this is used for the calculations function, so the program can get the data from Monkey Learn.api-key

    def monkey_learn(self, text):
        '''
        Access the Monkey Learn API. Argument 'text' should be an HTML content.
        '''
        mlurl = "https://api.monkeylearn.com/v2/extractors/ex_RK5ApHnN/extract/" # the Monkey Learn API URL.
        DATA = {"text_list": text} # data to send to Monkey Learn API.
        HEADERS = {"Authorization": self.api_key, "Content-Type": "application/json"} # headers for authorization.
        res = requests.post(mlurl, data=json.dumps(DATA), headers=HEADERS) # send the actual request.
        try:
            return json.loads(res.text)["result"][0] # try to load the data and return it, otherwise...
        except:
            console.logerror("Error in Monkey Learn API access.") # log the error.
            console.log("Request got: {res}".format(res=res.text)) # tell what the request got/returned.
            return False # return the function with a "False".

    def send_request(self, url):
        '''
        Send a request for a page URL, this is used to get a pages actual HTML content.
        '''
        try:
            response = requests.get(url=url, headers={})
            console.log('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            return response.content
        except requests.exceptions.RequestException:
            console.logerror('HTTP Request failed')
            return False

    def normalize_words(self, array):
        '''
        Normalize the values returned by the Monkey Learn API to a "human readable" json format.
        '''
        headers = [] # the headers list, used for 'mtext'
        paragraphs = [] # the paragraphs list, used for 'otext'
        for doc in array: # for each document in monkey learn return list.
            for par in doc: # for each paragraph/header in the document.
                par["paragraph_text_new"] = ""
                skip_next = 0
                for c in range(len(par["paragraph_text"])): # for each character in the paragraph/header.
                    if skip_next != 0: # skiping over characters already recorded.
                        skip_next -= 1
                        continue
                    # this next part is for \xXX escape codes.
                    if par["paragraph_text"][c] == "\\" and par["paragraph_text"][c+1] == "x":
                        pp = par["paragraph_text"][c+2:c+4]
                        par["paragraph_text_new"] += chr(int(pp, 16))
                        skip_next = 6
                    elif par["paragraph_text"][c] == "\\": # for back slashes.
                        skip_next = 1
                    else: # any other character.
                        par["paragraph_text_new"] += par["paragraph_text"][c]
                if par["paragraph_text_new"] == "": # after normalizing the paragraph, check to see if it's empty.
                    continue
                if par["is_header"]: # if the paragraph is a "header" then add it to 'mtext'.
                    headers.append(par["paragraph_text_new"].strip())
                else: # otherwise the paragraph is "paragraph" and add it to 'otext'.
                    paragraphs.append(par["paragraph_text_new"].strip())
        return {"headers": headers, "paragraphs": paragraphs} # return the normalized paragraphs.

    def save(self, data, news_type):
        '''
        Save the found data to a "human readable" json file.
        '''
        try: # try to open an already made 'sites.json' file, otherwise...
            with open("sites.json", 'rb') as f_in:
                f_cont = json.load(f_in)
        except: # create a new 'sites.json' file.
            console.logerror("File 'sites.json' doesn't exist.")
#            with open("sites.json", 'w') as f_in:
#                f_cont = {"urls": []} # default data of a single key.
        if data["url"] in f_cont["urls"]: # if the URL of found data is already in the json file, we modify only the header and paragraph.
            f_cont[data["url"]]["mtext"] = data["headers"]
            f_cont[data["url"]]["otext"] = data["paragraphs"]
        else: # otherwise, create a new dictionary of the data.
            f_cont[data["url"]] = {
                "url": data["url"], # set URL.
                "mtext": data["headers"], # set headers.
                "otext": data["paragraphs"], # set paragraphs.
                "whois": { # set default WHOIS. this will be changed later after automatic whois is implemented.
                    "email": "FIND",
                    "address": [
                        "FIND",
                        "FIND",
                        "FIND",
                        "FIND"
                    ],
                    "phone": "FIND"
                },
                "type": news_type # and set the news type. usually FIND, unless training data.
            }
            f_cont["urls"].append(data["url"]) # append the data to the file contents.
#        with open("sites.json", 'w') as f_out: # and finally save the file.
#            json.dump(f_cont, f_out)
        return f_cont # return the file content for the calculation function.

    def calculate(self, api_key, url, filename, file2=None):
        '''
        Calculate the probability of a web article being Fake or Real based on the content of that page compared to other data gathered about Fake and Real news articles.
        '''
        # open a file of pre-calculated sites if not None.
#        if file2 != None:
#            try:
#                with open(file2, 'r') as f_in:
#                    sites = json.load(f_in)
#            except:
#                with open(file2, 'w') as f_out:
#                    sites = {}
            # if the url is alread been calculated, there is no need to re-calculated.
#            if url in sites:
#                return sites[url] # just return, and be done.
        news_type = "FIND" # set default news type.
        with open(filename, 'rb') as f_in:
            f_cont = json.load(f_in)
        self.change_api_key(api_key) # change the API key, to input from user.
        page = self.get_page(url) # gather the page.
        for type in ["Real", "Fake"]: # for each type of news.
            for t in ["mtext", "otext"]: # for each 'mtext' and 'otext' in each type of news.
                for word in f_cont[type][t]: # for each word in section.
                    # re-calculated the probibilities to a decimal using total count and total articles.
                    f_cont[type][t][word] = f_cont[type][t][word] / float(f_cont["totals"][type])
        # set basic probibilities of each news type.
        fake_prob = 1.0
        real_prob = 1.0
        for t in ["mtext", "otext"]: # for each of 'mtext' and 'otext'.
            seen = [] # the already seen words, so we don't add on extra probibility.
            for word in ' '.join(page[url][t]).split(): # for each word, in each section.
                if word in seen: # if the word has been seen, just continue in the loop.
                    continue
                else: # otherwise, add it to list of words seen, and continue calculation.
                    seen.append(word)
# -----> Can uncomment/comment the next line of code for file logging. WARNING: May use too much memory.
#                console.filelog("Word: {word}".format(word=word))
                if word in f_cont["Real"][t]: # if the word is in the pre-calculated probibilities for real news, add it to the probibility of real news.
                    real_prob = real_prob * f_cont["Real"][t][word]
# -----> Can uncomment/comment the next line of code for file logging. WARNING: May use too much memory.
#                    console.filelog("Found {word} in real news. Added {prob} to probibility.".format(word=word, prob=f_cont["Real"][t][word]))
                if word in f_cont["Fake"][t]: # if the word is in the pre-calculated probibilities for fake news, add it to the probibility of fake news.
                    fake_prob = fake_prob * f_cont["Fake"][t][word]
# -----> Can uncomment/comment the next line of code for file logging. WARNING: May use too much memory.
#                    console.filelog("Found {word} in fake news. Added {prob} to probibility.".format(word=word, prob=f_cont["Fake"][t][word]))
        # log the probibilities of each news article to the console.
        console.log("Probibility of being real news: {prob}".format(prob=real_prob))
        console.log("Probibility of being fake news: {prob}".format(prob=fake_prob))
        if fake_prob >= real_prob: # if the probibility of being fake is greater than the probibility of being real, it's considered fake new.
            news_type = "Fake"
        else: # otherwise it's real news, not fake news.
            news_type = "Real"
        # add the url to calculated urls if a file inputed.
#        if file2 != None:
#            sites[url] = news_type
#            with open(file2, 'w') as f_out:
#                json.dump(sites, f_out)
        return (news_type, real_prob, fake_prob) # return the news type, and be finished.

def analyze(event, context):
    try:
        url = event["queryStringParameters"]["url"]
    except:
        result = {
            "news-type": "error",
            "error": "No URL inputed."
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        return response
    logging.debug("URL: "+url)
    logging.debug("Analyze: "+json.dumps(event))
    seml_inst = SEML()
    logging.debug("Initilized SEML.")
    news_type = seml_inst.calculate("<API KEY>", url, "out.json")
    logging.debug("Completed calculation. Result: "+news_type[0])
    result = {
        "news_type": news_type[0],
        "real_probibility": news_type[1],
        "fake_probibility": news_type[2]
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(result)
    }
    return response

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
