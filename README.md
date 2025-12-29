Project Structure !!! 
<img width="716" height="268" alt="image" src="https://github.com/user-attachments/assets/cfd7479d-0508-43e1-8f16-62b95e6e5e27" />


🚀 Quick Start
Installation bash

# Clone repository
git clone https://github.com/ABHISHEK22KGP/X-RAY.git
cd X-RAY

# Install package
pip install -e .




Run the Demo

# Run competitor selection demo
python run_demo.py

# Start dashboard
python dashboard/server.py

---->>>> Open browser: http://localhost:8000


-------------------------------------------------------------------------------------------             System Design               -------------------------------------------------------------------------------

Three-Layer Design
# Layer 1: Logic
@xray.trace(name="Process Step", step_type="business")
def your_function(data):
    xray.add_reasoning("Readable explanation of logic")
    return processed_data

# Layer 2: Debugging SDK (Automatic)
# - Captures timing, inputs, outputs
# - Serializes to JSON
# - Manages trace lifecycle

# Layer 3: Visualization Dashboard
# - Web interface for trace inspection
# - Step-by-step execution flow
# - Performance analytics

-----------------------------------------------------------------------       Integration Guide                ---------------------------------------------------------------------

from xray_sdk.xray import xray  # 1. Import

@xray.trace(name="Function", step_type="type")  # 2. Decorate
def your_function(args):
    xray.add_reasoning("What happened")  # 3. Explain (optional)
    return result


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Video Walkthrough: [Link to be added]

-------------------------------------------------------------- Dashboard View ---------------------------------------------------------------------

<img width="1776" height="833" alt="image" src="https://github.com/user-attachments/assets/33733914-267f-42c5-a569-88adfc589a8f" />
