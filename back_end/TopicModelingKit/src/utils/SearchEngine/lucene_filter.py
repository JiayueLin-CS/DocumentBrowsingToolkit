import os
import sys
import json

class LuceneFilter:
    def __init__(self, doc_ids: list):
        self.FILEPATH_R = os.path.join(os.path.dirname(__file__), "../../../sample.json")
        self.FILEPATH_W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formatted_sample_tmp.json")
        self.DOCUMENT_IDS = doc_ids
    

    def load_json(self):
        with open(self.FILEPATH_R, "r") as rf:
            lines = rf.readlines()
            
        md = dict()
        dl = []
        for line in lines:
            d = json.loads(line)
            dl.append(d)
            
        for i in dl:
            for k, v in i.items():
            
                md[k] = v
        return md
        
    def offload(self):
        d = json.dumps(self.load_json(), indent=4)
        with open(self.FILEPATH_W, "w") as wf:
            wf.write(d)

if __name__ == "__main__":
    lf = LuceneFilter([])
    lf.offload()