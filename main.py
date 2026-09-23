import sweep
from pathlib import Path

scriptPath = Path(__file__).resolve()
projectRoot = scriptPath.parent
bull = sweep.Sweep((projectRoot / "flyingBull"))
bull.begin('angle',-180,180,5)
bull.run()
cow = sweep.Sweep((projectRoot / "flyingCow"))
cow.begin('angle',-180,180,5)
cow.run()