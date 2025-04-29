#!/usr/bin/env python
# coding: utf-8

# In[4]:


import json
import pandas as pd
from pandas import json_normalize

# Load the JSON file
with open(r'G:\Data Analysis\GRP\response.json', 'r') as f:
    data = json.load(f)

# Use json_normalize to flatten nested dictionaries
df = json_normalize(data)

# Export to Excel
output_path = r'G:\Data Analysis\GRP\JSON_response_output.xlsx'
df.to_excel(output_path, index=False)

print(f"Excel file saved to: {output_path}")


# In[ ]:




