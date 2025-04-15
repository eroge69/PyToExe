import requests
import pandas as pd
#payload = {"Content": f"/md {"## :cop: Kind reminder\n**Pensez à vérifier vos DNR_investigation dans votre rapport supplémentaire. s'il vous plaît**"}"}
payload = {"Content":  "/md  ## :cop: Kind reminder\n**Pensez à vérifier vos DNR_investigation dans votre rapport supplémentaire, s'il vous plaît.**" }
df = pd.read_csv("chime_urls.csv",sep=";")

for url in df['urls']: 
    requests.post(url, json=payload)

#requests.post(str("https://hooks.chime.aws/incomingwebhooks/9108df35-b8c2-40c9-978d-18d6827e43ce?token=a2p3NXBlS1J8MXxyZ3pRQWw3YmRYUm0yVGFzcmZRZFdaUzlENzhPUldmX2ttZDJ3OHJSRUlv"), json=payload)