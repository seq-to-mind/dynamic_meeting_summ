import re
import random


def filter_out_fillers(input_text):
    for i in ["Yeah", "Um", "Uh", "Hmm", "Ah", "Mm-hmm", "um", "uh", "yeah", "hmm", "ah", "mm-hmm"]:
        input_text = input_text.replace(" " + i + " ", " ")
    return input_text


task_type = "test"
sample_list_file = "./AMI_data/lists/list.ami." + task_type
dialogue_file_path = "./AMI_data/ami/"
output_path = "AMI_experiment/tmp_data_dialogue_level/"

sample_name_list = open(sample_list_file).readlines()
sample_name_list = [i.replace("\n", "") for i in sample_name_list]
print(len(sample_name_list))
print(sample_name_list)

all_doc_level_len_list = []
all_long_summary_list = []

all_average_doc_level_len_list = []

new_list = []
for tmp_f in sample_name_list:
    print(tmp_f)
    tmp_raw_lines = open(dialogue_file_path + tmp_f + ".da").readlines()

    tmp_long_abs_lines = open(dialogue_file_path + tmp_f + ".longabstract").readlines()
    tmp_long_abs_lines = [i.replace("\n", " ")for i in tmp_long_abs_lines]
    tmp_long_abs_lines = " ".join(tmp_long_abs_lines)
    tmp_long_abs_lines = re.sub("\s+", " ", tmp_long_abs_lines)

    tmp_doc = []
    for j in range(len(tmp_raw_lines)):
        v = tmp_raw_lines[j].strip().split("\t")
        if len(v) > 1:
            try:
                utter = re.sub("\{\S+\}", " ", v[-1])
                utter = " " + utter + " "
                utter = filter_out_fillers(utter).strip()
                if len("".join(filter(str.isalnum, utter))) > 5:
                    tmp_doc.append([v[-5], " <seg> " + v[-5] + " <seg> " + utter])
            except:
                print("One line is not processed in conversation: ", j)

    # merge sentences with same speaker and EOS detection;
    merged_utter_list = []
    current_role = None
    current_clip = []
    for k, v in enumerate(tmp_doc):
        if k == (len(tmp_doc) - 1):
            v[1] = v[1] + " ."
        if len(current_clip) < 1:
            if (not v[1].strip().endswith(" .")) and (not v[1].strip().endswith(" ?")) and (not v[1].strip().endswith(" !")) and (not v[1].strip().endswith("\"")):
                current_clip.append(v[1])
                current_role = v[0]
            else:
                merged_utter_list.append(v[1])
                current_role = None
                current_clip = []
        else:
            if current_role == v[0]:
                if (not v[1].strip().endswith(" .")) and (not v[1].strip().endswith(" ?")) and (
                        not v[1].strip().endswith(" !")) and (not v[1].strip().endswith("\"")):
                    current_clip.append(v[1])
                    current_role = v[0]
                else:
                    current_clip.append(v[1])
                    merged_utter_list.append(" ".join(current_clip))
                    current_role = None
                    current_clip = []
            else:
                merged_utter_list.append(" ".join(current_clip))
                current_role = None
                current_clip = []

                if (not v[1].strip().endswith(" .")) and (not v[1].strip().endswith(" ?")) and (
                        not v[1].strip().endswith(" !")) and (not v[1].strip().endswith("\"")):
                    current_clip.append(v[1])
                    current_role = v[0]
                else:
                    merged_utter_list.append(v[1])
                    current_role = None
                    current_clip = []

    output_utter_list = []
    for tmp_i in merged_utter_list:
        tmp_t = tmp_i.strip()
        tmp_t = re.sub("\s+", " ", tmp_t)
        tmp_role = tmp_t.strip().split("<seg>")[1].strip()
        tmp_t = tmp_t.replace("<seg> " + tmp_role + " <seg>", " ")

        tmp_t = tmp_t.split()
        reduce_repeat_tmp = [tmp_t[i] for i in range(len(tmp_t)) if tmp_t[i] == 0 or tmp_t[i] != tmp_t[i - 1]]
        tmp_t = " ".join(reduce_repeat_tmp)

        # filter short utterances
        if len("".join(filter(str.isalnum, tmp_t))) > 10:
            tmp_t = " <seg> " + tmp_role + " <say> " + tmp_t
            output_utter_list.append(tmp_t)

    assert len(output_utter_list) > 0
    new_list.append(" ".join(output_utter_list))
    all_long_summary_list.append(tmp_long_abs_lines)

output_doc_fp = open(output_path + task_type + ".all.utter.source", "w", encoding="utf-8")

for i in new_list:
    if len(i) > 5:
        tmp_doc = i.strip()
        if "#" in tmp_doc:
            print("FIND # in text!")
            raise Exception

        tmp_doc = re.sub("\{\S+\}", " ", tmp_doc)
        tmp_doc = tmp_doc.replace("<seg>", "#")
        tmp_doc = tmp_doc.replace(" <say>", ":")
        tmp_doc = re.sub("\s+", " ", tmp_doc) + "\n"
        output_doc_fp.write(tmp_doc)

output_doc_fp = open(output_path + task_type + ".original.longAbs", "w", encoding="utf-8")
for i in all_long_summary_list:
    output_doc_fp.write(i+"\n")
