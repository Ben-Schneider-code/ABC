import os
import orjson 
from torch.utils.data import Dataset
import numpy as np
from datasets import load_dataset
from fetch_datasets.pretrain import check_pretraining_downloaded, get_pretraining_location
from fetch_datasets.instruct import check_finetuning_downloaded, get_finetuning_location
class ConceptualCaptionsPretrainAdapter(Dataset):


    def __len__(self):
        return len(self.meta)
    
    def __init__(self, negatives=None):      
        self.meta = load_dataset("TIGER-Lab/ABC-Pretraining-Data")["train"]
        assert check_pretraining_downloaded(), "Image Folder did not exist -- download it with`python fetch_datasets/pretrain.py`"
        self.root = get_pretraining_location(with_subdir=False)
        self.negatives = negatives

    def _attach_negatives(self, idx, item):
        
        offset = 5
        
        starts = np.arange(self.negatives) * offset
        offsets = np.random.randint(0, offset, size=self.negatives)
        neg_idx = starts + offsets

        negatives_for_idx = self.meta[idx]["negatives"]
        item["negatives"] = [self._create_candidate(self.meta[negatives_for_idx[i]]) for i in neg_idx]


    def _create_candidate(self, metadata, custom_caption = None):

        caption = metadata["caption"] 

        if custom_caption:
            caption = custom_caption

        return {
                "id": metadata["id"],
                "conversations": [
                    {
                        "from": "human",
                        "value": caption

                    },
                    {
                        "from": "gpt",
                        "value": ""
                    }
                ]
            }

    
    # Currently the modality is image -> text
    def __getitem__(self, idx):
        metadata = self.meta[idx]
        image = os.path.join(self.root, metadata["image"])

        formatted_item = {
            "id": metadata["id"],
            "url": metadata["url"], 
            "pos_cand": self._create_candidate(metadata),
            "query": {
                "id": metadata["id"],
                "image": image,
                "conversations": [
                    {
                        "from": "human",
                        "value": ""
                    },
                    {
                        "from": "gpt",
                        "value": ""
                    }
                ]
            }
        }
        
        if self.negatives is not None:
            self._attach_negatives(idx,formatted_item)

        return formatted_item

def format_cand(txt):
    return {
                "id": "nil",
                "conversations": [
                    {
                        "from": "human",
                        "value": txt

                    },
                    {
                        "from": "gpt",
                        "value": ""
                    }
                ]
    }

def format_inst_query(img_path, inst):
    return {
                "id": "nil",
                "image": img_path,
                "conversations": [
                    {
                        "from": "human",
                        "value": f"Instruction: {inst}"
                    },
                    {
                        "from": "gpt",
                        "value": ""
                    }
                ]
            }

class VGInstructAdapter(Dataset):

    def __init__(self):
        self.ds_defintion = load_dataset("TIGER-Lab/ABC-VG-Instruct")["train"]
        assert check_finetuning_downloaded(), "Image Folder did not exist -- download it with`python fetch_datasets/instruct.py`"
        self.root = get_finetuning_location()

    def __len__(self):
        return len(self.ds_defintion)

    def __getitem__(self, idx):
        
        items = self.ds_defintion[idx]

        return [{
            "id": str(i["id"]),
            "url": "nil", 
            "pos_cand": format_cand(i["phrase"]),
            "query": format_inst_query(os.path.join(self.root, f"{i["image"]}.jpg"), i["instruction"])
        } for i in items.values()]