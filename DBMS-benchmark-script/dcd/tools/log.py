import logging

logging.basicConfig(filename='logs/log.txt', level=logging.INFO, format='%(message)s')
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log(msg: str):
  logging.info(msg)
  print(msg)

def open_log_files():
  open('logs/log.txt', 'w')
  open('logs/logterm.txt', 'w')