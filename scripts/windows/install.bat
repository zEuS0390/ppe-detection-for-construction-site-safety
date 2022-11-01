python -m venv .venv

@REM Install project dependencies
".venv/Scripts/activate" && pip install -r requirements.txt

@REM Clone YOLOR repository
git clone "https://github.com/WongKinYiu/yolor.git"
rmdir /s /q "./yolor/.git"

@REM ./yolor/models/models.py
powershell -Command "(Get-Content ./yolor/models/models.py) -replace 'from utils.google_utils import *', 'from yolor.utils.google_utils import ' | Out-File -encoding ASCII ./yolor/models/models.py"
powershell -Command "(Get-Content ./yolor/models/models.py) -replace 'from utils.layers import *', 'from yolor.utils.layers import ' | Out-File -encoding ASCII ./yolor/models/models.py"
powershell -Command "(Get-Content ./yolor/models/models.py) -replace 'from utils.parse_config import *', 'from yolor.utils.parse_config import ' | Out-File -encoding ASCII ./yolor/models/models.py"
powershell -Command "(Get-Content ./yolor/models/models.py) -replace 'from utils import torch_utils', 'from yolor.utils import torch_utils' | Out-File -encoding ASCII ./yolor/models/models.py"

@REM ./yolor/utils/datasets.py
powershell -Command "(Get-Content ./yolor/utils/datasets.py) -replace 'from utils.general import xyxy2xywh, xywh2xyxy', 'from yolor.utils.general import xyxy2xywh, xywh2xyxy' | Out-File -encoding ASCII ./yolor/utils/datasets.py"
powershell -Command "(Get-Content ./yolor/utils/datasets.py) -replace 'from utils.torch_utils import torch_distributed_zero_first', 'from yolor.utils.torch_utils import torch_distributed_zero_first' | Out-File -encoding ASCII ./yolor/utils/datasets.py"

@REM ./yolor/utils/general.py
powershell -Command "(Get-Content ./yolor/utils/general.py) -replace 'from utils.google_utils import gsutil_getsize', 'from yolor.utils.google_utils import gsutil_getsize' | Out-File -encoding ASCII ./yolor/utils/general.py"
powershell -Command "(Get-Content ./yolor/utils/general.py) -replace 'from utils.metrics import fitness, fitness_p, fitness_r, fitness_ap50, fitness_ap, fitness_f', 'from yolor.utils.metrics import fitness, fitness_p, fitness_r, fitness_ap50, fitness_ap, fitness_f' | Out-File -encoding ASCII ./yolor/utils/general.py"
powershell -Command "(Get-Content ./yolor/utils/general.py) -replace 'from utils.torch_utils import init_torch_seeds', 'from yolor.utils.torch_utils import init_torch_seeds' | Out-File -encoding ASCII ./yolor/utils/general.py"

@REM ./yolor/utils/layers.py
powershell -Command "(Get-Content ./yolor/utils/layers.py) -replace 'from utils.general import *', 'from yolor.utils.general import ' | Out-File -encoding ASCII ./yolor/utils/layers.py"

@REM ./yolor/utils/loss.py
powershell -Command "(Get-Content ./yolor/utils/loss.py) -replace 'from utils.general import bbox_iou', 'from yolor.utils.general import bbox_iou' | Out-File -encoding ASCII ./yolor/utils/loss.py"
powershell -Command "(Get-Content ./yolor/utils/loss.py) -replace 'from utils.torch_utils import is_parallel', 'from yolor.utils.torch_utils import is_parallel' | Out-File -encoding ASCII ./yolor/utils/loss.py"

@REM ./yolor/utils/plots.py
powershell -Command "(Get-Content ./yolor/utils/plots.py) -replace 'from utils.general import xywh2xyxy, xyxy2xywh', 'from yolor.utils.general import xywh2xyxy, xyxy2xywh' | Out-File -encoding ASCII ./yolor/utils/plots.py"
powershell -Command "(Get-Content ./yolor/utils/plots.py) -replace 'from utils.metrics import fitness', 'from yolor.utils.metrics import fitness' | Out-File -encoding ASCII ./yolor/utils/plots.py"

pause