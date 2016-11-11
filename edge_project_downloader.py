#!/usr/bin/python3.5

import os
import json
import sys
import argparse

from constants import *
from subprocess import call
from urllib.request import urlopen


def print_json_data(data):
    """Print Edge Project Json Data

    Args:
        data (json object): Json representation of edge projects

    Returns:
        None: None
    """
    j = 0
    for i in data:
        # print("Name: " + i["name"] + " Code: " + i["code"])
        print(get_project_str(i))
        j += 1
    print("Count: " + str(j))


def get_project_str(project):
    """Get project as string

    Args:
        project (dict): Object representing name and code of project

    Returns:
        str: String format
    """
    return "Name: " + project["name"] + " Code: " + project["code"]


def get_logfile_path(code):
    """Get the process.log file contents

    Args:
        code (str): Code for the project

    Returns:
        str: Url string
    """
    return DOMAIN + EO + code + LOG


def get_qc_trimmed_paths(code):
    """Get QC Trimmed Paths

    Args:
        code (str): Code of the project

    Returns:
        list: Of Paths
    """
    return [DOMAIN + EO + code + QC + QC1, DOMAIN + EO + code + QC + QC2]


def get_host_clean_paths(code):
    """Get host cleaned Paths

    Args:
        code (str): Code of the project

    Returns:
        list: Of Paths
    """
    return [DOMAIN + EO + code + HR + HR1, DOMAIN + EO + code + HR + HR2]


def get_contigs_path(code):
    """Get contigs path

    Args:
        code (str): Code of the project

    Returns:
        str: Path (url)
    """
    return DOMAIN + EO + code + ABA + CONTIGS


def wget(filename, url):
    """Call wget external using subsystem call

    Args:
        filename (str): Name and path to the file
        url (str): Locator to uniform resource

    Returns:
        None: None
    """
    call(["wget", "-O", filename, url],
         stdout=open("wget.log", 'w'),
         stderr=open("wget_error.log", 'w'))
    # call(["wget", "-O", "someses.html", "google.com"],
    #     stdout=open("wget.log", 'w'),
    #     stderr=open("wget_error.log", 'w'))


def validate_data(data, v):
    """Validate json file for corresponding project name and code

    Args:
        data (object): Json file object representing list of projects
        v (bool): Verbosity on

    Returns:
        None: Description
    """
    count = 0
    for i in data:
        name = i["name"]
        code = i["code"]
        if v:
            print("Getting: " + get_logfile_path(code))
        c = urlopen(get_logfile_path(code)).read().decode("utf-8")
        if name in str(c):
            count += 1
            if v:
                print("Matched!")
        else:
            if v:
                print("Mismatched! " + get_project_str(i))
    return count == len(data)


if __name__ == "__main__":
    # Parse command line argument options
    parser = argparse.ArgumentParser(description="Edge Project Downloader")
    # Add some argument options
    parser.add_argument('-t', '--trimmed',
                        action='store_true',
                        help='Download Only Trimmed Reads')
    parser.add_argument('-hc', '--hostcleaned',
                        action='store_true',
                        help='Download Only Host Cleaned Reads')
    parser.add_argument('-c', '--contigs',
                        action='store_true',
                        help='Download Only Contigs')
    parser.add_argument('-tc', '--trimmed_and_contigs',
                        action='store_true',
                        help='Download Trimmed Reads and Contigs')
    parser.add_argument('-hcc', '--host_cleaned_and_contigs',
                        action='store_true',
                        help='Download Host Cleaned Reads and Contigs')
    parser.add_argument('-thc', '--trimmed_cleaned_and_contigs',
                        action='store_true',
                        help='Download Trimmed, Cleaned Reads and Contigs')
    # Parse the arguments
    args = parser.parse_args()

    # print(args.trimmed)
    # print(args.hostcleaned)
    # print(args.contigs)
    # print(args.trimmed_and_contigs)
    # print(args.host_cleaned_and_contigs)
    # print(args.trimmed_cleaned_and_contigs)

    # Start Project Downloader
    try:
        # Try opening json file
        json_file = open(PLF).read()
    except FileNotFoundError:
        print("File Not Found!")
        sys.exit()
    # Get data from json file
    data = json.loads(json_file)

    # Print data
    # print_json_data(data)

    # Validate Data
    print("Validating Data...")
    if validate_data(data, False):
        print("Data Validation Complete!")
        # Make Directory PFD
        if not os.path.exists(PFD):
            print("Creating Directory...")
            os.makedirs(PFD)
        else:
            print("Projects Directory Exists!")

        for project in data:
            name = project["name"]      # Store Name
            code = project["code"]      # Store Code
            p_dir = PFD + "/" + name    # Create project directory
            # Make directory named i["name"] inside ProjectFiles
            if not os.path.exists(p_dir):
                os.makedirs(p_dir)

            print("Starting Download for " + name + " :")
            # If Any option that contains trimmed
            if (args.trimmed or
                args.trimmed_and_contigs or
                    args.trimmed_cleaned_and_contigs):
                # Download QC trimmed reads inside i["name"] and rename
                qc_paths = get_qc_trimmed_paths(code)
                print("    * Trimmed R1: " + qc_paths[0], end="")
                wget(p_dir + "/" + name + "_" + QC1, qc_paths[0])
                print("\t[o] Done!")
                print("    * Trimmed R2: " + qc_paths[1], end="")
                wget(p_dir + "/" + name + "_" + QC2, qc_paths[1])
                print("\t[o] Done!")
                print()

            # If Any option that contains host
            if (args.hostcleaned or
                args.host_cleaned_and_contigs or
                    args.trimmed_cleaned_and_contigs):
                # Download Host cleaned reads inside i["name"] and rename
                hr_paths = get_host_clean_paths(code)
                print("    * Cleaned R1: " + hr_paths[0], end="")
                wget(p_dir + "/" + name + "_" + HR1, hr_paths[0])
                print("\t[o] Done!")
                print("    * Cleaned R2: " + hr_paths[1], end="")
                wget(p_dir + "/" + name + "_" + HR2, hr_paths[1])
                print("\t[o] Done!")
                print()

            # If Any options that contains contigs
            if (args.contigs or
                args.trimmed_and_contigs or
                args.host_cleaned_and_contigs or
                    args.trimmed_cleaned_and_contigs):
                # Dowload contigs file and rename it
                contigs_path = get_contigs_path(code)
                print("    * Contigs: " + contigs_path, end="")
                wget(p_dir + "/" + name + "_" + CONTIGS, contigs_path)
                print("\t[o] Done!")
                print()
                print("<-------------------->")
                print()
    else:
        print("Data Validation Failed!")
        sys.exit()

    print("Procedure Has Been Finished Successfully!")
