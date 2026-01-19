import os
import time
import mlflow

def setup_mlflow():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "onboarding-agent")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

def start_run_if_needed(run_name: str = "demo-run"):
    setup_mlflow()
    if mlflow.active_run() is None:
        mlflow.start_run(run_name=f"{run_name}-{int(time.time())}")

def log_params_once(params: dict):
    start_run_if_needed()
    for k, v in params.items():
        mlflow.log_param(k, v)

def log_metric(name: str, value: float):
    start_run_if_needed()
    mlflow.log_metric(name, value)
