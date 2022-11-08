import json,argparse,os
import glob

"""
--folder where the unfiltered json files are stored

--outFile is the SINGLE json file where results will be stored. different behaviour if it is .json or jsonl
--direcotry if wished to be stored in multiple json files and not one 
  sorry for the ugliness
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script will process the extracted json files, filter out unnecesary data and produce a single json file with multiple json objects, one for each pubmedid')
    parser.add_argument("-f", "--folder", nargs=1, required=True, help="Folder where json files are located", metavar="PATH")
    parser.add_argument("-o", "--outFile", nargs=1, required=False, help="Json File with filtered json data", metavar="PATH")
    parser.add_argument("-d", "--directory", nargs=1, required=False, help="If isngle json file fails try saving in to multiple json files(one for each article)", metavar="PATH")
    args = parser.parse_args()
    json_dict = {}

    if args.outFile:
        if "jsonl" in args.outFile[0]:
            for file in glob.glob(args.folder[0]+"*.jsonl"):
                pubmed_id = os.path.splitext(os.path.basename(file))[0]
                with open(file) as json_file:
                    data = json.load(json_file)
                    new_dict = {}
                    desired_data = ["METHODS","ACK_FUND","KEYWORDS"]
                    for field in desired_data:
                        new_dict[field] = data[field]
                    new_dict["PID"] = pubmed_id
                with open(args.outFile[0],'a') as out_file:
                    json.dump(new_dict,out_file)
                    out_file.write('\n')
                    out_file.close()
        else :
            for file in glob.glob(args.folder[0]+"*.jsonl"):
                    pubmed_id = os.path.splitext(os.path.basename(file))[0]
                    with open(file) as json_file:
                        data = json.load(json_file)
                        new_dict = {}
                        # switch to input argument if wanted
                        desired_data = ["METHODS","ACK_FUND","KEYWORDS"]
                        for field in desired_data:
                            new_dict[field] = data[field]
                        json_dict[pubmed_id] = new_dict
            with open(args.outFile[0],'a') as out_file:
                json.dump(json_dict,out_file)
                out_file.close()
    elif args.directory:
        for file in glob.glob(args.folder[0]+"*.jsonl"):
            pubmed_id = os.path.splitext(os.path.basename(file))[0]
            with open(file) as json_file:
                data = json.load(json_file)
                new_dict = {}
                # switch to input argument if wanted
                desired_data = ["METHODS","ACK_FUND","KEYWORDS"]
                for field in desired_data:
                    new_dict[field] = data[field]
                new_dict["PID"] = pubmed_id
            with open(args.directory[0]+pubmed_id+".jsonl",'a') as out_file:
                json.dump(new_dict,out_file)
                out_file.close()



