from pathlib import Path
import numpy
import case
import os
import matplotlib.pyplot as plt
class Sweep():
    def __init__(self,path): 
        self.path = path
    def begin(self, variable: str, min:float, max:float, interval:float):
        self.registry = []
        for i in numpy.arrange(min,max+interval,interval):
            case_path = self.path / f"{variable} -> {i}"
            template_path = self.path / "CaseTemplate"
            match variable:
                case 'velocity': self.registry.append(case.Case(case_path, template_path, vel=i))
                case 'angle': self.registry.append(case.Case(case_path, template_path, angle=i))
                case _: raise ValueError(f"[INVALID]: variable '{variable}' is not proper. variable is required to be either 'velocity' or 'angle'")
            self.variable = variable
    def simpleFoam_monocore(self):
        for i in self.registry:
            i.run_cmd(['simpleFoam'])
    def simpleFoam_parallel(self,core:int = os.cpu_count()-2): 
        for i in self.registry: 
            i.parallelRun(core)
    def parse_all(self,lines:int = 5):
        result = {self.variable: [], "drag": [], "lift": []}
        for i in self.registry:
            i.parse(lines)
            result["drag"].append(i.drag)
            result["lift"].append(i.lift)
            match self.variable:
                case "velocity": result[self.variable].append(i.vel)
                case "angle": result[self.variable].append(i.angle)
        return result
    def plot(self, data:dict):
        plt.plot(
            data[self.variable], 
            data["lift"],
            color="c", label="Lift [N]"
            )
        plt.plot(
            data[self.variable], 
            data["drag"],
            color="b", label="Drag [N]"
            )
        plt.axhline(y=10000, color='r', label="Gravity [N]")
        plt.title(f"Forces on cow in varied {self.variable} of Current")
        if self.variable == "velocity": plt.xlabel("Velocity of Current [m/s]")
        elif self.variable == "angle": plt.xlabel("Angle of Current [deg]")
        plt.legend(
            loc='best',
            frameon=True,
            framealpha=0.8,
            edgecolor='lightgray',
            facecolor='white' 
        )
        outputPath = self.path / "results"
        outputPath.mkdir(parents=True, exist_ok=True)
        filePath = outputPath / f"[{self.variable}] cow_forces_result.png"
        plt.savefig(filePath, dpi=300, bbox_inches='tight')
        plt.show()
    def run(self, core:int = 0):
        if core == 1:self.simpleFoam_monocore()
        elif core == 0: self.simpleFoam_parallel()
        elif core<0: raise ValueError("[Error] variable 'core' in method 'run' is required to be at least zero.")
        else: self.simpleFoam_parallel(core)
        data = self.parse_all()
        self.plot(data)