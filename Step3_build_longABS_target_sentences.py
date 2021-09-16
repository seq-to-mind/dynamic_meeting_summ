import re
import random
import pickle
from rouge_score.rouge_scorer import RougeScorer

tmp_scorer = RougeScorer(rouge_types=["rouge1"])

""" indicate the subset type: train, eval, test """
task_type = "test"
sample_list_file = "./AMI_data/lists/list.ami." + task_type
dialogue_file_path = "./AMI_data/ami/"
output_path = "AMI_experiment/tmp_AMI_all_utterances/"

sample_name_list = open(sample_list_file).readlines()
sample_name_list = [i.replace("\n", "") for i in sample_name_list]
print(len(sample_name_list))
print(sample_name_list)

all_doc_level_len_list = []
all_long_summary_list = []

all_average_doc_level_len_list = []

paired_source_file = open("AMI_experiment/tmp_data_with_segments/" + task_type + ".source").readlines()
paired_target_file = open("AMI_experiment/tmp_data_with_segments/" + task_type + ".target.raw").readlines()
paired_target_coref_file = open("AMI_experiment/tmp_data_with_segments/" + task_type + ".target").readlines()

idx_range_list = pickle.load(open("./AMI_experiment/tmp_data_with_segments/" + task_type + "_seg_id_list.pickle", "rb"))

new_list = []

assert sum(idx_range_list) == len(paired_target_coref_file)

output_fp = open("./AMI_experiment/tmp_data_with_segments/" + task_type + ".target.plus_long", "w", encoding="utf-8")

unmatched_number = 0

for tmp_k, tmp_f in enumerate(sample_name_list):
    print(tmp_f)

    idx_start = sum(idx_range_list[:tmp_k])
    idx_end = sum(idx_range_list[:tmp_k]) + idx_range_list[tmp_k]

    tmp_long_abs_lines = open(dialogue_file_path + tmp_f + ".longabstract").readlines()
    tmp_long_abs_lines = [i.replace("\n", " ") for i in tmp_long_abs_lines]

    differ_list = []
    for one_seg in tmp_long_abs_lines:
        one_best_score = 0.0
        one_best_idx = None
        flag = False
        for j in range(idx_start, idx_end):
            if one_seg.lower() in paired_target_file[j].lower():
                flag = True

        if flag is False:
            for j in range(idx_start, idx_end):
                tmp = tmp_scorer.score(target=paired_source_file[j], prediction=one_seg)["rouge1"]
                if tmp.recall > 0.5 or tmp.precision > 0.5:
                    if max(tmp.recall, tmp.precision) > one_best_score:
                        one_best_score = max(tmp.recall, tmp.precision)
                        one_best_idx = j
            if one_best_idx is not None:
                print(one_best_idx, one_best_score)
                print(one_seg)
                # print(paired_source_file[one_best_idx])

                paired_target_coref_file[one_best_idx] = paired_target_coref_file[one_best_idx].split("[SEP]")[0] + one_seg + "[SEP]" + paired_target_coref_file[one_best_idx].split("[SEP]")[1]
            else:
                print("#missing sentence:", one_seg)
                unmatched_number += 1

output_fp.writelines(paired_target_coref_file)
output_fp.close()

segmented_summary_list = open("./AMI_experiment/tmp_data_with_segments/" + task_type + ".target.plus_long", encoding="utf-8").readlines()

""" write the merged long abstract summary for merged inference """
with open("./AMI_experiment/tmp_data_dialogue_level/" + task_type + ".doc_level_longabs", "w", encoding="utf-8") as fp:
    for tmp_k, tmp_f in enumerate(sample_name_list):
        print(tmp_f)
        idx_start = sum(idx_range_list[:tmp_k])
        idx_end = sum(idx_range_list[:tmp_k]) + idx_range_list[tmp_k]
        long_ABS = [i.split("[SEP]")[0].strip() for i in segmented_summary_list[idx_start:idx_end]]
        fp.write(" ".join(long_ABS) + "\n")

print("unmatched_number:", unmatched_number)
