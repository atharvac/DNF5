import dns.resolver
import socket
import csv
import matplotlib.pyplot as plt


HOSTS = "ttl_hosts.csv"

# Read the csv file and store the hosts in a list.
def get_ttl_hosts(hostfile):
    host_list = []
    with open(hostfile, "r") as csvfile:
        csv_s = csv.reader(csvfile)
        next(csv_s)
        for x in csv_s:
            host_list.append(x[0])
    return host_list

# Get TTL for a host.
def get_domain_ttl(host):
    try:
        answers = dns.resolver.resolve(host, "NS")
        nameservers = []
        for x in answers:
            nameservers.append(socket.gethostbyname(str(x)))

        temp = dns.resolver.Resolver()
        temp.nameservers = nameservers
        answers = temp.resolve(host)
        return answers.rrset.ttl
    except Exception as e:
        print(f"Could not get TTL for {host} Please remove it from the csv for accurate data.")
        return 0

# Get TTL for all the domains in the list.
def get_ttl(host_list):
    ttl_list = []
    for host in host_list:
        answer = get_domain_ttl(host)
        ttl_list.append(answer/60)
        print(f"{host}----------->{answer/60:0.1f} minutes")
    return ttl_list


def visualize(host_list, ttl_list):
    plt.rcParams['font.size'] = '8'
    plt.figure(figsize=(25, 15))
    plt.barh(host_list, ttl_list, height = 0.6, color=['b','m'])
    plt.ylabel("Host", fontsize=12)
    plt.xlabel("Time To Live in minutes", fontsize=12)
    plt.title("TTL by host")
    plt.show()

def visualize_metadata(ttl_list):
    mean = sum(ttl_list) / len(ttl_list)
    ttl_list.sort()
    median = ttl_list[len(ttl_list)//2]
    max_ = max(ttl_list)
    min_ = min(ttl_list)
    data = [mean, median, max_, min_]
    names = ["Mean", "Median", "Max", "Min"]
    print()
    for x, y in zip(data, names):
        print(f"{y}----------->{x:0.2f} minutes")
    plt.rcParams['font.size'] = '8'
    plt.figure(figsize=(25, 15))
    plt.barh(names, data, height = 0.6, color=['b','m'])
    plt.ylabel("", fontsize=12)
    plt.xlabel("", fontsize=12)
    plt.title("TTL by host")
    plt.show()



if __name__ == "__main__":
    host_list = get_ttl_hosts(HOSTS)
    ttl_list = get_ttl(host_list=host_list)
    visualize(host_list, ttl_list)
    visualize_metadata(ttl_list=ttl_list)
