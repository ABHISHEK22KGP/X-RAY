# Project Structure !!! 
<img width="716" height="268" alt="image" src="https://github.com/user-attachments/assets/cfd7479d-0508-43e1-8f16-62b95e6e5e27" />


# 🚀 Quick Start
Installation 

Clone repository
git clone https://github.com/ABHISHEK22KGP/X-RAY.git

Install package

pip install -e .





# Run competitor selection demo
python run_demo.py

# Start dashboard
python dashboard/server.py

---->>>> Open browser: http://localhost:8000


# System Design  

Three-Layer Design

# Layer 1: Logic
<img width="403" height="89" alt="image" src="https://github.com/user-attachments/assets/22ee3610-c35f-4591-9375-d1b482a3c149" />


# Layer 2: Debugging SDK (Automatic)
- Captures timing, inputs, outputs
  
- Serializes to JSON
  
- Manages trace lifecycle

# Layer 3: Visualization Dashboard
- Web interface for trace inspection
  
- Step-by-step execution flow
  
- Performance analytics

# Integration Guide
<img width="474" height="137" alt="image" src="https://github.com/user-attachments/assets/4ad3c26e-f34c-49c7-b8df-f48097d5b7c2" />


#Video explanation

Video Walkthrough: [Link to be added]

# Known limitations / future improvements

No database - only saves to JSON files

No real-time updates - need to refresh dashboard

Works with one process only (not distributed)

Basic dashboard UI

Can't handle very large traces well

No authentication/security features

>>>> Things That Could Be Better

Sometimes timing is not 100% accurate

JSON files can get messy with many traces

Dashboard looks basic can make it better

>>>>> For Production Use

Not tested with high traffic

No backup system for traces

No monitoring or alerts

Only works with Python code

# Dashboard View - Just double click to zoom

<img width="1912" height="7959" alt="screencapture-localhost-8000-2025-12-29-11_57_49" src="https://github.com/user-attachments/assets/abc09b4d-a8d7-4ac8-a661-fdfb09ee9951" />


