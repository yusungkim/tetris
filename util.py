def get_record():
  try:
    with open('.record') as f:
      return f.readline()
  except FileNotFoundError:
    with open('.record', 'w') as f:
      f.write('0')
    return '0'


def set_record(record, score):
  rec = max(int(record), score)
  with open('.record', 'w') as f:
    f.write(str(rec))

def filenames(path):
  import glob
  return glob.glob(path)

def svg2png(path):
  import cairosvg
  print(f"Converting.. {path}")
  cairosvg.svg2png(url=f"{path}.svg", write_to=f"{path}.png")