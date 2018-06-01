from scrape_linkedin import ProfileScraper, MyConnectionScraper
from selenium.webdriver import Chrome
from joblib import Parallel, delayed
from scrape_linkedin.utils import split_lists
import os
import shutil
import json


def get_all_connections(output_file=None):
    """
    Get a list of all of your connections

    Args:
        output_file {str}: output file for the list

    Returns:
        {list}: list of connections (dict type). Each dict has 2 keys: name & id
    """
    with MyConnectionScraper as mcs:
        connections = mcs.scrape()
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(connections, f)
        return connections


def job(connections, output_file=None):
    assert output_file is not None
    with ProfileScraper() as ps:
        for connection in connections:
            connection['profile'] = ps.scrape(user=connection['id']).to_dict()
            connection['mutual_connections'] = list(
                map(lambda x: x['id'], ps.get_mutual_connections()))
    with open(output_file, 'w') as f:
        json.dump(connections, f)


def generate_graph_data(connections=None, num_instances=2, temp_dir='temp_data', output_file=None):
    """Generates the data needed for a map of your connections

    Gets a list of your connections, and their profile info + mutual connections
    Set num_instances to be greater than 1 to run it in parallel.

    Args:
        fresh {bool}: should it do a fresh scrape of your connections?
        connections {list}: pass a list of connections if not fresh
        num_instances {int}: number of parallel selenium instances to run
        temp_dir {str}: temporary directory to store data from a job
        output_file {str}: Output file for results

    Returns:
        {list}: list of dicts with 5 keys: id, name, profile, mutual_connections
                & connected_time 
    """
    assert connections != None
    chunks = split_lists(connections, num_instances)
    os.mkdir(temp_dir)

    # Parallelized jobs
    Parallel(n_jobs=num_instances)(delayed(job)(
        connections=chunks[i],
        output_file=temp_dir + '/{}.json'.format(i)
    ) for i in range(num_instances))

    all_data = []

    # Re-access and combine all temp data
    for i in range(num_instances):
        with open(temp_dir + '/{}.json'.format(i), 'r') as data:
            all_data += json.load(data)

    # Write results to output file
    if output_file:
        with open(output_file, 'w') as out:
            json.dump(all_data, out)

    # Clean up temp data
    shutil.rmtree(temp_dir)
    return all_data
