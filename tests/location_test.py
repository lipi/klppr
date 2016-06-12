
from context import location


#
# Location constructor
#
def test_latlonalt_is_valid_location():
    assert location.Location(0, 0, 0).valid()


def test_latlon_only_is_valid_location():
    assert location.Location(0, 0).valid()


def test_location_default_not_valid():
    assert not location.Location().valid()


#
# distance tests
#
def test_distance_at_equator():
    assert 111195.0 == round(location.distance(
        location.Location(0, 0),
        location.Location(0, 1)))


def test_distance_at_45_south():
    assert 78626.0 == round(location.distance(
        location.Location(-45, 0),
        location.Location(-45, 1)))


def test_distance_of_invalid_location():
    assert 0.0 == location.distance(
        location.Location(),
        location.Location(-45, 1))


#
# bearing tests
#
def test_bearing_appx_45_degrees():
    # see http://www.gpsvisualizer.com/calculators#distance
    assert 44.996 == round(location.bearing(
        location.Location(0, 0),
        location.Location(1, 1)), 3)


def test_bearing_from_invalid_location():
    assert 0.0 == location.bearing(
        location.Location(),
        location.Location(1, 1))


#
# elevation tests
#
def test_elevation_appx_5_degree():
    assert 4.766 == round(location.elevation(
        location.Location(-36, 174, 0),
        location.Location(-36.0002, 174.0001, 2)), 3)


def test_elevation_invalid_location():
    assert 0.0 == location.elevation(
        location.Location(),
        location.Location(-36.0002, 174.0001, 2))
