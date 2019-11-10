from tornasole.core.writer import FileWriter
from tornasole.core.reader import FileReader
import numpy as np
from tornasole.core.modes import ModeKeys
from tornasole.trials import create_trial
from datetime import datetime
import socket
import glob

from .utils import write_dummy_collection_file
import shutil


def test_mode_writing():
    run_id = "trial_" + datetime.now().strftime("%Y%m%d-%H%M%S%f")
    worker = socket.gethostname()
    for s in range(0, 10):
        fw = FileWriter(trial_dir="ts_outputs/" + run_id, step=s, worker=worker)
        if s % 2 == 0:
            fw.write_tensor(
                tdata=np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32),
                tname="arr",
                mode=ModeKeys.TRAIN,
                mode_step=s // 2,
            )
        else:
            fw.write_tensor(
                tdata=np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32),
                tname="arr",
                mode=ModeKeys.EVAL,
                mode_step=s // 2,
            )
        fw.close()
    write_dummy_collection_file("ts_outputs/" + run_id)
    files = glob.glob("ts_outputs/" + run_id + "/**/*.tfevents", recursive=True)

    global_steps = []
    train_steps = []
    eval_steps = []
    for f in files:
        fr = FileReader(fname=f)
        for tu in fr.read_tensors():
            tensor_name, step, tensor_data, mode, mode_step = tu
            if step % 2 == 0:
                assert mode == ModeKeys.TRAIN
                train_steps.append(step // 2)
            else:
                assert mode == ModeKeys.EVAL
                eval_steps.append(step // 2)
            assert mode_step == step // 2
            global_steps.append(step)

    trial = create_trial("ts_outputs/" + run_id)
    assert trial.steps() == sorted(global_steps)
    assert trial.steps(ModeKeys.TRAIN) == sorted(train_steps)
    assert trial.steps(ModeKeys.EVAL) == sorted(eval_steps)
    shutil.rmtree("ts_outputs/" + run_id)
