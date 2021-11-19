# DNF5
DNF5 is a tool for tracking the propagation of 'A' records across the world as well as getting TTLs of domains.
This tool allows you to quantify the time taken from updating your A record, to the record being seen across all the nameservers of the world.

## Requirements
* Python 3.6+
* pip

## Installation
### Clone the repository
`git clone https://github.com/atharvac/DNF5.git`

### Open the folder in cmd/terminal
`cd DNF5`

### Use pip to install the tool
`python3 -m pip install .`

## Usage
### To get TTL Values of various domains
Enter the required domains in the ttl_hosts.csv file adn run the command.  
`dnf5 get-ttl-data --domains ttl_hosts.csv`  
This will give you the TTL of the domains in the file as well as some graphs for comparison.  
It will also give you the Mean, Median, Max and Min TTL of the hosts in the file.  

### Log the propagation time of an A record change
You can use the following command to get all the options available.  
`dnf5 propagation-logger --help`  
```
Usage: dnf5 propagation-logger [OPTIONS]

  Log the propagation time of 'A' records. Run this command immediately
  after changing the records.

Options:
  --nameservers TEXT  The CSV file containing the nameserver data
  --output TEXT       The output folder name
  --target TEXT       The ip the newly changed A record points to.  [required]
  --domain TEXT       The domain to test.  [required]
  --registrar TEXT    The domain registrar name.  [required]
  --polltime INTEGER  Time to wait between DNS requests in minutes.
  --help              Show this message and exit.
```  
  
  Example Command:  
  `dnf5 propagation-logger --nameservers ns_template.csv --target 159.65.x.x --domain example.com --registrar nc`
