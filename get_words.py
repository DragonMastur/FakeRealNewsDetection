# get_words.py

import string
import copy

class GetWords:
    def __init__(self):
        self.types = [];
        self.posts = [];

    def set_posts(self, posts):
        for type in posts:
            self.types.append(type)
            for post in posts[type]:
                post["type"] = type
                self.posts.append(post)

    def get_prob(self):
        probs = {}
        words = {};
        totals = {};
        for type in self.types:
            words[type] = {};
            totals[type] = 0;
        for post in self.posts:
            type = post["type"];
            for text in post["texts"]:
                for word in text.split():
                    if word.startswith('http://'):
                        continue
                    word = ''.join(ch for ch in word.lower() if ch not in set(string.punctuation));
                    if word in words[type]:
                        words[type][word] += 1;
                    else:
                        words[type][word] = 1;
                    totals[type] += 1;
        words2 = copy.deepcopy(words)
        for type in words2:
            for word in words2[type]:
                words2[type][word] = words[type][word] / float(totals[type])
        return [words, words2]

def main():
    import json;
    import sys;
    if len(sys.argv) < 2:
        print("Useage: python get_words.py [input.json] [output.json]")
        quit(0)
    app = GetWords();
    posts_file = sys.argv[1];
    posts = json.load(open(posts_file,'r'));
    app.set_posts(posts);
    prob = app.get_prob()
    with open(sys.argv[2]+"0.json",'w') as f_out:
        json.dump(prob[0], f_out)
    with open(sys.argv[2]+"1.json",'w') as f_out:
        json.dump(prob[1], f_out)

if __name__ == '__main__':
    main();
