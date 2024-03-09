'''Entry  point script'''
'''__main__.py allows us to run our python script with python -m '''
'''Fun right?'''

from mongocd import cli
from mongocd.Core.config import __app_name__

def main():
    cli.app(prog_name=__app_name__)
if __name__ == "__main__":
    main()
