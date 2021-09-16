import re

speaker_role_list = ["The user interface designer", "The marketing expert", "The project manager", "The industrial designer"]

""" Simple coreference resolution processing of the summary snippets """
for task_name in ["train", "eval", "test"]:
    file_path = "./AMI_experiment/tmp_data_with_segments/" + task_name + ".target.raw"
    text_list = open(file_path, encoding="utf-8").readlines()
    output_fp = open(file_path.replace(".raw", ""), "w", encoding="utf-8")

    tmp_new_list = []
    for k, v in enumerate(text_list):
        tmp_v = v
        tmp_v = tmp_v.strip()
        search_idx = k
        if tmp_v.startswith("He") or tmp_v.startswith("She"):
            flag = True
            while flag:
                search_idx -= 1
                for i in speaker_role_list:
                    if i.lower() in text_list[search_idx].lower():
                        flag = False
                        print(tmp_v)
                        tmp_v = i + " " + " ".join(tmp_v.split()[1:])
                        print(tmp_v)
                        print("################")
                        break

        tmp_new_list.append(tmp_v + "\n")

    assert len(tmp_new_list) == len(text_list)
    for i in tmp_new_list:
        output_fp.write(i)
