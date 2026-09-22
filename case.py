from pathlib import Path
import shutil
import subprocess
import re

class Case():
    def __init__(self, path:Path, source:Path, angle:float, vel:float = 50):
        self.path = path
        self.angle = angle
        self.vel = vel
        shutil.copytree(source,path,dirs_exist_ok=True)
        if not angle == 0: 
            subprocess.run(["transformPoints", "-rollPitchYaw", f"(0, {angle}, 0)"], cwd=self.path)
        if not vel == 50: 
            Ufile = (self.path / "0" / "U")
            Utext = Ufile.read_text(encoding="utf-8")
            Utext = Utext.replace("{motherfucker}",str(self.vel))
            Ufile.write_text(Utext, encoding="utf-8")
        print(f"[Success] Case with Velocity {self.vel}m/s, Angle {self.angle} deg")
        print(f"[ Path  ] Case  in  {self.path.absolute()}")
    def run_cmd(self, cmd_list: list):
        log_file = self.path.parent / "logs" / f"{self.angle}deg-{self.vel}mps" /cmd_list[0]
        if not log_file.parent.is_dir(): 
            log_file.parent.mkdir(parents=True)
        with log_file.open("w", encoding="utf-8") as f:
            subprocess.run(
                cmd_list,
                cwd=self.path,
                stdout=f,
                stderr=subprocess.STDOUT,
                check=True
            )
        print(f"[Success] {cmd_list[0]} in Case {self.path.absolute()}")
    def parallelRun(self, subdomains: int):
        if subdomains < 2: raise ValueError(f"[Invalid Value: {subdomains}] numberOfSubdomains is required to be at least 2.")
        decomposeParDict = (self.path / "system" / "decomposeParDict")
        dictionary = decomposeParDict.read_text(encoding="utf-8")
        dictionary = dictionary.replace("{motherfucker}",str(subdomains))
        decomposeParDict.write_text(dictionary, encoding="utf-8")
        self.run_cmd(["decomposePar"])
        self.run_cmd(["mpirun", "-np", str(subdomains), "simpleFoam", "-parallel"])
        self.run_cmd(["reconstructPar"])
    def parse(self, lines):
        forces = (self.path / "postProcessing"/ "Forces"/ "0"/ "forces.dat")
        forces = forces.read_text()
        forces = forces.splitlines()[-1*lines:]
        liftList = []
        dragList = []
        for line in forces:
            vectors = re.findall(r"\(([^()]+)\)", line)
            f_a = vectors[0].strip().split()
            f_b = vectors[1].strip().split()
            lift = float(f_a[2]) + float(f_b[2])
            drag = float(f_a[1]) + float(f_b[1])
            dragList.append(drag)
            liftList.append(lift)
        self.drag = sum(dragList) / len(dragList)
        self.lift = sum(liftList) / len(liftList)
        return self.drag, self.lift
    