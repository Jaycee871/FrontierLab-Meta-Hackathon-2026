"""Entire test set is deliberately fictional. No biomedical findings asserted."""
from .demo_data import DEMO_PAPERS

def benchmark():
    # Text snippets are exact substrings of the invented abstracts.
    return DEMO_PAPERS[:], [
      {"id":"C01","paper_id":"SYNTHETIC:A","claim_key":"affinity","claim":"Case A improves binding under one buffer condition","quote":"a histidine variant improves target binding at acidic pH under one buffer condition","predicted":"SUPPORTED","gold":"SUPPORTED"},
      {"id":"C02","paper_id":"SYNTHETIC:B","claim_key":"affinity","claim":"Case B reduces affinity under another ionic condition","quote":"the same substitution reduces affinity at acidic pH under a different ionic-strength condition","predicted":"SUPPORTED","gold":"SUPPORTED"},
      {"id":"C03","paper_id":"SYNTHETIC:A","claim_key":"affinity","claim":"The effect replicates in every buffer","quote":"but no replication was conducted","predicted":"SUPPORTED","gold":"CONTRADICTED"},
      {"id":"C04","paper_id":"SYNTHETIC:B","claim_key":"affinity","claim":"Affinity improves under the different ionic-strength condition","quote":"the same substitution reduces affinity at acidic pH","predicted":"CONTRADICTED","gold":"CONTRADICTED"},
      {"id":"C05","paper_id":"SYNTHETIC:C","claim_key":"assay","claim":"Assay conditions affect observed pH effects","quote":"buffer and assay format could change the direction","predicted":"SUPPORTED","gold":"SUPPORTED"},
      {"id":"C06","paper_id":"SYNTHETIC:A","claim_key":"replication","claim":"Independent replication was completed in case A","quote":"no replication was conducted","predicted":"CONTRADICTED","gold":"CONTRADICTED"},
      {"id":"C07","paper_id":"SYNTHETIC:B","claim_key":"sample","claim":"Exactly 50 people participated","quote":"Small hypothetical sample","predicted":"SUPPORTED","gold":"INSUFFICIENT"},
      {"id":"C08","paper_id":"DOI:FAKE","claim_key":"affinity","claim":"An unknown DOI proves binding increases","quote":"histidine variant improves","predicted":"SUPPORTED","gold":"INSUFFICIENT"},
      {"id":"C09","paper_id":"SYNTHETIC:C","claim_key":"replication","claim":"The effect is observed in all proteins","quote":"","predicted":"SUPPORTED","gold":"INSUFFICIENT"},
      {"id":"C10","paper_id":"SYNTHETIC:A","claim_key":"affinity","claim":"The original source shows affinity reduction","quote":"the same substitution reduces affinity","predicted":"CONTRADICTED","gold":"INSUFFICIENT"}
    ]

def annotated_conflicts():
    # Two human-authored paired source reports are in tension; conditions differ.
    # Don't assert that different experimental conditions are proof of a logical contradiction.
    return [("SYNTHETIC:A","SYNTHETIC:B")]
