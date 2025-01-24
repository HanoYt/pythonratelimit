import requests

def convertir_temps(seconds):
    seconds = int(seconds)
    heures = seconds // 3600
    minutes = (seconds % 3600) // 60
    secondes = seconds % 60
    return heures, minutes, secondes

def verifier_limitation(url):
    response = requests.get(url)
    if response.status_code == 429:
        retry_after = response.headers.get('Retry-After')
        if retry_after is not None:
            return True, int(retry_after)
    return False, None

# URL de test pour vérifier les limitations de débit
url = "https://discord.com/api/v10/path/to/endpoint"

limite, retry_after = verifier_limitation(url)
if limite:
    heures, minutes, secondes = convertir_temps(retry_after)
    print(f"L'IP est rate par Discord. Réessayez après {heures} heures, {minutes} minutes et {secondes} secondes !")
else:
    print("L'IP n'est pas rate par Discord, gg all !")
