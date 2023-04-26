from requests import get, post, delete

print(delete('http://localhost:8080/api/game/1').json())