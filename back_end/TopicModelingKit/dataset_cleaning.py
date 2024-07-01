import pandas as pd

src_dataset_path = '/home/mchenyu/web-app/back_end/TopicModelingKit/etds_samples.csv'
out_dataset_path = '/home/mchenyu/web-app/back_end/TopicModelingKit/etds_samples_processed.csv'


def standardize_data(data):
    # map university names
    # data['university'] = data['university'].replace(['Geomrgia Institute of Technology',
    #                                                  'Georgia Institute of \r\n\r\n Technology',
    #                                                  'Georgia Institute of \r\n \r\nTechnology'],
    #                                                 'Georgia Institute of Technology')
    # data['university'] = data['university'].replace(['North Texas State [University]',
    #                                                  'North Texas [State] University',
    #                                                  'North Texas State Univeristy',
    #                                                  'North Texas Sate University',
    #                                                  'North Texas state University',
    #                                                  'North Texas.State University',
    #                                                  'North Texas State'],
    #                                                 'North Texas State University')
    # data['university'] = data['university'].replace(['Virginia Polytechnic Institute',
    #                                                  'Virginia Polytechnic Institute and State Univesity'],
    #                                                 'Virginia Polytechnic Institute and State University')
    # data['university'] = data['university'].replace(["North Texas State Teacher's College"],
    #                                                 'North Texas State Teachers College')
    # replace new lines and tabs
    data = data.fillna('None')
    data['title'] = data['title'].str.replace('\n|\t|\r|"|\'', ' ')
    data['abstract'] = data['abstract'].str.replace('\n|\t|\r|"|\'', ' ')
    return data


data = pd.read_csv(src_dataset_path)
data = standardize_data(data)
data.to_csv(out_dataset_path, index=False)

