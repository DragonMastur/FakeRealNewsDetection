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

    def logerror(self, text, end="", name=None):
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

    def opose_type(self, type):
        if type == "Fake":
            return "Real"
        else:
            return "Fake"

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
            console.logerror("No sites.json file.")
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
        return f_cont # return the file content for the calculation function.

    def get_prob(self, filename, outfile, infile=None):
        '''
        Get the probability of words based on a site file, gathered by 'getpage' functions.
        '''
        # open a file for any previous outputs.
        if infile != None:
            console.log("Opening previous output...")
            with open(infile, 'rb') as f_in:
                words = json.load(f_in)
            console.log("DONE!")
        # if there is no previous output file, set the defaults.
        else:
            words = {"Real": {"mtext": {}, "otext": {}, "whois": {}}, "Fake": {"mtext": {}, "otext": {}, "whois": {}}, "totals": {"Real": 0, "Fake": 0}} # default dictionary.
            console.log("Set defaults.")
        console.log("Reading file of sites...")
        # read the sites file, contains all info gathered with a 'getpage' function.
        with open(filename, 'rb') as f_in:
            f_cont = json.load(f_in)
        console.log("DONE! Going through URLS...")
        # for each url in urls list.
        for url in f_cont["urls"]: # the list allows for more flexibility in the json file.
            type = f_cont[url]["type"] # gather the type of news.
            if type not in ["Fake", "Real"]:
                continue
            words["totals"][type] += 1 # add to the total number of articles run.
            for t in ["mtext", "otext"]: # for each 'mtext' and 'otext' section, whois is done later.
                seen = [] # list of already seen words.
                console.log("Reading '{type}' text for url, '{url}' and logging...".format(type=t, url=url))
                for word in ' '.join(f_cont[url][t]).split(): # for each word in the section of paragraphs/headers.
                    if word.lower() not in seen: # if the word has not yet been seen.
                        seen.append(word.lower()) # add it to the list of words seen.
                        if word.lower() not in words[type][t]: # if there's not a key, make one.
                            words[type][t][word.lower()] = 1
                            words[self.opose_type(type)][t][word.lower()] = 0
                        else: # if the key(word) exists, add 1 to it.
                            words[type][t][word.lower()] += 1
            console.log("Reading whois text and logging...")
            # now time for calculating whois text.
            whois_text = ""
            whois_text += f_cont[url]["whois"]["email"] + " " # add email to whois text.
            whois_text += ' '.join(f_cont[url]["whois"]["address"]) + " " # add adress to whois text, seperating each entry with a space.
            whois_text += f_cont[url]["whois"]["phone"] # add phone to whois text.
            seen = [] # the list of words seen, needs to be reset after each section.
            for word in whois_text.split(): # for each word in the whois.
                if word.lower() not in seen: # if word not seen yet,.
                    seen.append(word.lower()) # add to list of words seen.
                    if word.lower() not in words[type]["whois"]: # if key(word) doesn't exists create the key, set at 1.
                        words[type]["whois"][word.lower()] = 1
                    else: # if key(word) does exist add 1 to count.
                        words[type]["whois"][word.lower()] += 1
        console.log("Finished with URLS. Dumping output...")
        console.log("DONE!")

    def calculate(self, api_key, url, filename, file2=None, depth=50, margin=0.1):
        '''
        Calculate the probability of a web article being Fake or Real based on the content of that page compared to other data gathered about Fake and Real news articles.
        '''
        # open a file of pre-calculated sites if not None.
        if file2 != None:
            try:
                with open(file2, 'r') as f_in:
                    sites = json.load(f_in)
            except:
                console.logerror("No file with name: {name}, was found.".format(name=file2))
            # if the url is alread been calculated, there is no need to re-calculated.
            if url in sites:
                return sites[url] # just return, and be done.
        news_type = "FIND" # set default news type.
        with open(filename, 'rb') as f_in:
            f_cont = json.load(f_in)
        self.change_api_key(api_key) # change the API key, to input from user.
        page = self.get_page(url) # gather the page.
        '''
        for type in ["Real", "Fake"]: # for each type of news.
            for t in ["mtext", "otext"]: # for each 'mtext' and 'otext' in each type of news.
                for word in f_cont[type][t]: # for each word in section.
                    # re-calculated the probibilities to a decimal using total count and total articles.
                    try:
                        f_cont[type][t][word] = f_cont[type][t][word] / float(f_cont["Real"][t][word]+f_cont["Fake"][t][word])
                    except KeyError:
                        f_cont[type][t][word] = f_cont[type][t][word] / float(f_cont[type][t][word])
        '''
        # set basic probibilities of each news type.
        fake_prob = []
        real_prob = []
        for t in ["mtext", "otext"]: # for each of 'mtext' and 'otext'.
            seen = [] # the already seen words, so we don't add on extra probibility.
            for word in ' '.join(page[url][t]).split(): # for each word, in each section.
                if word in seen: # if the word has been seen, just continue in the loop.
                    continue
                else: # otherwise, add it to list of words seen, and continue calculation.
                    seen.append(word)
                # check to see if word exists in Fake or Real pre calcs.
                if word not in f_cont["Real"][t] and word not in f_cont["Fake"][t]:
                    continue # if neither contains word, then continue the loop.
                # pre-calculate the totals and words.
                fake_word = f_cont["Fake"][t][word]
                fake_total = f_cont["totals"]["Fake"]
                real_word = f_cont["Real"][t][word]
                real_total = f_cont["totals"]["Real"]
                all_total = f_cont["totals"]["Fake"] + f_cont["totals"]["Real"]
                # calculae likelyhoods and proirs.
                fake_likelyhood = fake_word / fake_total
                fake_proir = fake_total / all_total
                real_likelyhood = real_word / real_total
                real_proir = real_total / all_total
                marginal_likelyhood = fake_likelyhood * fake_proir + real_likelyhood * real_proir
                # calculate the signals of real and fake probability.
                signal = ( real_likelyhood * real_proir ) / marginal_likelyhood
                real_prob.append(signal)
                signal = ( fake_likelyhood * fake_proir ) / marginal_likelyhood
                fake_prob.append(signal)
        # now we calculate the probability of each news type.
        real_prob_list = sorted(real_prob, reverse=True)
        fake_prob_list = sorted(fake_prob, reverse=True)
        real_prob = 0.5
        fake_prob = 0.5
        for prob in real_prob_list[0:depth]:
            real_prob = real_prob * prob
        for prob in fake_prob_list[0:depth]:
            fake_prob = fake_prob * prob
        normalizer = real_prob + fake_prob # create the normalizer, and normalizer probabilities.
        real_prob = real_prob / normalizer
        fake_prob = fake_prob / normalizer
        if fake_prob > 0.5 + margin: # if the probability of being fake is greater than the margian of being fake news, defaulting to 60%.
            news_type = "Fake"
        elif real_prob > 0.5 + margin:
            news_type = "Real"
        else: # if the probability of fake or real news is between the margin, defaulting to 40%-60%.
            news_type = "Caution"
        # log the probibilities of each news article to the console.
        console.log("Probibility of being real news: {prob}".format(prob=real_prob))
        console.log("Probibility of being fake news: {prob}".format(prob=fake_prob))
        return news_type # return the news type, and be finished.


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
#    logging.debug("Analyze: "+json.dumps(event))
    seml_inst = SEML()
#    logging.debug("Initilized SEML.")
    news_type = seml_inst.calculate("<API KEY>", url, "out.json", 50, 0.2)
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
