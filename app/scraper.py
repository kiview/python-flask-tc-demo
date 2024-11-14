import requests
from app.models import FastestLap, RaceWinner
from app import db
from datetime import datetime

def scrape_fastest_laps(season):
    current_year = datetime.now().year
    if season < 1950 or season > current_year:
        raise ValueError(f"Season must be between 1950 and {current_year}")

    base_url = f"http://ergast.com/api/f1/{season}/results/1.json"
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        
        races = data['MRData']['RaceTable']['Races']
        
        if not races:
            print(f"No race data found for season {season}")
            return
            
        for race in races:
            results = race['Results'][0]
            fastest_lap = FastestLap(
                season=season,
                race=race['raceName'],
                driver=f"{results['Driver']['givenName']} {results['Driver']['familyName']}",
                team=results['Constructor']['name'],
                lap_time=results.get('FastestLap', {}).get('Time', {}).get('time', 'N/A'),
                lap_number=results.get('FastestLap', {}).get('lap', 0)
            )
            
            db.session.add(fastest_lap)
        
        db.session.commit()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        raise
    except KeyError as e:
        print(f"Error parsing data for season {season}: {e}")
        raise

def scrape_race_winners(season):
    current_year = datetime.now().year
    if season < 1950 or season > current_year:
        raise ValueError(f"Season must be between 1950 and {current_year}")

    base_url = f"http://ergast.com/api/f1/{season}/results/1.json"
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        
        races = data['MRData']['RaceTable']['Races']
        
        if not races:
            print(f"No race data found for season {season}")
            return
            
        for race in races:
            result = race['Results'][0]
            winner = RaceWinner(
                season=season,
                race=race['raceName'],
                driver=f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                team=result['Constructor']['name']
            )
            
            db.session.add(winner)
        
        db.session.commit()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        raise
    except KeyError as e:
        print(f"Error parsing data for season {season}: {e}")
        raise