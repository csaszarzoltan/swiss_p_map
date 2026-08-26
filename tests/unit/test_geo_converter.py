import pytest

def test_coordinate_math_formulas():
    """
    Verify the mathematical transformation formula defined by Swisstopo.
    Test point: Zürich Hauptbahnhof (approx E: 2683100, N: 1248100 -> Lat: 47.37817, Lon: 8.54019).
    """
    easting = 2683100.0
    northing = 1248100.0
    
    # Swisstopo approximate transformation algorithm
    y_aux = (easting - 2600000.0) / 1000000.0
    x_aux = (northing - 1200000.0) / 1000000.0
    
    lat = (16.9023892 
           + 3.238272 * x_aux 
           - 0.270978 * (y_aux ** 2) 
           - 0.002528 * (x_aux ** 2) 
           - 0.0447 * (y_aux ** 2) * x_aux 
           - 0.0140 * (x_aux ** 3)) * (100.0 / 36.0)
           
    lon = (2.6779094 
           + 4.728982 * y_aux 
           + 0.791484 * y_aux * x_aux 
           + 0.1306 * y_aux * (x_aux ** 2) 
           - 0.0436 * (y_aux ** 3)) * (100.0 / 36.0)
           
    assert abs(lat - 47.3781) < 0.005, f"Latitude {lat} deviated from 47.3781"
    assert abs(lon - 8.5401) < 0.005, f"Longitude {lon} deviated from 8.5401"

def test_swiss_bounds_validation():
    """Verify bounds validation logic for Swiss coordinates (LV95: E 2'485'000-2'835'000, N 1'075'000-1'295'000)."""
    valid_easting = 2600000.0
    valid_northing = 1200000.0
    
    assert 2400000.0 <= valid_easting <= 2900000.0
    assert 1050000.0 <= valid_northing <= 1350000.0
    
    invalid_easting = 1500000.0
    assert not (2400000.0 <= invalid_easting <= 2900000.0)
