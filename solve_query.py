import subprocess
from decimal import Decimal

import yaml

container_id = subprocess.check_output("docker run -it --rm -v $PWD:$PWD -w $PWD -d zupermind/mcdp:2024 bash -l", shell=True).decode().strip()
print(f"Container ID: {container_id}")

query = "system"
# subprocess.run(f"docker exec {container_id} mcdp-solve-query --imp {query}", shell=True, check=True)

# Call your requirements
subprocess.run(f"docker exec {container_id} mcdp-solve --imp {query} '<10 kg, 3 , 900>'", shell=True, check=True)


# stop the docker container
subprocess.run(f"docker stop {container_id}", shell=True, check=True)