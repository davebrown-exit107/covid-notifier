'''Handles the database definitions'''
# pylint: disable=no-member
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

from covid_notifier.app import db

class Subscriber(db.Model):
    '''Phone number subscribed to an update of some sort.'''
    __tablename__ = 'subscribers'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String)

    regions = db.relationship('Region', backref=db.backref('subscribers', lazy=True))

    def __init__(self, phone_number):
        self.phone_number = phone_number


class Region(db.Model):
    '''Region where entries can be assigned.
    Generally this is a county but there is one
    named 'Montana' that contains statewide
    rollups.'''
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_label = db.Column(db.String)
    name_abbr = db.Column(db.String)
    county_number = db.Column(db.String)
    fips = db.Column(db.String)

    entries = db.relationship("Entry")

    def __init__(self, name, name_label, name_abbr, county_number, fips):
        self.name = name
        self.name_label = name_label
        self.name_abbr = name_abbr
        self.county_number = county_number
        self.fips = fips


class Entry(db.Model):
    '''Entries assigned to a region.'''
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    total = db.Column(db.Integer)
    f_0_9 = db.Column(db.Integer)
    m_0_9 = db.Column(db.Integer)
    t_0_9 = db.Column(db.Integer)
    f_10_19 = db.Column(db.Integer)
    m_10_19 = db.Column(db.Integer)
    t_10_19 = db.Column(db.Integer)
    f_20_29 = db.Column(db.Integer)
    m_20_29 = db.Column(db.Integer)
    t_20_29 = db.Column(db.Integer)
    f_30_39 = db.Column(db.Integer)
    m_30_39 = db.Column(db.Integer)
    t_30_39 = db.Column(db.Integer)
    f_40_49 = db.Column(db.Integer)
    m_40_49 = db.Column(db.Integer)
    t_40_49 = db.Column(db.Integer)
    f_50_59 = db.Column(db.Integer)
    m_50_59 = db.Column(db.Integer)
    t_50_59 = db.Column(db.Integer)
    f_60_69 = db.Column(db.Integer)
    m_60_69 = db.Column(db.Integer)
    t_60_69 = db.Column(db.Integer)
    f_70_79 = db.Column(db.Integer)
    m_70_79 = db.Column(db.Integer)
    t_70_79 = db.Column(db.Integer)
    f_80_89 = db.Column(db.Integer)
    m_80_89 = db.Column(db.Integer)
    t_80_89 = db.Column(db.Integer)
    f_90_99 = db.Column(db.Integer)
    m_90_99 = db.Column(db.Integer)
    t_90_99 = db.Column(db.Integer)
    f_100 = db.Column(db.Integer)
    m_100 = db.Column(db.Integer)
    t_100 = db.Column(db.Integer)
    notes = db.Column(db.String)
    new_case = db.Column(db.Integer)
    total_deaths = db.Column(db.Integer)
    hospitalization_count = db.Column(db.Integer)
    total_recovered = db.Column(db.Integer)
    total_active = db.Column(db.Integer)

    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    region = db.relationship("Region", back_populates="entries")

    def __init__(self, region, date):
        self.region = region
        self.date = date

subscriptions = db.Table('subscriptions',
                db.Column('subscriber_id', db.Integer, db.ForeignKey('subscribers.id'), primary_key=True),
                db.Column('region_id', db.Integer, db.ForeignKey('regions.id'), primary_key=True)
                )

