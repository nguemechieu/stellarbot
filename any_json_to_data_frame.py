import pandas as pd
import numpy as np
class Any_json_to_data_frame:

    def __init__(self) :
        
        ''' Initialize the class '''

    ''' Convert the json data to a data frame '''

    def convert_json_to_data_frame(self, json_data) :
        

        data_df = pd.DataFrame()
        ii= 0
        keys = []
        values = []
        for key in json_data :
            ii+= 0
            if key is  isinstance( json_data, list ):
                print("Data type :list")
                for key2 in json_data[key] :
                    if key2 is isinstance( json_data[key][key2] , list ):
                     print("Data type :list")
                     for key3 in json_data[key][key2] :
                         values.append(json_data[key][key2][key3])
                         keys.append(key)
                         data_df[key] = json_data[key]
                         print(keys, values)
                    else:
                     values.append(json_data[key][key2])
                     keys.append(key)
                     data_df[key] = json_data[key]
                     print(keys, values)
               
            elif type(key)== str and key is  isinstance( json_data[key], dict ) :
                 print("Data type :dict")
                 
                 for key2 in json_data[key] :
                     
                     if type( json_data[key][key2] ) == list :
                         print("Data type :list")
                         for key3 in json_data[key][key2] :
                             values.append(json_data[key][key2][key3])
                             keys.append(key)
                             data_df[key] = json_data[key]
                             print(keys, values)
                     elif key2 is  isinstance( json_data[key][key2] , dict ):
                         print("Data type :dict")
                         for key3 in json_data[key][key2] :
                             values.append(json_data[key][key2][key3])
                             keys.append(key)
                             data_df[key] = json_data[key]
                             print(keys, values)

                     else:
                      values.append(json_data[key][key2])
                      keys.append(key)
                      data_df[key] = json_data[key]
                 print(keys, values)
            elif    type(key)== int and key is  isinstance( key, dict ) :

                 print("Data type :dict")
                 for i in range(0,len(json_data[key])) :
                     
                     if type( json_data[key][i] ) == list :
                         print("Data type :list")
                         for key3 in json_data[key][i] :
                             values.append(json_data[key][i][key3])
                             keys.append(key)
                             data_df[key] = json_data[key]
                             print(keys, values)
                     elif i is  isinstance( json_data[key][i], dict ):
                         print("Data type :dict")
                         for key3 in json_data[key][i] :
                             values.append(json_data[key][i][key3])
                             keys.append(key)
                             data_df[key] = json_data[key]
                             print(keys, values)
                     elif i is  isinstance( json_data[key][i], str ):
                         print("Data type :str")
                         values.append(json_data[key][i])
                         keys.append(key)
                         data_df[key] = json_data[key]
                         print(keys, values)
      
                 
            elif key is  isinstance( json_data, dict) :
                 for i in range(0,len(json_data[key])) :
                    if type(  json_data[key][i] ) == list :
                         print("Data type :list")
                         for key3 in json_data[key][i] :
                             values.append(json_data[key][i][key3])
                             keys.append(key)
                             data_df[key] = json_data[key]
                             print(keys, values)
                    elif i is  isinstance( json_data[key][i], dict ):
                         print("Data type :dict")
                         for key3 in json_data[key][i] :
                             values.append(json_data[key][i][key3])
                             keys.append(key)
                             data_df[key] = json_data[key]
                             print(keys, values)
                    elif i is  isinstance( json_data[key][i], str ):

                         values.append(json_data[key][i])
                         keys.append(key)
                         data_df[key] = json_data[key]
                         print(keys, values)
                
            elif type(  key) == int  and key is  isinstance( json_data, str ) :
                 print("Data type :int")
                 values.append(json_data[key])
                 keys.append(key)
                 data_df[key] = json_data[key]
                 print(keys, values)
                 
            elif type(  key ) == float :
                print("Data type :float")
                values.append(json_data[key])
                keys.append(key)
                data_df[key] = json_data[key]
            elif type(  key) == bool :
                print("Data type :bool")
                values.append(json_data[key])
                keys.append(key)
                data_df[key] = json_data[key]
                print(keys, values)
                
            elif type(  key ) == None :
                values.append(json_data[key])
                keys.append(key)
                data_df[key] = json_data[key]
                print(keys, values)
                

            elif type(  key ) == np.ndarray :
                print('Data type :ndarray')
                for i in range(0,len(json_data[key])) :
                    values.append(json_data[key][i])
                    keys.append(key)
                    data_df[key] = json_data[key]
                
            elif type(  key) == pd.DataFrame :
                print('Data type :dataframe')

                for i in range(0,len(json_data[key].columns)) :
                    values.append(json_data[key][i])
                    keys.append(key)
                    data_df[key] = json_data[key]
                
            elif type(  key ) == pd.Series :
                print('Data type :series')
                for i in range(0,len(json_data[key])) :
                    values.append(json_data[key][i])
                    keys.append(key)
                    data_df[key] = json_data[key]
            
            else :
                print('Data type :unknown')
                print(keys, values)
            return data_df