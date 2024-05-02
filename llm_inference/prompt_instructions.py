import json


json_response = {
 “reason”: 'str',
 "total_sample_size":{ "int",
 		   "sample": "[int]",
           "sentence_where_found": "[str]",},
 "men": {"total": "int",
         "sample": "[int]",
         "sentence_where_found": "[str]",}.
 "women": {"total": "int",
           "sample": "[int]",
           "sentence_where_found": "[str]",}
}


json_string = json.dumps(json_response, indent=4)

prompt_instruction = f"""Find the total of men and women in that study. 
Your response should be in JSON only. If you need to output information about your process do it under the key: model_inference_info and don't output a Note at the end. 
If there are several sample that contains men or women, create a list of sample size for men and a list of sample size for women in addition to the total sample size per women and men and the total. 
Women can be sometimes refered to female. Men can be sometimes refers to males. 
In case there are percentages. output a field specifying it is percentages. 
If there is no mention of men or women (or related terms) please state that the value are 0, don't assume the representation. 
For the JSON verify it follow this structure: {json_string}"""

prompt_instruction = f"""data_source": "Text extracted from research article",
"processing_steps": [
"Identified key sections discussing men and women in the study",
"Extracted relevant numerical data on men and women",
"Validated the data against the context in the text",
"Calculated total sample size, men and women counts",
"Don't make assumption of the repartition if no direct mentions",
“If the answer is clear, stated in reason: `information clear`”,
“If it is not about human subject stated in reason: `no human subject`”,
“If the information is not clear stated in reason: `information not clear`”,
"Output the decision process  in json format following the format: {json_string}"""

