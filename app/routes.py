from flask import Blueprint, render_template, request, flash
from app.models import FastestLap, RaceWinner
from app.scraper import scrape_fastest_laps, scrape_race_winners
from collections import Counter, defaultdict
from datetime import datetime
from sqlalchemy import func
from app import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    current_year = datetime.now().year
    seasons = range(2000, current_year + 1)
    selected_season = None
    laps = []
    chart_data = {}
    
    if request.method == 'POST':
        try:
            selected_season = int(request.form.get('season'))
            if not FastestLap.query.filter_by(season=selected_season).first():
                scrape_fastest_laps(selected_season)
            
            laps = FastestLap.query.filter_by(season=selected_season).all()
            
            if not laps:
                flash(f"No race data available for season {selected_season}", "warning")
            else:
                # Prepare chart data for both drivers and teams
                driver_counts = Counter(lap.driver for lap in laps)
                team_counts = Counter(lap.team for lap in laps)
                
                chart_data = {
                    'drivers': {
                        'labels': list(driver_counts.keys()),
                        'data': list(driver_counts.values())
                    },
                    'teams': {
                        'labels': list(team_counts.keys()),
                        'data': list(team_counts.values())
                    }
                }
            
        except Exception as e:
            flash(f"Error fetching data: {str(e)}", "error")
    
    return render_template('index.html', 
                         seasons=seasons, 
                         selected_season=selected_season, 
                         laps=laps,
                         chart_data=chart_data) 

@main.route('/team-stats')
def team_stats():
    try:
        # Get all seasons from the database
        seasons = db.session.query(RaceWinner.season).distinct().order_by(RaceWinner.season).all()
        seasons = [season[0] for season in seasons]
        
        if not seasons:
            # If no data exists, scrape some initial seasons
            for year in range(2000, 2024):
                scrape_race_winners(year)
            seasons = range(2000, 2024)
        
        # Query wins per team per season
        wins_by_team = db.session.query(
            RaceWinner.season,
            RaceWinner.team,
            func.count(RaceWinner.id).label('wins')
        ).group_by(RaceWinner.season, RaceWinner.team).all()
        
        # Organize data for the chart
        teams_data = defaultdict(lambda: defaultdict(int))
        all_teams = set()
        
        for season, team, wins in wins_by_team:
            teams_data[team][season] = wins
            all_teams.add(team)
        
        # Prepare the chart data
        chart_data = {
            'labels': sorted(seasons),
            'datasets': [
                {
                    'label': team,
                    'data': [teams_data[team][season] for season in sorted(seasons)]
                } for team in sorted(all_teams)
            ]
        }
        
        return render_template('team_stats.html', 
                             chart_data=chart_data,
                             teams=sorted(all_teams))
                             
    except Exception as e:
        flash(f"Error loading team statistics: {str(e)}", "error")
        return render_template('team_stats.html', chart_data=None, teams=None) 