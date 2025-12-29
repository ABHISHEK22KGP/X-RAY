"""
xray.py - The debugger that actually tells you WHY things happened
Not just what happened, but the story behind it.
"""

import json
import time
import uuid
from datetime import datetime

# Each step in our detective story
class XRayStep:
    # When something happens, we write it down
    
    def __init__(self, name: str, step_type: str = "generic"):
        # Give this step a unique ID - like case file number
        self.id = str(uuid.uuid4())[:8]  # Short ID, easier to read
        self.name = name
        self.step_type = step_type
        
        # What went in, what came out
        self.input = {}
        self.output = {}
        self.reasoning = ""  # The "why" - most important part
        
        # When did this happen
        self.timestamp = datetime.now().isoformat()
        self.duration_ms = 0
        self.success = True
        self.error = None
        
        # Start the clock
        self._start_time = time.time()
        
    def end(self):
        # Stop timing
        self.duration_ms = (time.time() - self._start_time) * 1000
        
    def add_reasoning(self, reasoning: str):
        # Add the human explanation
        self.reasoning = reasoning
        
    def to_dict(self):
        # Convert to JSON for storage
        return {
            "id": self.id,
            "name": self.name,
            "step_type": self.step_type,
            "input": self.input,
            "output": self.output,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "duration_ms": round(self.duration_ms, 2),  # 2 decimal places is enough
            "success": self.success,
            "error": self.error
        }

class XRay:
    """
    The main detective class.
    Tracks everything that happens in your system.
    """
    
    def __init__(self):
        # We're keeping cases (traces) in memory
        self.current_trace_id = None
        self.traces = {}
        self._current_step = None  # What step are we in right now?
        
    def start_trace(self, trace_name: str = ""):
        # Start a new investigation
        timestamp = int(time.time())
        short_id = uuid.uuid4().hex[:8]
        self.current_trace_id = f"trace_{timestamp}_{short_id}"
        
        # Create case file
        self.traces[self.current_trace_id] = {
            "id": self.current_trace_id,
            "name": trace_name,
            "start_time": datetime.now().isoformat(),
            "steps": []  # Empty for now
        }
        
        print(f"\n Starting investigation: {trace_name}")
        print(f"   Case ID: {self.current_trace_id}")
        
        return self.current_trace_id
    
    def trace(self, name: str, step_type: str = "generic"):
        """
        Decorator to wrap any function.
        Put @xray.trace above any function you want to track.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Start tracking this step
                self._current_step = XRayStep(name, step_type)
                
                # Note down what went in
                self._current_step.input = self._capture_input(args, kwargs)
                
                try:
                    # Actually run the function
                    result = func(*args, **kwargs)
                    
                    # Note down what came out
                    self._current_step.output = {"result": self._make_json_safe(result)}
                    self._current_step.success = True
                    
                    return result
                    
                except Exception as e:
                    # Something went wrong - note it
                    self._current_step.success = False
                    self._current_step.error = str(e)
                    raise
                    
                finally:
                    # Stop timing
                    self._current_step.end()
                    
                    # Add to case file
                    if self.current_trace_id and self.current_trace_id in self.traces:
                        self.traces[self.current_trace_id]["steps"].append(
                            self._current_step.to_dict()
                        )
                    
                    # Show what happened
                    self._show_step_info(self._current_step)
                    
                    # Move on to next step
                    self._current_step = None
            
            return wrapper
        return decorator
    
    def add_reasoning(self, reasoning: str):
        if self._current_step:
            self._current_step.add_reasoning(reasoning)
        else:
            if self.current_trace_id and self.traces[self.current_trace_id]["steps"]:
                steps = self.traces[self.current_trace_id]["steps"]
                if steps:
                    # APPEND to existing reasoning, not overwrite!
                    if "reasoning" in steps[-1]:
                        steps[-1]["reasoning"] += f"\n{reasoning}"
                    else:
                        steps[-1]["reasoning"] = reasoning
    def end_trace(self):
        # Close the case file
        if not self.current_trace_id:
            return None
        
        trace = self.traces[self.current_trace_id]
        trace["end_time"] = datetime.now().isoformat()
        trace["total_steps"] = len(trace["steps"])
        
        # Add up all the time
        total_time = sum(step["duration_ms"] for step in trace["steps"])
        trace["total_duration_ms"] = round(total_time, 2)
        
        print(f"\n Investigation complete")
        print(f"   Case ID: {self.current_trace_id}")
        print(f"   Steps recorded: {trace['total_steps']}")
        print(f"   Total time: {total_time:.2f}ms")
        
        # Save to file
        case_id = self.current_trace_id
        self._save_to_file(case_id)
        
        # Reset for next case
        self.current_trace_id = None
        self._current_step = None
        
        return case_id
    
    def _save_to_file(self, trace_id: str):
        # Write case to JSON file
        if trace_id in self.traces:
            filename = f"trace_{trace_id}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(self.traces[trace_id], f, indent=2)
                print(f"   Saved to: {filename}")
            except Exception as e:
                print(f"   Couldn't save: {e}")
    
    def _capture_input(self, args, kwargs):
        # Convert function arguments to something we can store
        input_data = {}
        
        # Skip 'self' if it's a method
        start_idx = 0
        if args and hasattr(args[0], '__class__'):
            # It's probably a method, skip 'self'
            input_data["self"] = f"{args[0].__class__.__name__} object"
            start_idx = 1
        
        # Add all other arguments
        for i, arg in enumerate(args[start_idx:], start=start_idx):
            input_data[f"arg_{i}"] = self._make_json_safe(arg)
        
        # Add keyword arguments
        for key, value in kwargs.items():
            input_data[key] = self._make_json_safe(value)
        
        return input_data
    
    def _make_json_safe(self, value):
        # Make sure we can store this in JSON
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._make_json_safe(item) for item in value]
        elif isinstance(value, dict):
            return {str(k): self._make_json_safe(v) for k, v in value.items()}
        else:
            # For complex objects, just show type
            try:
                return str(value)[:150]  # Don't store giant strings
            except:
                return f"Object of type {type(value).__name__}"
    
    def _show_step_info(self, step):
        # Print step details to console
        status = "PASS" if step.success else "FAIL"
        
        print(f"\n Step: {step.name}")
        print(f"   Type: {step.step_type}")
        print(f"   Status: {status}")
        print(f"   Time: {step.duration_ms:.2f}ms")
        
        if step.reasoning:
            print(f"   Why: {step.reasoning}")
        
        if step.error:
            print(f"   Error: {step.error}")

# Create one global detective everyone can use
# Just import 'xray' and start decorating functions
xray = XRay()