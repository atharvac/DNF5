import csv
import click
from .dns_logger import *
from .ttl_tester import *

@click.group()
def cli():
    pass


@cli.command()
@click.option("--out",
    default="template.csv",
    help="The CSV file containing the nameserver data",
    required=True)
def get_csv_templates(out):
    """Create csv template files, used to add nameservers and Domains."""
    nameserver_template = ["Name","Country","IP","Company"]
    ttl_template = ["Domains"]
    with open(f"ns_{out}", "w+") as nameserver_file:
        writer = csv.writer(nameserver_file)
        writer.writerow(nameserver_template)

    with open(f"ttl_{out}", "w+") as ttl_file:
        writer = csv.writer(ttl_file)
        writer.writerow(ttl_template)
    

@cli.command()
@click.option("--nameservers",
    default="ns_template.csv",
    help="The CSV file containing the nameserver data",
    required=False)
@click.option("--output",
    default="Output",
    help="The output folder name",
    required=False)
@click.option("--target",
    help="The ip the newly changed A record points to.",
    required=True)
@click.option("--domain",
    help="The domain to test.",
    required=True)
@click.option("--registrar",
    help="The domain registrar name.",
    required=True)
@click.option("--polltime",
    default=1,
    help="Time to wait between DNS requests in minutes.",
    required=False)
def propagation_logger(nameservers, output, target, domain, registrar, polltime):
    """Log the propagation time of 'A' records. Run this command immediately after changing the records."""
    if not os.path.exists(nameservers):
        print(f"Could not find the given path '{nameservers}' use --nameservers to specify another file.")
        return
    start_collection = StartDataCollection(
                target, domain, registrar, output_folder=output, nameservers=nameservers,
                domain_ttl=get_domain_ttl(domain)
            )
    start_collection.start(minutes_to_wait=int(polltime))
    start_collection.visualize()



@cli.command()
@click.option("--domains",
    default="ttl_template.csv",
    help="The CSV file containing the domains",
    required=True)
def get_ttl_data(domains):
    """Graph the TTL of various domains."""
    if not os.path.exists(domains):
        print(f"Could not find the given path '{domains}' use --domains to specify another file.")
        return
    host_list = get_ttl_hosts(domains)
    ttl_list = get_ttl(host_list=host_list)
    visualize(host_list, ttl_list)
    visualize_metadata(ttl_list=ttl_list)