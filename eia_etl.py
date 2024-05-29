import pandas as pd
import datetime
import eia_api

def load_log(path):
    class log_obj:
        def __init__(output, log, last_success, end, start):
            output.log = log
            output.last_success = last_success
            output.end = end
            output.start = start

    log_file = pd.read_csv(path)
    cols_time = log_file.columns[3:8]
    log_file[cols_time] = log_file[cols_time].apply(pd.to_datetime)

    # Identify the last successful update
    meta_success = log_file[log_file["success"] == True] 
    meta_success = meta_success[meta_success["index"] == meta_success["index"].max()]
    end = meta_success["end_act"]
    start = end + datetime.timedelta(hours = 1)
    start = datetime.datetime.strptime(str(start.iloc[0]), "%Y-%m-%d %H:%M:%S")
    
    log = log_obj(log = log_file, 
                  last_success = meta_success, 
                  end = end,
                  start = start)

    return log


def get_api_end(api_key, api_path, offset):
    
    class api_meta:
        def __init__(output, metadata, end, end_fix):
            output.metadata = metadata
            output.end = end
            output.end_fix = end_fix
    
    metadata = eia_api.eia_metadata(api_key = api_key, 
                                    api_path = api_path)
    end_api = datetime.datetime.strptime(metadata.meta["endPeriod"], "%Y-%m-%dT%H")
    end_fix = end_api -  datetime.timedelta(hours = offset)

    meta = api_meta(metadata = metadata,
                    end = end_api,
                    end_fix = end_fix)
    
    return meta
    

def eia_data_refresh(start, end, api_key, api_path, facets, offset = None, verbose = True):
    
    class data_refresh:
        def __init__(output, data, status, log):
            output.data = data
            output.status = status
            output.log = log
    
    df = None
    comments = ""


    if(start < end):
        if verbose:
            print("Updates are available")
        if offset is not None:
            s = start -  datetime.timedelta(hours = offset)
            o = offset
            comments = comments + "Offset the start argument by" + str(offset) + "; "
        else:
            s = start
            o = 0
        
        df = eia_api.eia_get(api_key = api_key, 
                             api_path = api_path, 
                             facets = facets, 
                             start = s,
                             end = end) 
        if df is not None and len(df.data) > 0:
            start_match_flag = df.data["period"].min() == s
            end_match_flag = df.data["period"].max() == end
            start_act = df.data["period"].min()
            end_act = df.data["period"].max()
            end_flag = start_act < end_act
            n_obs = len(df.data)
            na = df.data["value"].isna().sum()
            if start_match_flag and end_flag and na == 0 and n_obs > 0:
                if verbose:
                    print("Refresh successed")
                success_flag = True
                if end_match_flag:
                    comments = comments + "The end argument does not match the last data point timestamp; "
            else:
                success_flag = False
                if verbose:
                    print("Refresh failed")
                comments = comments + "The refresh process failed, please check the log's flags; "

        else:
            if verbose:
                print("Refresh failed")
            success_flag = False
            start_match_flag = None
            end_match_flag = None
            start_act = None
            end_act = None
            n_obs = None
            na = None
            comments = comments + "The refresh process failed, something went wrong with the data request; "
    else:
        if verbose:
            print("No updates are available...")
        success_flag = False
        start_match_flag = None
        end_match_flag = None
        start_act = None
        end_act = None
        n_obs = None
        na = None
        comments = comments + "No new data is available; "
    
    log = {
        "index": None,
        "respondent": "US48",
        "respondent_type": "Demand",
        "time": datetime.datetime.now(),
        "start": start,
        "end": end,
        "offset": offset,
        "start_act": start_act,
        "end_act": end_act,
        "start_match": start_match_flag, 
        "end_match": end_match_flag, 
        "n_obs": n_obs,
        "na": na,
        "type": "refresh",
        "update": None,
        "success": success_flag,
        "comments": comments
        }
    
    if success_flag:
        data = df.data
    else:
        data = None
    
    output = data_refresh(data = data, status = success_flag, log = log)

    return output





def append_new_data(data_path,log_path, new_data, save = False, verbose = True):
    
    class appended_data:
        def __init__(output, data, data_update, log):
            output.data = data
            output.data_update = data_update
            output.log = log

    log = load_log(path = log_path)
    new_data.log["index"] = log.log["index"].max() + 1
    new_data.log["update"] = False
    

    if new_data.status:
        if verbose:
            print("Appending the new data to the series")
            print("Adding " + str(len(new_data.data)) + " new rows")
        pre_data = pd.read_csv(data_path)
        pre_data["period"] = pd.to_datetime(pre_data["period"])
        pre_data["value"] = pd.to_numeric(pre_data["value"])
        if new_data.log["offset"] > 0 and pre_data["period"].max() > new_data.log["start_act"]:
            pre_data = pre_data[pre_data["period"] < new_data.log["start_act"]]
            
        data = pre_data._append(new_data.data)
        data = data.sort_values("period")

        new_data.log["update"] = True
        log_file_new = pd.DataFrame([new_data.log])
        new_log = log.log._append(log_file_new)

        if save:
            if verbose:
                print("Save the data into CSV file")
            data.to_csv(data_path, index = False)
            if verbose:
                print("Save the metadata into CSV file")
            new_log.to_csv(log_path, index = False)
    else:
        if verbose:
            print("No new data is available or the data refresh failed, please check the log file")

        data = pd.read_csv(data_path)
        data["period"] = pd.to_datetime(data["period"])
        data["value"] = pd.to_numeric(data["value"])

        log_file_new = pd.DataFrame([new_data.log])
        new_log = log.log._append(log_file_new)
        if save:
            if verbose:
                print("Save the metadata into CSV file")
            new_log.to_csv(log_path, index = False)

    output = appended_data(data = data, data_update = new_data.log["update"], log = new_log)

    return output


def check_updates(start, end, verbose = True):
    if start < end and verbose:
        print("Updates are available")
        return True
    else:
        return False
    
