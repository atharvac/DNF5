import dns.resolver
import time
import csv
import sys
import pickle
import matplotlib.pyplot as plt
import os

LOGFILE = "logfile.txt"
NAMESERVERS = "nameservers.csv"
SEPARATOR = "++=============================================================================++"
OUTPUT_FOLDER = "Output"


def ts(brackets=True):
    out = f"{time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())}"
    if brackets:
        return f"[{out}]"
    return out


class DnsServer:
    def __init__(self, name, country, ip, company, target_ip, domain, start_time):
        self.name = name
        self.country = country
        self.ip = ip
        self.company = company

        self.timestamp = None
        self.target_ip = target_ip
        self.domain = domain
        self.start_time = start_time

        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [self.ip]

        self.resolved = False

    def __str__(self):
        timeres = self.timestamp-self.start_time
        if timeres < 60:
            out = f"{timeres:0.3f} seconds for {self.country} - {self.company} DNS"
        else:
            timeres_min = timeres // 60
            timeres_sec = timeres % 60
            out=f"{timeres_min} min {timeres_sec:0.3f} for {self.country} - {self.company} DNS"
        return out

    def resolve_target(self):
        try:
            for rdata in self.resolver.resolve(self.domain, 'A'):
                if str(rdata) == self.target_ip:
                    self.timestamp = time.time()
                    self.resolved = True
                    return True
        except Exception as e:
            print(e)



class FileManager:
    def __init__(self, output_folder):
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        TIMESTAMP = ts(False)
        if not os.path.exists(TIMESTAMP):
            os.mkdir(os.path.join(output_folder,TIMESTAMP))
        self.logfile = open(os.path.join(output_folder, TIMESTAMP, "logfile.txt"), "w+")
        self.summary_buffer = []
        self.savefile_name = os.path.join(output_folder, TIMESTAMP, f"savefile.pkl")
        self.summaryfile_name = os.path.join(output_folder, TIMESTAMP, f"summary.txt")

    def print_log(self, log):
        if type(log) == list:
            log = f"\n{ts()} ".join(log)
        print(f"{ts()} {log}")
        self.logfile.write(f"{ts()} {log} \n")


    def gen_summary(self, summary_line):
        if type(summary_line) == list:
            self.summary_buffer.extend(summary_line)
        else:
            self.summary_buffer.append(summary_line)

    def dump_savefile(self, data):
        with open(self.savefile_name, "wb+") as savefile:
            pickle.dump(data, savefile)

    def write_summary_to_disk(self):
        with open(self.summaryfile_name, "w+") as summaryfile:
            temp = "\n".join(self.summary_buffer)
            summaryfile.write(temp)
            summaryfile.write(SEPARATOR)

    def close_logfile(self):
        self.logfile.close()



class StartDataCollection:
    def __init__(self, target_ip, domain, registrar, nameservers, output_folder, domain_ttl):
        self.target_ip = target_ip
        self.domain = domain
        self.registrar = registrar
        self.nameservers = nameservers
        self.domain_ttl = domain_ttl

        self.current_ip = self.get_current_ip()

        self.start_time = time.time()
        self.dnsservers = self.get_nameservers()

        self.filemanager = FileManager(output_folder)
        self.init_summary()
        self.init_log()

    def get_nameservers(self):
        servers = []
        with open(self.nameservers, "r") as csvfile:
            csv_s = csv.reader(csvfile)
            next(csv_s)
            for x in csv_s:
                temp = DnsServer(
                    name=x[0],
                    country=x[1],
                    ip=x[2],
                    company=x[3],
                    target_ip=self.target_ip,
                    domain=self.domain,
                    start_time=self.start_time
                )
                servers.append(temp)
        return servers

    def get_current_ip(self):
        try:
            answers = dns.resolver.resolve(self.domain)
            for ans in answers:
                return str(ans)
        except Exception as e:
            return "0.0.0.0"

    def init_summary(self):
        summary = []
        start_time = time.localtime(self.start_time)
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', start_time)
        summary.append(SEPARATOR)
        summary.append(f"Start Time: {start_time}")
        summary.append(f"Current IP: {self.current_ip}")
        summary.append(f"Target IP: {self.target_ip}")
        summary.append(f"Domain: {self.domain}")
        summary.append(f"Domain TTL: {self.domain_ttl}")
        summary.append(f"Registrar: {self.registrar}")
        summary.append(SEPARATOR)
        self.filemanager.gen_summary(summary)

    def init_log(self):
        logs = []
        logs.append(f"{SEPARATOR}")
        logs.append(f"Current IP: {self.current_ip}")
        logs.append(f"Domain: {self.domain}")
        logs.append(f"Domain TTL: {self.domain_ttl}")
        logs.append(f"Registrar: {self.registrar}")
        logs.append(SEPARATOR)
        self.filemanager.print_log(logs)

    def add_summary_line(self, dns_obj):
        timeres = dns_obj.timestamp-dns_obj.start_time
        names = f"{dns_obj.country} - {dns_obj.company}"
        if timeres < 60:
            end =  f"{timeres:0.3f} sec\n"
        else:
            timeres_min = timeres // 60
            timeres_sec = timeres % 60
            end = f"{timeres_min} min {timeres_sec:0.3f} sec\n"

        names_len = len(names)
        time_start_index = 60
        if names_len > 60:
            time_start_index = names_len + 1
        spaces = time_start_index - names_len
        out = f"{names}{spaces*' '}{end}"
        self.filemanager.gen_summary(out)

    def visualize(self):
        countries = []
        times = []
        for x in self.dnsservers:
            if x.resolved:
                countries.append(x.country)
                times.append(x.timestamp-self.start_time)
        plt.rcParams['font.size'] = '7'
        plt.figure(figsize=(25, 15))
        plt.barh(countries, times, height = 0.6, color=['b','m'])
        plt.ylabel("Country", fontsize=12)
        plt.xlabel("Time to resolve in seconds", fontsize=12)
        plt.title("DNS resolution time by country")
        plt.show()

    def cleanup(self):
        dump = {
            "start_time": self.start_time,
            "domain": self.domain,
            "current_ip": self.current_ip,
            "target": self.target_ip,
            "registrar": self.registrar,
            "servers": self.dnsservers
        }
        self.filemanager.print_log(SEPARATOR)
        self.filemanager.close_logfile()
        self.filemanager.dump_savefile(dump)
        self.filemanager.write_summary_to_disk()

    def start(self, minutes_to_wait):
        stop_count = 0
        try:
            while True:
                for server in self.dnsservers:
                    if not server.resolved:
                        if server.resolve_target():
                            self.filemanager.print_log(str(server))
                            self.add_summary_line(server)
                            stop_count += 1
                        else:
                            self.filemanager.print_log(f"{server.country} Not updated")
                if stop_count >= len(self.dnsservers):
                    break
                self.filemanager.print_log(f"\nWaiting for {minutes_to_wait} minute(s)...\n")
                time.sleep(minutes_to_wait*60)
        except KeyboardInterrupt:
            print("Cleaning Up.....")
            self.cleanup()
            exit()
        self.cleanup()



if __name__ == "__main__":
    try:
        if len(sys.argv) == 4:
            target_ip = sys.argv[1]
            domain = sys.argv[2]
            registrar = sys.argv[3]
            start_collection = StartDataCollection(
                target_ip, domain, registrar, output_folder=OUTPUT_FOLDER, nameservers=NAMESERVERS,
                domain_ttl=1200
            )
            start_collection.start(minutes_to_wait=1)
            start_collection.visualize()

        else:
            print(
                "Arguments are: Target IP, Domain, Registrar. \n\
                e.g. python3 dns_logger.py 192.168.1.1 example.com registrar"
            )
    except KeyboardInterrupt:
        print("Execution interrupted")
        exit()
    except Exception as e:
        traceback = e.__traceback__
        while traceback:
            print("{}: {}".format(traceback.tb_frame.f_code.co_filename,traceback.tb_lineno))
            traceback = traceback.tb_next
        print(e)

