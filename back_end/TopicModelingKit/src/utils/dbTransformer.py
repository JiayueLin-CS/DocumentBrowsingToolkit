from configparser import ConfigParser
import json
import csv
configur = ConfigParser()

def dbTransform():
    db_path = configur.get('dataset','path')
    print ("Installation Library : ", db_path)
    print ("Installation Library : ", configur.get('dataset','field'))

    # Opening JSON file and loading the data
    # into the variable data
    with open(db_path) as json_file:
        data = json.load(json_file)
    
    employee_data = data['documents']
    
    # now we will open a file for writing
    data_file = open('metadata.csv', 'w')
    
    # create the csv writer object
    csv_writer = csv.writer(data_file)
    
    # Counter variable used for writing
    # headers to the CSV file
    count = 0
    
    for emp in employee_data:
        if count == 0:
            # Writing headers of CSV file
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
    
        # Writing data of CSV file
        csv_writer.writerow(emp.values())
    
    data_file.close()