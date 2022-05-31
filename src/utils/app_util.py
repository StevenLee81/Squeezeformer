from tqdm import tqdm
import tensorflow as tf

from .metric_util import wer, cer
from ..metrics.error_rates import ErrorRate
from .file_util import read_file

logger = tf.get_logger()


def evaluate_results(filepath: str):
    logger.info(f"Evaluating result from {filepath} ...")
    metrics = {
        "greedy_wer": ErrorRate(wer, name="greedy_wer", dtype=tf.float32),
        "greedy_cer": ErrorRate(cer, name="greedy_cer", dtype=tf.float32),
        "beamsearch_wer": ErrorRate(wer, name="beamsearch_wer", dtype=tf.float32),
        "beamsearch_cer": ErrorRate(cer, name="beamsearch_cer", dtype=tf.float32)
    }
    with read_file(filepath) as path:
        with open(path, "r", encoding="utf-8") as openfile:
            lines = openfile.read().splitlines()
            lines = lines[1:]  # skip header
    for eachline in tqdm(lines):
        _, _, groundtruth, greedy, beamsearch = eachline.split("\t")
        groundtruth = tf.convert_to_tensor([groundtruth], dtype=tf.string)
        greedy = tf.convert_to_tensor([greedy], dtype=tf.string)
        beamsearch = tf.convert_to_tensor([beamsearch], dtype=tf.string)
        metrics["greedy_wer"].update_state(decode=greedy, target=groundtruth)
        metrics["greedy_cer"].update_state(decode=greedy, target=groundtruth)
        metrics["beamsearch_wer"].update_state(decode=beamsearch, target=groundtruth)
        metrics["beamsearch_cer"].update_state(decode=beamsearch, target=groundtruth)
    for key, value in metrics.items():
        logger.info(f"{key}: {value.result().numpy()}")