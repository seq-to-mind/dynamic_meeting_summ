import re
import random
import pickle


def filter_out_fillers(input_text):
    for i in ["Yeah", "Um", "Uh", "Hmm", "Ah", "Mm-hmm", "um", "uh", "yeah", "hmm", "ah", "mm-hmm"]:
        input_text = input_text.replace(" " + i + " ", " ")
    return input_text


""" indicate the subset type: train, eval, test """
task_type = "eval"
sample_list_file = "./AMI_data/lists/list.ami." + task_type
dialogue_file_path = "./AMI_data/ami/"
output_path = "./AMI_experiment/tmp_data_with_segments/"

sample_name_list = open(sample_list_file).readlines()
sample_name_list = [i.replace("\n", "") for i in sample_name_list]
print(len(sample_name_list))
print(sample_name_list)

all_doc_level_len_list = []

new_list = []
for tmp_f in sample_name_list:
    print(tmp_f)
    tmp_raw_lines = open(dialogue_file_path + tmp_f + ".da").readlines()

    tmp_abs_file_content = open(dialogue_file_path + tmp_f + ".abstract").readlines()
    tmp_abs_file_content = [i.strip() for i in tmp_abs_file_content if len(i.strip()) > 2]

    """ merge the adjacent summary sentences """
    for i in range(1, len(tmp_abs_file_content)):
        if tmp_abs_file_content[i][0].isdigit() and tmp_abs_file_content[i - 1][0].isdigit():
            tmp_abs_file_content[i - 1] = tmp_abs_file_content[i - 1] + " " + tmp_abs_file_content[i].strip().split("\t")[-1]
            tmp_abs_file_content[i] = ""
    tmp_abs_file_content = [i.strip() for i in tmp_abs_file_content if len(i.strip()) > 2]

    """ record the summary sentence line number """
    tmp_l = [k for k, v in enumerate(tmp_abs_file_content) if v[0].isdigit()]
    tmp_l.append(len(tmp_abs_file_content))

    raw_list_split_list = []
    tmp_one_sample_abs_list = []
    tmp_one_sample_source_list = []

    for i in range(len(tmp_l) - 1):
        tmp_abs = tmp_abs_file_content[tmp_l[i]].replace("\n", " ").split("\t")[2]

        if tmp_l[i] + 1 < len(tmp_abs_file_content):
            """ build the summary extractive sentence start/end index in the source content """
            tmp_start = tmp_abs_file_content[tmp_l[i] + 1].replace("\n", " ").split("\t")[0]
            tmp_end = tmp_abs_file_content[tmp_l[i + 1] - 1].replace("\n", " ").split("\t")[0]
            last_span_hint = " [SEP] " + tmp_abs_file_content[tmp_l[i + 1] - 1].replace("\n", " ").split("\t")[-5] + ": " + \
                             " ".join(tmp_abs_file_content[tmp_l[i + 1] - 1].replace("\n", " ").split("\t")[-1].split()[:5])
            assert len(tmp_start) > 5 and len(tmp_end) > 5
            for k, v in enumerate(tmp_raw_lines):
                if v.split("\t")[0] == tmp_start:
                    raw_list_start = k
                if v.split("\t")[0] == tmp_end:
                    raw_list_end = k
                    if raw_list_end >= raw_list_start:
                        raw_list_split_list.append([raw_list_start, raw_list_end])
                    else:
                        raw_list_split_list.append([raw_list_end, raw_list_start])
                    break
            # print(raw_list_split_list)
        else:
            raw_list_split_list.append([raw_list_split_list[-1][1] + 1, len(tmp_raw_lines)])
            last_span_hint = " [SEP] " + tmp_abs_file_content[tmp_l[i + 1] - 2].replace("\n", " ").split("\t")[-5] + ": " + \
                             " ".join(tmp_abs_file_content[tmp_l[i + 1] - 2].replace("\n", " ").split("\t")[-1].split()[:5])
        tmp_one_sample_abs_list.append([tmp_abs, last_span_hint])

    print("######################")

    """ if the extractive start/end position is too large, adjust the end position """
    for tmp_k, tmp_v in enumerate(raw_list_split_list):
        if tmp_v[1] - tmp_v[0] > (len(tmp_raw_lines) * 3 / len(raw_list_split_list)):
            print(tmp_v)
            raw_list_split_list[tmp_k][1] = int(raw_list_split_list[tmp_k][0] + (len(tmp_raw_lines) / len(raw_list_split_list)))
    print(raw_list_split_list)

    for i in range(len(raw_list_split_list)):
        raw_list_split_list[i].extend(tmp_one_sample_abs_list[i])
    raw_list_split_list = sorted(raw_list_split_list, key=lambda k: k[0])

    """ merge the start/end position when there are some overlap """
    merged_tmp_list = [raw_list_split_list[0], ]
    for i in range(1, len(raw_list_split_list)):
        if merged_tmp_list[-1][1] - 10 > raw_list_split_list[i][0] or (raw_list_split_list[i][1] - merged_tmp_list[-1][0] < 30):
            if merged_tmp_list[-1][1] >= raw_list_split_list[i][1]:
                merged_tmp_list[-1][1] = merged_tmp_list[-1][1]
                merged_tmp_list[-1][2] = merged_tmp_list[-1][2] + " " + raw_list_split_list[i][2]
                merged_tmp_list[-1][3] = merged_tmp_list[-1][3]
            else:
                merged_tmp_list[-1][1] = raw_list_split_list[i][1]
                merged_tmp_list[-1][2] = merged_tmp_list[-1][2] + " " + raw_list_split_list[i][2]
                merged_tmp_list[-1][3] = raw_list_split_list[i][3]
        else:
            merged_tmp_list.append(raw_list_split_list[i])

    raw_list_split_list = merged_tmp_list
    print([i[:2] for i in raw_list_split_list])

    for i in range(len(raw_list_split_list)):
        raw_list_split_list[i][0] = max(0, raw_list_split_list[i][0] - random.randint(5, 11))
        raw_list_split_list[i][1] = min(len(tmp_raw_lines), raw_list_split_list[i][1] + random.randint(7, 15))

    print("Add random pre/post sentences", [i[:2] for i in raw_list_split_list])
    print("######################")

    """ use the start/end indices to obtain source content segments """
    for i in raw_list_split_list:
        tmp_doc = []
        for j in range(i[0], i[1]):
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
        # print(tmp_doc)

        """ merge sentences with same speaker and EOS detection """
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

            """ filter the short utterances """
            if len("".join(filter(str.isalnum, tmp_t))) > 10:
                tmp_t = " <seg> " + tmp_role + " <say> " + tmp_t
                output_utter_list.append(tmp_t)

        assert len(output_utter_list) > 0
        tmp_one_sample_source_list.append(" ".join(output_utter_list))

    assert len(raw_list_split_list) == len(tmp_one_sample_source_list)

    """ merge the segmented source content with corresponding summary sentences """
    all_doc_level_len_list.append(len(raw_list_split_list))
    for i in range(len(raw_list_split_list)):
        new_list.append([raw_list_split_list[i][2] + raw_list_split_list[i][3], tmp_one_sample_source_list[i]])

output_doc_fp = open(output_path + task_type + ".source", "w", encoding="utf-8")
output_abs_fp = open(output_path + task_type + ".target.raw", "w", encoding="utf-8")

for i in new_list:
    if len(i[0]) > 3 and len(i[1]) > 0:
        output_abs_fp.write(i[0].strip() + "\n")
        tmp_doc = i[1].strip()
        """ here we use # as the utterance start indicator """
        if "#" in tmp_doc:
            print("FIND # in text!")
            raise Exception

        tmp_doc = re.sub("\{\S+\}", " ", tmp_doc)
        tmp_doc = tmp_doc.replace("<seg>", "#")
        tmp_doc = tmp_doc.replace(" <say>", ":")

        tmp_doc = re.sub("\s+", " ", tmp_doc) + "\n"
        output_doc_fp.write(tmp_doc)

pickle.dump(all_doc_level_len_list, open("./AMI_experiment/tmp_data_with_segments/" + task_type + "_seg_id_list.pickle", "wb"))

print(all_doc_level_len_list)
print(len(all_doc_level_len_list))
print(sum(all_doc_level_len_list))
