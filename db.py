'''Handles the database connections and definitions'''
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

engine = create_engine('sqlite:///covid.sqlite', echo=False)
class Region(Base):
    '''Region where entries can be assigned.
    Generally this is a county but there is one
    named 'Montana' that contains statewide
    rollups.'''
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_label = Column(String)
    name_abbr = Column(String)
    county_number = Column(String)
    fips = Column(String)

    entries = relationship("Entry")

    def __init__(self, name, name_label, name_abbr, county_number, fips):
        self.name = name
        self.name_label = name_label
        self.name_abbr = name_abbr
        self.county_number = county_number
        self.fips = fips

    def __str__(self):
        return f"<Region: {self.name}>"

    def __repl__(self):
        return f"<Region: {self.name}>"


class Entry(Base):
    '''Entries assigned to a region.'''
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    total = Column(Integer)
    f_0_9 = Column(Integer)
    m_0_9 = Column(Integer)
    t_0_9 = Column(Integer)
    f_10_19 = Column(Integer)
    m_10_19 = Column(Integer)
    t_10_19 = Column(Integer)
    f_20_29 = Column(Integer)
    m_20_29 = Column(Integer)
    t_20_29 = Column(Integer)
    f_30_39 = Column(Integer)
    m_30_39 = Column(Integer)
    t_30_39 = Column(Integer)
    f_40_49 = Column(Integer)
    m_40_49 = Column(Integer)
    t_40_49 = Column(Integer)
    f_50_59 = Column(Integer)
    m_50_59 = Column(Integer)
    t_50_59 = Column(Integer)
    f_60_69 = Column(Integer)
    m_60_69 = Column(Integer)
    t_60_69 = Column(Integer)
    f_70_79 = Column(Integer)
    m_70_79 = Column(Integer)
    t_70_79 = Column(Integer)
    f_80_89 = Column(Integer)
    m_80_89 = Column(Integer)
    t_80_89 = Column(Integer)
    f_90_99 = Column(Integer)
    m_90_99 = Column(Integer)
    t_90_99 = Column(Integer)
    f_100 = Column(Integer)
    m_100 = Column(Integer)
    t_100 = Column(Integer)
    notes = Column(String)
    new_case = Column(Integer)
    total_deaths = Column(Integer)
    hospitalization_count = Column(Integer)
    total_recovered = Column(Integer)
    total_active = Column(Integer)

    region_id = Column(Integer, ForeignKey('regions.id'))
    region = relationship("Region", back_populates="entries")

    def __init__(self, region, date):
        self.region = region
        self.date = date

    def __str__(self):
        return f"<Entry: {self.id}>"

    def __repl__(self):
        return f"<Entry: {self.id}>"

def get_or_create(session, model, **kwargs):
    '''Mostly stolen from:
    https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create'''
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance
