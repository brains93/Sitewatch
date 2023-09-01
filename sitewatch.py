import argparse
import requests
import ppdeep
import json

def gethash(domain):
    #pulls down HTML of site and hashs it
    try:
        # needs input sanitization here 
        r = requests.get(domain)
    except:
        raise Exception(f"could not access site status code was {r.status_code}")
    hash = ppdeep.hash(r.text)
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
        print(f"An error occurred: {e}")

def compare(domain, oldhash, newhash):
    '''
    returns true if the site has change or false if it has not
    '''
    sim = ppdeep.compare(oldhash, newhash)

    if sim <= 50:
        return True
    return False

def datafromfile(filename):
    try:
        with open(filename, 'r') as file:
            try:
                data = json.load(file)
                domain_list = data.get("domains", [])
                for domain_entry in domain_list:
                    for domain, hashes in domain_entry.items():
                        print(f"Domain: {domain}")
                        print(f"Hashes:{hashes}")
            except json.decoder.JSONDecodeError:
                print("The file is empty or not valid JSON.")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(description="simple code to watch for sites changing")
    parser.add_argument("--domain", help="The domain name to process")
    filename = 'domains.json'
    args = parser.parse_args()


    if args.domain:
        domain = 'https://' + args.domain
        hash = gethash(domain)
        addtofile(filename, domain, hash )
    else:
        datafromfile(filename)
   


if __name__ == "__main__":
    main()