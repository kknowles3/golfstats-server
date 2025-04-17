# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 15:02:13 2025

@author: kknow
"""

if __name__ == "__main__":
    
    from devx.espn.golf_event_loader import GolfEventLoader
    
    event_id = 401703504

    loader = GolfEventLoader(event_id=event_id)
    
    ged = loader.load_golf_event_data()
    
    comp_data = ged.get_competition_data()
    
    competitors = comp_data.get_competitors()
    
    athletes = competitors.get_athletes()
    
    athletes_df = athletes.to_df()
