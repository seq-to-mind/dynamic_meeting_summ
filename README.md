## Introduction
One implementation of the paper "Dynamic Sliding Window for Meeting Summarization".

## Package Requirements
1. pytorch==1.7.1
2. transformers==4.8.2
3. click==7.1.2
4. sentencepiece==0.1.92
5. allennlp==2.6.0
6. allennlp-models==2.6.0

## AMI Data Processing
There are 4 steps to process the original AMI meeting conversations, to get the segmented samples described in the paper.  
  > `Step1_build_AMI_data_with_segments.py`  
  Splitting the meeting conversations as well as the summaries to multiple segments/snippets, this is based on the extractive supporting annotation in AMI data.  
  > `Step2_process_segmented_data.py`  
  Conducting simple coreference resolution on the summary snippets.  
  > `Step3_build_longABS_target_sentences.py`  
  The AMI data provides long abstract, to improve the informativeness of generation, we further merge them to the summary snippets.  
  > `Step4_build_AMI_all_utterances.py`  
  Building the dialogue level sample for testing.

## Citation
```
@article{liu2021dynamic,
  title={Dynamic Sliding Window for Meeting Summarization},
  author={Liu, Zhengyuan and Chen, Nancy F},
  journal={arXiv preprint arXiv:2108.13629},
  year={2021}
}
```
