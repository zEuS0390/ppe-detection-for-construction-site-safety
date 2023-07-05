from argparse import ArgumentParser
import sys

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022 - 2023]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
        - LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

# This is the main entry point of the program.
# It calls the static method of the Application
# module to run the main process.
if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument(
            "-l", 
            "--local", 
            action="store_true", 
            help="Change the mode of the application is local or cloud based"
    )
    args = parser.parse_args()
    if args.local:
        from src import localapp
        print("Initializing local application")
        localapp.Application.main()
    else:
        from src.cloud import cloudapp
        print("Initializing cloud application")
        cloudapp.Application.main()

