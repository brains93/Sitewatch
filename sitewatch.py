import argparse
import requests
import ppdeep
import json
import time
import logging

def gethash(domain):
    #pulls down HTML of site and hashs it
    try:
        # needs input sanitization here 
        r = requests.get(domain)
        logging.info(f'request for {domain} status code was {r.status_code}')
    except Exception:
        logging.error(f"could not access site status code was {r.status_code}")
    hash = ppdeep.hash(r.text)
    logging.info(f'hash of {domain}: {hash}')
    return hash

def addtofile(filename, domain, hash):
    try:
        # Try to open the file for reading and writing (a+ mode)
        with open(filename, 'r+') as file:
            # Attempt to load existing data
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                # If the file is empty or not valid JSON, initialize an empty dictionary
                data = {"domains": []}

            # Check if the domain is already in the list
            domain_entry = next((entry for entry in data["domains"] if domain in entry), None)

            data["domains"].append({domain: hash})

            # Move the file pointer to the beginning of the file for writing
            file.seek(0)
            # Truncate the file to remove old data
            file.truncate()
            # Write the updated data back to the file
            json.dump(data, file, indent=4)
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def compare(oldhash, newhash):
    '''
    returns true if the site has change or false if it has not
    '''
    sim = ppdeep.compare(oldhash, newhash)
    logging.info(f'sim of hash is {sim}')
    if sim <= 50:
        return True
    return False

def datafromfile(filename):
    try:
        with open(filename, 'r') as file:
            try:
                data = json.load(file)
                domain_list = data.get("domains", [])
                logging.debug(f'domain list is :{domain_list}')
                return domain_list
            except json.decoder.JSONDecodeError:
                logging.error("The file is empty or not valid JSON.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main():
    logging.basicConfig(filename='sitewatch.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')
    parser = argparse.ArgumentParser(description="simple code to watch for sites changing")
    parser.add_argument("--domain", help="The domain name to process")
    filename = 'domains.json'
    args = parser.parse_args()


    if args.domain:
        logging.info(f'domain provided, adding {args.domain} to file')
        domain = 'https://' + args.domain
        hash = gethash(domain)
        addtofile(filename, domain, hash )
    else:
        logging.info('No domain provided, starting loop')

        while True:
            domain_list = datafromfile(filename)
            for domain_entry in domain_list:
                        for domain, hashes in domain_entry.items():
                            oldhash = hashes
                            newhash = gethash(domain)
                            if compare(oldhash, newhash):
                                #can configure logger to print to stdout as well to file but found its messy 
                                print(f"{domain} has changed")
                                logging.info(f'{domain} has changed')
            logging.info('loop compleate waiting')
            time.sleep(60)
            

if __name__ == "__main__":
    main()