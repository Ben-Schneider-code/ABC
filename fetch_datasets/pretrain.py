# fetches pretraining data, tools for validating that the data has been unpacked.
from datasets import config, load_dataset
import os
BOLD = '\033[1m'

hf_hub_tarball = ["abc-pretrain.tar.gz.part_aa",
                "abc-pretrain.tar.gz.part_ab",
                "abc-pretrain.tar.gz.part_ac",
                "abc-pretrain.tar.gz.part_ad",
                "abc-pretrain.tar.gz.part_ae",
                "abc-pretrain.tar.gz.part_af",
                "abc-pretrain.tar.gz.part_ag",
                "abc-pretrain.tar.gz.part_ah",
                "abc-pretrain.tar.gz.part_ai"]

def download_pretraining_data():
    ds = load_dataset("TIGER-Lab/ABC-Pretraining-Data")
    print(f"{BOLD}Downloading pretraining data, this could take a while...{BOLD}")
    cache_dir = config.HF_DATASETS_CACHE
    path = os.path.join(cache_dir, "tigerlab/abc-pretrain")
    os.makedirs(path, exist_ok=True)
    from huggingface_hub import hf_hub_download
    for tarball in hf_hub_tarball:
        hf_hub_download(repo_id="TIGER-Lab/ABC-Pretraining-Data", repo_type="dataset", filename=tarball, local_dir=path)

    print(f"{BOLD}Unpacking pretraining data, this could take a while...{BOLD}")
    os.system(f"cat {path}/abc-pretrain.tar.gz.part_* | tar -xvzf - -C {path} && rm {path}/abc-pretrain.tar.gz.part_*")


def check_pretraining_downloaded():
    img_path = get_pretraining_location()
    return os.path.isdir(img_path)

def get_pretraining_location(with_subdir=True):
    from datasets import config
    import os
    cache_dir = config.HF_DATASETS_CACHE

    if with_subdir:
        return os.path.join(cache_dir, "tigerlab/abc-pretrain/train")
    else:
        return os.path.join(cache_dir, "tigerlab/abc-pretrain")


if __name__ == "__main__":
    download_pretraining_data()
