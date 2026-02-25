# Test the run_bracket POST method in the flask app.
import requests
import json


#print(requests.get('http://localhost:5000/model/pnw_all_qm/predict/frc2910,frc2910/frc1983,frc1983').json())

alliances = { f'A{i}': [''] for i in range(1,9) }
alliances['A1'] = ['frc2910','','']
alliances['A2'] = ['frc1983','','']
headers = {'Content-Type': 'application/json'}
host = 'http://localhost:5000'
result = requests.post(f'{host}/model/pnw_all_qm/bracket', json=alliances, timeout=20000) #, headers=headers)
print(result.json())    