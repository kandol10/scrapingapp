import requests

url = 'https://scraping-app123.herokuapp.com/process'
data = {'task_description': 'Your task description here'}

response = requests.post(url, json=data)
print(response.json())
