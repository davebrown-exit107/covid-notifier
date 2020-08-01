'''Commands for the flask application'''

##########################################
# Stdlib imports
###########################################
from datetime import datetime
from urllib.parse import quote

##########################################
# 3rd party imports
###########################################
import click

##########################################
# Application component imports
###########################################
from covid_notifier.app import notifier_app
from covid_notifier.helpers import insert_results, newer_data_available

@notifier_app.cli.command('pull-updates')
def pull_new_data():
    '''Pull new data from the state.'''
    if newer_data_available():
        click.echo('Newer data found online')
        base_url = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?'
        ret_format = 'json'
        where_query = 'Total <> 0'
        return_geometry = 'false'
        spatial_rel = 'esriSpatialRelIntersects'
        out_fields = 'orderByFields=NewCases desc,NAMELABEL asc&outSR=102100'
        result_offset = '0'
        result_record_count = '56'
        result_type = 'standard'
        cache_hint = 'true'

        click.echo('Building query')
        query_options = [
            "f={}".format(quote(ret_format)),
            "&where={}".format(quote(where_query)),
            "&returnGeometry={}".format(quote(return_geometry)),
            "&spatialRel={}".format(quote(spatial_rel)),
            "&outFields=*&{}".format(quote(out_fields)),
            "&resultOffset={}".format(quote(result_offset)),
            "&resultRecordCount={}".format(quote(result_record_count)),
            "&resultType={}".format(quote(result_type)),
            "&cacheHint={}".format(quote(cache_hint))
            ]

        full_url = ''.join([base_url, ''.join(query_options)])

        # Run the query
        click.echo('Requesting data')
        results = requests.get(full_url).json()

        # Find the date on the database
        url = 'https://services.arcgis.com/qnjIrwR8z5Izc0ij/arcgis/rest/services/COVID_Cases_Production_View/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=ScriptRunDate%20desc&resultOffset=0&resultRecordCount=1&resultType=standard&cacheHint=true'
        date_result = requests.get(url).json()
        current = datetime.fromtimestamp(date_result['features'][0]['attributes']['ScriptRunDate'] / 1000).date()

        # Insert the results into the database
        click.echo('Processing results and committing to the database')
        insert_results(results, current)

        click.echo(f'Results for {current} added to the database.')
    else:
        click.echo('No newer data found online')
