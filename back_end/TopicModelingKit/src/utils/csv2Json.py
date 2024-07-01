import csv
import json
 
def csv_to_json(csv_file_path, json_file_path):
    #create a dictionary
    
 
    #Step 2
    #open a csv file handler
    with open(csv_file_path, encoding = 'utf-8') as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
 
        #convert each row into a dictionary
        #and add the converted data to the data_variable
        with open(json_file_path, 'a', encoding = 'utf-8') as json_file_handler:
            for rows in csv_reader:
                #assuming a column named 'No'
                #to be the primary key
                data_dict = {
                    "id": rows['id'],"text": rows['title'],
                    "parent_id": '',
                    "metadata": {
                        "author": rows['author'],
                        "advisor": rows['advisor'],
                        "year": rows['year'],
                        "university": rows['university'],
                        "degree": rows['degree'],
                        "URI": rows['URI'],
                        "department": rows['department'],
                        "discipline": rows['discipline'],
                        "language": rows['language'],
                    }
                }
                tempString = json.dumps(data_dict, indent = None)
                tempString.replace('\n','')
                json_file_handler.write(tempString)
                json_file_handler.write("\n")
 
    #open a json file handler and use json.dumps
    #method to dump the data
    #Step 3
    
        #Step 4
        
 
#driver code
#be careful while providing the path of the csv file
#provide the file path relative to your machine
 
#Step 1
csv_file_path = 'TopicModelingKit/etds_1000.csv'
json_file_path = 'TopicModelingKit/sample.json'
 
csv_to_json(csv_file_path, json_file_path)