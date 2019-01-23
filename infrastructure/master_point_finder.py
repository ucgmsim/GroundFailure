import argparse
import os
from subprocess import Popen
import sys


def main(args):
    imdb_fname = args.imdb
    landslide_fname = args.landslide
    liquefaction_fname = args.liquefaction
    files = ""
    if args.files:
        files = args.files
    else:
        folder = args.infrastructure_folder
        files = list(map(lambda x:os.path.join(folder, x), os.listdir(folder)))

    processes = []

    if imdb_fname != "None":
        script = "im_extractor.py"
        for input_file in files:
            output = os.path.join(args.output, os.path.basename(input_file.replace(".csv", "_PGA.csv")))
            cmd = [
                "python3",
                script,
                imdb_fname,
                input_file,
                output,
                "AlpineF2K_HYP01-47_S1244",
                "PGA"
                ]
            processes.append(Popen(cmd))

    if landslide_fname != "None":
        script = "landslide_association.py"
        for input_file in files:
            output = os.path.join(args.output, os.path.basename(input_file.replace(".csv", "_landslide.csv")))
            cmd = [
                "python3",
                script,
                landslide_fname,
                input_file,
                output
                ]
            processes.append(Popen(cmd))

    if liquefaction_fname != "None":
        script = "landslide_association.py"
        for input_file in files:
            output = os.path.join(args.output, os.path.basename(input_file.replace(".csv", "_liquefaction.csv")))
            cmd = [
                "python3",
                script,
                liquefaction_fname,
                input_file,
                output
                ]
            processes.append(Popen(cmd))
    for proc in processes:
        proc.wait()
    print("All tasks completed")


if __name__ == "__main__":

    parser = argparse.ArgumentParser('masterInfra')
    parser.add_argument('imdb', type=str, help='Path to imdb file. May be None')
    parser.add_argument('landslide', type=str, help='Path to landslide hdf5 file. May be None')
    parser.add_argument('liquefaction', type=str, help='Path to liquefaction hdf5 file. May be None')
    parser.add_argument('output', type=str, help='The folder to put all output files in.')

    files = parser.add_mutually_exclusive_group(required=True)
    files.add_argument('-g','--infrastructure_folder', type=str, help='Name of the rupture - should be unique per simulation')
    files.add_argument('-f', '--infrastructure_files', type=list, dest='files', nargs=argparse.REMAINDER, help='A list of infrastructure files to be processed' )

    if len(sys.argv) == 6:
        sys.argv.insert(5, "-g")
    
    #print(sys.argv)

    args = parser.parse_args()

    main(args)
