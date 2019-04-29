import os
import json

def get_data(table):
    table_data = None
    with open(table) as f:
        table_data = json.load(f)

    return table_data

def get_sensor_data(data):
    sdata = None
    #print(data)
    with open(data) as f:
        last = None

        for line in f:
            last = line
        sdata = json.loads(line)

    return sdata



if __name__ == "__main__":
    files = os.listdir(".")
    #print(files)
    dict_rv = {}
    for file in files:
        if file[-4:] == "info":
            tdata = get_data(file)
            sdata = get_sensor_data(file[:-5]+".data")
            #print("Table: ", tdata)
            #print("Data: ", sdata)
            table_list = [None for _ in range(8)]
            for i in range(8):
                if tdata['body']['sensors'][i] is None:
                    continue
                table_list[i] = {'name':tdata['body']['sensors'][i],
                                'value':sdata['body']['sdata'][i]}

            dict_rv[tdata['body']['name']] = table_list
    print(json.dumps(dict_rv))
