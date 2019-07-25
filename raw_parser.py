from pathlib import Path


data_dir = Path("tide_data")
lines = data_dir.joinpath("boston_5780_raw.txt").read_text().split("\n")

output = ""
for line in lines:
    date = line[8:19]
    time = line[20:25]
    height = line[26:].strip()
    output += f"{date},{time},{height}\n"

output = output[:-1]

data_dir.joinpath("boston_5780.csv").write_text(output)
