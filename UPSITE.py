import pmids
import classify
import os
import gzip
import queries
import shutil
import csv
import decimal
import time
import sys
import math
import operator
import collections
import Cosine_Sim
from nltk.stem.porter import *
from os import listdir
from os.path import isfile, join
from random import randrange
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    


def get_already_downloaded_ids(q, models):
    current_dir = os.getcwd()
    already_downloaded_pmids = []
    for m in models:
        gene_dir_batch = current_dir + 'output/batch/genes/{0}/{1}' .format(m, q)
        gene_dir_single = current_dir + 'output/{0}/genes/{1}' .format(m, q)
        gene_dirs = [gene_dir_batch, gene_dir_single]
        for gene_dir in gene_dirs:
            if os.path.exists(gene_dir):
                onlyfiles = [ f for f in listdir(gene_dir) if isfile(join(gene_dir,f))]
                file_name_list = list(file_name for file_name in onlyfiles)
                for x in file_name_list:
                    if any(char.isdigit() for char in x):
                        if x.endswith('-pred.xml.gz'):
                            split_at_dash = x.split('-')
                            for piece_of_file_name in split_at_dash:
                                if piece_of_file_name.isdigit():
                                    if piece_of_file_name in already_downloaded_pmids:
                                        continue
                                    else:
                                        already_downloaded_pmids.append(str(piece_of_file_name)) 
    return already_downloaded_pmids   

def get_already_downloaded_file_paths(q, models, num_articles):
    current_dir = os.getcwd()
    already_downloaded_file_path_list = []
    files_to_delete = []
    count = 0
    for m in models:
        gene_dir_batch = current_dir + 'output/batch/genes/{0}/{1}' .format(m, q)
        gene_dir_single = current_dir + 'output/{0}/genes/{1}' .format(m, q)
        gene_dirs = [gene_dir_batch, gene_dir_single]
        for gene_dir in gene_dirs:
            if os.path.exists(gene_dir): 
                onlyfiles = [ f for f in listdir(gene_dir)]
                file_name_list = list(file_name for file_name in onlyfiles)
                for x in file_name_list:
                    if any(char.isdigit() for char in x):
                        if x.endswith('-pred.xml.gz'):
                            already_downloaded_file_path_list.append(gene_dir + '/' + x)
                            count += 1
                        else:
                            unwantedfile_path = gene_dir + '/' + x
                            files_to_delete.append(unwantedfile_path)
                        
    for fp in files_to_delete:
        try:
            os.unlink(fp) 
        except OSError:
            try:
                shutil.rmtree(fp)
            except OSError:
                pass       
    return already_downloaded_file_path_list    

# def run_tees_batch(q, id_list, models):
#     current_dir = os.getcwd()    
#     already_downloaded_pmids = get_already_downloaded_ids(q, models)
#     ignore_list_path = current_dir + '/text_files/id_ignore_list.txt'
#     pmid_ignore_list = []
#     with open (ignore_list_path, 'r') as f:
#         reader = csv.reader(f,delimiter='\t')
#         if reader:
#             for pmid_list in reader:
#                 pmid_ignore_list = pmid_list
#         else:
#             pmid_ignore_list = []
#             
#     pmid_run_list = [] 
#     for pmid in id_list:
#         if pmid in pmid_ignore_list:
#             continue
#         elif pmid in already_downloaded_pmids:
#             continue
#         else:
#             pmid_run_list.append(pmid)
# 
#     
# 
#     float_num = float(len(pmid_run_list))/25
#     rounded_up_num = math.ceil(float_num)
#     list_of_pmid_lists = []
#     for x in range(int(rounded_up_num)):
#         list_of_pmid_lists.append(pmid_run_list[25*x:(25*x)+24])  
# 
#     file_path_list = [] 
#     if not list_of_pmid_lists:
#         return file_path_list
#     else:
#         for plist in list_of_pmid_lists:
#             file_path = current_dir + 'output/batch/genes/{0}/{1}' .format(q , '-'.join(plist))
#             addition = '-pred.xml.gz'
#             file_path_check = file_path + addition
#             file_path_list.append(file_path)
#             
#             if os.path.exists(file_path_check):
#                 print '--------------------------------SKIPPING ALREADY DOWNLOADED ABSTRACTS {0}-------------------------------------------' .format(plist)
#             else:
#                 classify.classify('-'.join(plist),'GE11',file_path)               
#                 try:    
#                     classify.classify('-'.join(plist),'GE11',file_path)
#                 except (ValueError, UnicodeEncodeError, AssertionError, IndexError) as e:
#                     print 'error,', e
#                     file_path_list.remove(file_path)
#                     single_pmids_file_path_list = run_tees(q, plist)
#                     file_path_list += single_pmids_file_path_list
#         return file_path_list
    
def run_tees(q, id_list, models, text_file):
    current_dir = os.getcwd()
    ignore_list_path = current_dir + '/text_files/id_ignore_list2'
    pmid_ignore_list = []
    
    
    try:
        with open (ignore_list_path, 'r') as f:
            reader = csv.reader(f,delimiter='\t')
            for pmid_list in reader:
                pmid_ignore_list = pmid_list
    except Exception:
        print repr(open(ignore_list_path, 'rb').read(20000))
        fi = open(ignore_list_path, 'rb')
        data = fi.read()
        fi.close()
        fo = open(current_dir + '/text_files/id_ignore_list2', 'w')
        fo.write(data.replace('\x00', ''))
        fo.close()        
    
    
    file_path_list = []  
    
    if text_file == 'no':  
        for pmid in id_list:
            if pmid in pmid_ignore_list:
                pass
            else:
                for m in models:
                    print '--------------------------------------------model: {0}--------------------------------------------' .format(m)
                    TEES_output_file_path = current_dir + 'output/{0}/genes/{1}/{2}' .format(m, q ,pmid)
                    addition = '-pred.xml.gz'
                    full_file_path = TEES_output_file_path + addition
                    file_path_list.append(full_file_path)
                    if os.path.exists(full_file_path):
                        print '---------------------------SKIPPING ALREADY DOWNLOADED {0} ABSTRACT {1}---------------------------' .format(q, pmid)
                    else:
                        try:
                            classify.classify(pmid, m, TEES_output_file_path) 
                        except (ValueError, UnicodeEncodeError, AssertionError, IndexError) as e:
                            file_path_list.remove(full_file_path)
                            with open(ignore_list_path, 'a') as f:
                                f.write(pmid + '\t')
                                f.close()
    else:
        input_path_list = []
        if os.path.isdir(text_file):
            for f_name in os.listdir(text_file):
                input_path_list.append(text_file + '/' + f_name)

        for m in models:
            for input_path in input_path_list:
                print '--------------------------------------------model: {0}--------------------------------------------' .format(m)
                pmid = os.path.basename(input_path)
                print pmid
                TEES_output_file_path = current_dir + 'output/{0}/genes/{1}/{2}' .format(m, q ,pmid)
                addition = '-pred.xml.gz'
                fp_check = current_dir + 'output/{0}/genes/{1}/{2}' .format(m, q ,pmid + addition)
                file_path_list.append(fp_check)
                if os.path.exists(fp_check):
                    print '---------------------------SKIPPING ALREADY DOWNLOADED {0} ABSTRACT {1}---------------------------' .format(q, pmid)
                else:   
                    try:
                        classify.classify(input_path, m, TEES_output_file_path) 
                    except (ValueError, UnicodeEncodeError, AssertionError, IndexError) as e:
                        file_path_list.remove(TEES_output_file_path)
                    with open(ignore_list_path, 'a') as f:
                        pmid =''.join(i for i in pmid if i.isdigit())       #strips nonnumeric chars from 'PMID-39879897
                        f.write(pmid + '\t')
                        f.close()        
                        
    return file_path_list

def get_info_from_interaction_xml(file_paths):
    final_dict = {}
#    combined_final_dict = {}
#    indprotein_final_dict = {}
    for file_path in file_paths:
        print 'info from inter', file_path
        try:
            infile = gzip.open(file_path, 'r')
            tree = ET.ElementTree(file=infile)
            entity_dict = {}
            trigger_dict = {}
            entity_trigger_dict = {}
            for elem in tree.iter(tag='entity'):
                entity_trigger_dict[elem.attrib['id']]=elem.attrib['text']
                if 'source' in elem.attrib:
                    entity_dict[elem.attrib['id']] = elem.attrib['text']
                if 'umConf' in elem.attrib:
                    trigger_dict[elem.attrib['id']] = elem.attrib['text']
                if 'conf' in elem.attrib:
                    trigger_dict[elem.attrib['id']] = elem.attrib['text']
    #        entity_trigger_dict = dict(entity_dict.items() + trigger_dict.items())
            for elem in tree.iter(tag='interaction'):
                e1 = elem.attrib['e1']
                e2 = elem.attrib['e2']
                if (e1 in entity_trigger_dict) and (e2 in entity_trigger_dict):
                    e1_text = entity_trigger_dict[e1]
                    e2_text = entity_trigger_dict[e2]
                if (e1 in entity_dict) and (e2 in trigger_dict):
                    if e1_text not in final_dict:
                        final_dict[e1_text]=[e2_text]
                    else:
                        final_dict[e1_text].append(e2_text)  
                elif (e2 in entity_dict) and (e1 in trigger_dict):
                    if e2_text not in final_dict:
                        final_dict[e2_text]=[e1_text]
                    else:
                        final_dict[e2_text].append(e1_text)
                elif (e1 in entity_dict) and (e2 in entity_dict):
                    if e1_text not in final_dict:
                        final_dict[e1_text]=[e2_text]
                    else:
                        final_dict[e1_text].append(e2_text)
                    if e2_text not in final_dict:
                        final_dict[e2_text]=[e1_text]
                    else:
                        final_dict[e2_text].append(e1_text)
        except (IOError, ET.ParseError):
            continue
    print final_dict        
    return final_dict	
    
def get_all_words_dict(q1, q2, q1_dict, q2_dict):
    all_words_dict = {}
    if q1_dict:
        all_q1_words = []
        for q in q1_dict:
            all_q1_words.extend(q1_dict[q])
        all_words_dict[q1] = all_q1_words
        
    if q2_dict:
        all_q2_words = []
        for q in q2_dict:
            all_q2_words.extend(q2_dict[q])
        all_words_dict[q2] = all_q2_words
    
    if not q1_dict:
        all_words_dict[q1] = []
    if not q2_dict:
        all_words_dict[q2] = []
    
    return all_words_dict

    
def normalize_dict(dict_in, query, stemmed):
    stemmer = PorterStemmer()
    dict_x = {}
    for k, v in dict_in.iteritems():
        v_lower = []
        for word in v:
            if not word[0].isalnum():
                word = word[1:]
            if stemmed == 'yes':
                word = stemmer.stem(word)
            v_lower.append(str(word.lower()))            #stemmer 
        if k.lower() not in dict_x:
            dict_x[k.lower()] = v_lower 
        else:
            dict_x[k.lower()] += v_lower 
    normalized_dict = {}
    for entity in dict_x:
        try:
            if entity in normalized_dict:
                normalized_dict[entity] += dict_x[entity]
            elif entity == query.q1.lower():
                if query.q1.lower() in normalized_dict:
                    normalized_dict[entity] += dict_x[entity]
                else:
                    normalized_dict[entity] = dict_x[entity]  
            elif entity == query.q2.lower():
                if query.q2.lower() in normalized_dict:
                    normalized_dict[entity] += dict_x[entity]
                else:
                    normalized_dict[entity] = dict_x[entity]               
            else:
                if query.q1_syns:
                    if entity in query.q1_syns:
                        if query.q1.lower() in normalized_dict:
                            normalized_dict[query.q1.lower()] += dict_x[entity]
                        else:
                            normalized_dict[query.q1.lower()] = dict_x[entity]
                if query.q2_syns:   
                    if entity in query.q2_syns:
                        if query.q2.lower() in normalized_dict:
                            normalized_dict[query.q2.lower()] += dict_x[entity]
                        else:
                            normalized_dict[query.q2.lower()] = dict_x[entity]
                else:
                    pass
                
        except TypeError:
            pass
        
    return normalized_dict

def combine_dictionaries(query_dicts):
    combined_dict = {}
    for d in query_dicts:
        for k in d:
            if k not in combined_dict:
                combined_dict[k] = d[k]
            else:
                combined_dict[k] += d[k]    
    return combined_dict

def output_pair_score_dict(angle_list, protein_dict, q1, q2, input_type, outputFileName):
    current_dir = os.getcwd()  
    if input_type == 'known':
        write_path = current_dir + '/text_files/output_known_interactions.txt'              
    elif input_type == 'unknown' or input_type =='random':
        write_path = current_dir  + '/text_files/output_random_interactions.txt'               
    elif outputFileName:
        write_path = current_dir + '/text_files/' +str(outputFileName)   
    else:       
        write_path = current_dir + '/text_files/' +str(input_type)            
    with open (write_path,'a') as f:
        f.write(q1+'\t'+q2+'\t')
        f.write(str(angle_list))
        f.write(str('\t'))
        f.write(str(protein_dict))
        f.write(str('\n'))  
             
def main(q1, q2, articles, batch, input_type, outputFileName, dictType, outputType, evaluation_mode, stemmed, model, text_file):
    models = model.split(' ')
    num_articles = int(articles)
    query = queries.main(q1,q2)
    q1_dict = {}
    q2_dict = {}

    q1_already_downloaded_ids = get_already_downloaded_ids(q1, models)
    q2_already_downloaded_ids = get_already_downloaded_ids(q2, models)
    q1_already_downloaded_file_path_list = get_already_downloaded_file_paths(q1, models, num_articles)
    q2_already_downloaded_file_path_list = get_already_downloaded_file_paths(q2, models, num_articles)
    
    q1_already_dl_slice = None
    q2_already_dl_slice = None
    q1_file_paths = None
    q2_file_paths = None 
    
    
#     if num_articles <= len(q1_already_downloaded_file_path_list):
#         q1_already_dl_slice = q1_already_downloaded_file_path_list[:num_articles]
#         q1_dict = get_info_from_interaction_xml(q1_already_dl_slice)
#    else:

    if num_articles * 100 <= len(q1_already_downloaded_file_path_list):
        q1_already_dl_slice = q1_already_downloaded_file_path_list[:num_articles]
        q1_dict = get_info_from_interaction_xml(q1_already_dl_slice)
    else:
        q1_id_list = pmids.main(query.q1, num_articles, query.q1_search_string, evaluation_mode)
        if len(q1_id_list) == len(q1_already_downloaded_file_path_list):
            q1_dict = get_info_from_interaction_xml(q1_already_downloaded_file_path_list)
        else:
            if batch == 'yes':
                q1_file_paths = run_tees_batch(q1, q1_id_list, models, text_file)
            elif batch == 'no':
                q1_file_paths = run_tees(q1, q1_id_list, models, text_file)
            if not q1_file_paths:
                q1_file_paths = q1_already_downloaded_file_path_list[:num_articles]
            q1_dict = get_info_from_interaction_xml(q1_file_paths)
    
    if num_articles * 100 <= len(q2_already_downloaded_file_path_list):
        q2_already_dl_slice = q2_already_downloaded_file_path_list[:num_articles]
        q2_dict = get_info_from_interaction_xml(q2_already_dl_slice)
    else:
        q2_id_list = pmids.main(query.q2, num_articles, query.q2_search_string, evaluation_mode)
        if len(q2_id_list) == len(q2_already_downloaded_file_path_list):
            q2_dict = get_info_from_interaction_xml(q2_already_downloaded_file_path_list)
        else:
            if batch == 'yes':
                q2_file_paths= run_tees_batch(q2, q2_id_list, models, text_file)
            elif batch == 'no':
                q2_file_paths= run_tees(q2, q2_id_list, models, text_file)
            if not q2_file_paths:
                q2_file_paths = q2_already_downloaded_file_path_list[:num_articles]
            q2_dict = get_info_from_interaction_xml(q2_file_paths)


    if q1_already_dl_slice:
        q1_num_docs_processed = len(q1_already_dl_slice)
    elif q1_file_paths:
        q1_num_docs_processed = len(q1_file_paths)
    else:
        q1_num_docs_processed = len(q1_already_downloaded_file_path_list)
        
    if q2_already_dl_slice:
        q2_num_docs_processed = len(q2_already_dl_slice)
    elif q2_file_paths:
        q2_num_docs_processed = len(q2_file_paths)
    else:
        q2_num_docs_processed = len(q2_already_downloaded_file_path_list)
        
    print q1, 'num_docs_processed', q1_num_docs_processed
    print q2, 'num_docs_processed', q2_num_docs_processed
    num_docs_processed = [q1_num_docs_processed,q2_num_docs_processed]
    
    return_dict_s = []
    if dictType == 'all':
        all_words_dict = get_all_words_dict(q1, q2, q1_dict, q2_dict)
        normalized_all_words_dict = normalize_dict(all_words_dict, query, stemmed)
        return_dict_s.append(normalized_all_words_dict)
        if len(normalized_all_words_dict[query.q1.lower()]) < 1 or len(normalized_all_words_dict[query.q2.lower()]) < 1:
            angle_list = [90.00]
        else:
            angle_list = Cosine_Sim.main(normalized_all_words_dict, q1, q2)
        
    if dictType == 'protein':
        query_dicts = [q1_dict, q2_dict]
        combined_dict = combine_dictionaries(query_dicts)
        normalized_protein_dict = normalize_dict(combined_dict, query, stemmed)
        return_dict_s.append(normalized_protein_dict)
        if len(normalized_protein_dict[query.q1.lower()]) < 1 or len(normalized_protein_dict[query.q2.lower()]) < 1:
            angle_list = [90.00]
        else:
            angle_list = Cosine_Sim.main(normalized_protein_dict, q1, q2)


    return angle_list, return_dict_s, num_docs_processed

def write_output(list_of_queries, iteration_angle_dict, angle_score_query_dict, angle_protein_word_dicts, input_type, outputFileName, 
                 outputType, num_processed_docs, final_protein_word_dict):
    
    current_dir = os.getcwd()  
    ordered_iteration_angle_dict = collections.OrderedDict(sorted(iteration_angle_dict.items()))  

    if not outputFileName:
        outputFileName = outputType
        

    write_path = current_dir + '/text_files/final_protein_word_dict.txt'
    with open (write_path, 'w') as f:    
        for x in final_protein_word_dict:
            for key in x[0]:
                f.write(str(key))
                f.write('\t')
                term_count_dict = {}
                for val in x[0][key]:
                    if val not in term_count_dict:
                        term_count_dict[val] = 1
                    else:
                        term_count_dict[val] += 1
                tot_term_count = sum(term_count_dict.values())
                tfd = {}
                for key, value in term_count_dict.items():              #term_frequency
                    tfd[key] = round(float(value) / float(tot_term_count), 6)        # round
#                    tfd[key] = float(value) / float(tot_term_count) 
                sorted_tfd = sorted(tfd.items(), key=operator.itemgetter(1), reverse= True)        #sort by values in dict, returns list of tuples sorted by second element
                f.write(str(sorted_tfd))
                f.write('\t')
                f.write('\n')
        
    if outputType == 'normal':
        if input_type == 'known':
            write_path = current_dir + '/text_files/output_known_interactions.txt'        
        elif input_type == 'unknown' or input_type =='random':
            write_path = current_dir  + '/text_files/output_random_interactions.txt'             
        elif outputFileName:
            write_path = current_dir + '/text_files/' +str(outputFileName)  
        else:       
            write_path = current_dir + '/text_files/' +str(input_type)             
        with open (write_path,'a') as f:
            f.write(str('\t'))
            for protein_dict in angle_protein_word_dicts:
                f.write(str(protein_dict))
                f.write(str('\n'))
            
    if outputType == 'tab':
        write_path = current_dir + '/text_files/results/{0}.tsv' .format(outputFileName)
        with open(write_path, 'wb') as f:
            f.write('# articles') 
            f.write('\t')  
            for q in list_of_queries:
                f.write(q)
                f.write('\t')
            f.write('\n')
            for article_cycle in ordered_iteration_angle_dict:
                f.write(str(article_cycle) + '\t')
                for angle in ordered_iteration_angle_dict[article_cycle]:
                    f.write(str(angle[0]) + '\t')
                f.write(str('\n'))
            f.write('\n')
            f.write('# docs q1')
            f.write('\t')
            for num_docs in num_processed_docs:
                f.write(str(num_docs[0]))
                f.write('\t')
            f.write('\n')
            f.write('# docs q2')
            f.write('\t')
            for num_docs in num_processed_docs:
                f.write(str(num_docs[1]))
                f.write('\t')
            f.write('\n')
            
            f.write('List_length_A')
            f.write('\t')
            values_list = []
            print 'final_protein_word_dict', final_protein_word_dict
            for protein_dict in final_protein_word_dict:
                len_of_values_new = []
                for v in protein_dict[0].itervalues():
                    len_of_values_new.append(len(v))
#                 values_len = sum(len(v) for v in protein_dict[0].itervalues())
#                 if values_len >= 0:
#                     values_list.append(values_len)
#                 else:
#                     values_list.append(0)
                values_list.append(len_of_values_new)
            for val in values_list:
                f.write(str(val[0]))
                f.write('\t')
            f.write('\n')
            f.write('List_length_B')
            for val in values_list:
                f.write(str(val[1]))
                f.write('\t')
            f.write('\n')
                                
    raw_input('press enter to continue')    
#    print "iteration_angle_dict", iteration_angle_dict
#    raw_input('press enter to continue')
#    print 'angle_score_query_dict', angle_score_query_dict
#   raw_input('press enter to continue')
#    print 'angle_protein_word_dicts', angle_protein_word_dicts
#   raw_input('press enter to continue')
#   print 'list_of_queries', list_of_queries
            

def index(q1, q2, num_articles, batch, input_type , outputFileName, dictType, outputType, iterate, evaluation_mode, iteration_type, stemmed, model, text_file):
    articles_per_cycle = []   
    if iterate == 'yes':
        if batch == 'yes':
            raise Exception("Batch downloads 25 files at a time and doesn't work with iteration!")
        else:
            if iteration_type == 'list_len':
                articles_per_cycle.append(num_articles)
            if iteration_type == 'docs':
                num_iterations = int(num_articles) / 5
                for num in range(num_iterations):
                    num_articles_split = 5* (num + 1)
                    articles_per_cycle.append(num_articles_split)
        
        iteration_angle_dict = {}
        angle_score_query_dict ={}
        angle_protein_word_dicts = []
        list_of_queries = []
        
        for articles in articles_per_cycle:
            list_of_protein_pairs = []
            if input_type == 'single':
                list_of_protein_pairs.append([q1,q2])
            else:
                if input_type =='50examples':
                    file_entry = r'/text_files/madhavi_example_protein_interactions.txt' 
                          
                if input_type =='known':
                    file_entry = r'/text_files/known/known_interactions.tsv'
                if input_type =='known1':
                    file_entry = r'/text_files/known/known_interactions1.tsv'
                if input_type =='known2':
                    file_entry = r'/text_files/known/known_interactions2.tsv'
                if input_type =='known3':
                    file_entry = r'/text_files/known/known_interactions3.tsv'
                if input_type =='known4':
                    file_entry = r'/text_files/known/known_interactions4.tsv'
                if input_type =='known5':
                    file_entry = r'/text_files/known/known_interactions5.tsv'
                    
                if input_type =='unknown' or input_type =='random':
                    file_entry = r'/text_files/random/random_interactions.tsv'
                if input_type =='unknown1' or input_type =='random1':
                    file_entry = r'/text_files/random/random_interactions1.tsv'
                if input_type =='unknown2' or input_type =='random2':
                    file_entry = r'/text_files/random/random_interactions2.tsv'                   
                if input_type =='unknown3' or input_type =='random3':
                    file_entry = r'/text_files/random/random_interactions3.tsv'                    
                if input_type =='unknown4' or input_type =='random4':
                    file_entry = r'/text_files/random/random_interactions4.tsv'
                if input_type =='unknown5' or input_type =='random5':
                    file_entry = r'/text_files/random/random_interactions5.tsv'
                    
                if input_type =='FrequentlyViewed':
                    file_entry = r'/text_files/FV.txt'
                if input_type =='negatome':
                    file_entry = r'/text_files/negatome200.csv'
                if input_type =='madhavi_split':
                    file_entry = r'/text_files/Madhavi_split/madhavi_split.txt'
                     
                current_dir = os.getcwd()
                dir_entry = current_dir + file_entry
                with open(dir_entry, 'r') as my_file:
                    reader = csv.reader(my_file, delimiter='\t')
                    for row in reader:
                        list_of_protein_pairs.append(row)
            
            skimmed_angle_protein_pair_list = []
            all_angles = []
            processed_docs_all_proteins = []
            final_protein_word_dict = []

            for protein_pair in list_of_protein_pairs:
                q1 = str(protein_pair[0])
                q2 = str(protein_pair[1])
                both_queries = q1 + '/' + q2 
                time.sleep(0) 
                angle, protein_word_dict, num_docs_processed = main(q1, q2, articles, batch, input_type, outputFileName, dictType, outputType, 
                                                                                        evaluation_mode, stemmed, model, main)
                if angle:
                    if len(protein_word_dict[0]) >= 2:
                        if angle:
                            processed_docs_all_proteins.append(num_docs_processed)
                            angle_protein_word_dicts.append((angle[0], protein_word_dict))
                            final_protein_word_dict.append(protein_word_dict)
                            skimmed_angle_protein_pair_list.append((both_queries, angle[0]))
                            if both_queries not in list_of_queries:
                                list_of_queries.append(both_queries)
                            all_angles.append(angle)
            if articles not in iteration_angle_dict:
                iteration_angle_dict[articles] = all_angles
                angle_score_query_dict[articles] = skimmed_angle_protein_pair_list
            else:
                iteration_angle_dict[articles] += all_angles
                angle_score_query_dict[articles] += skimmed_angle_protein_pair_list 
            
        write_output(list_of_queries, iteration_angle_dict, angle_score_query_dict, angle_protein_word_dicts, input_type, outputFileName, outputType, processed_docs_all_proteins, final_protein_word_dict)
         
    elif iterate == 'no':
        articles_per_cycle.append(num_articles)
        iteration_angle_dict = {}
        angle_score_query_dict ={}
        angle_protein_word_dicts = []
        list_of_queries = []
        processed_docs_all_proteins = []
        
        for articles in articles_per_cycle:
            list_of_protein_pairs = []
            if options.input_type == 'single':
                list_of_protein_pairs.append([q1,q2])
            else:
                if input_type =='50examples':
                    file_entry = r'/text_files/madhavi_example_protein_interactions.txt'  
                         
                if input_type =='known':
                    file_entry = r'/text_files/known/known_interactions.tsv'
                if input_type =='known1':
                    file_entry = r'/text_files/known/known_interactions1.tsv'
                if input_type =='known2':
                    file_entry = r'/text_files/known/known_interactions2.tsv'
                if input_type =='known3':
                    file_entry = r'/text_files/known/known_interactions3.tsv'
                if input_type =='known4':
                    file_entry = r'/text_files/known/known_interactions4.tsv'
                if input_type =='known5':
                    file_entry = r'/text_files/known/known_interactions5.tsv'
                    
                if input_type =='unknown' or input_type =='random':
                    file_entry = r'/text_files/random/random_interactions.tsv'
                if input_type =='unknown1' or input_type =='random1':
                    file_entry = r'/text_files/random/random_interactions1.tsv'
                if input_type =='unknown2' or input_type =='random2':
                    file_entry = r'/text_files/random/random_interactions2.tsv'                   
                if input_type =='unknown3' or input_type =='random3':
                    file_entry = r'/text_files/random/random_interactions3.tsv'                    
                if input_type =='unknown4' or input_type =='random4':
                    file_entry = r'/text_files/random/random_interactions4.tsv'
                if input_type =='unknown5' or input_type =='random5':
                    file_entry = r'/text_files/random/random_interactions5.tsv'
                    
                if input_type =='FrequentlyViewed':
                    file_entry = r'/text_files/FV.txt'
                if input_type =='negatome':
                    file_entry = r'/text_files/negatome200.csv'
                if input_type =='madhavi_split':
                    file_entry = r'/text_files/Madhavi_split/madhavi_split.txt'
                    
                if input_type =='madhavi_split1':
                    file_entry = r'/text_files/Madhavi_split/1.txt'
                if input_type =='madhavi_split2':
                    file_entry = r'/text_files/Madhavi_split/2.txt'
                if input_type =='madhavi_split3':
                    file_entry = r'/text_files/Madhavi_split/3.txt'
                if input_type =='madhavi_split4':
                    file_entry = r'/text_files/Madhavi_split/4.txt'   
                if input_type =='madhavi_split5':
                    file_entry = r'/text_files/Madhavi_split/5.txt'
                if input_type =='madhavi_split_other':
                    file_entry = r'/text_files/Madhavi_split/other.txt'
                                     
                current_dir = os.getcwd()
                dir_entry = current_dir + file_entry
                with open(dir_entry, 'r') as my_file:
                    reader = csv.reader(my_file, delimiter='\t')
                    for row in reader:
                        list_of_protein_pairs.append(row)
            
            skimmed_angle_protein_pair_list = []
            all_angles = []    
            final_protein_word_dict = []  
            for protein_pair in list_of_protein_pairs:
                q1 = str(protein_pair[0])
                q2 = str(protein_pair[1])
                both_queries = q1 + '/' + q2 
                time.sleep(0) 
                angle, protein_word_dict, num_docs_processed = main(q1, q2, articles, batch, input_type, outputFileName, dictType, outputType, 
                                                                    evaluation_mode, stemmed, model, text_file)
                if angle:
                    if len(protein_word_dict[0]) >= 2:
                        if angle:
                            processed_docs_all_proteins.append(num_docs_processed)
                            angle_protein_word_dicts.append((angle[0], protein_word_dict))
                            final_protein_word_dict.append(protein_word_dict)
                            skimmed_angle_protein_pair_list.append((both_queries, angle[0]))
                            list_of_queries.append(both_queries)
                            all_angles.append(angle)
            if articles not in iteration_angle_dict:
                iteration_angle_dict[articles] = all_angles
                angle_score_query_dict[articles] = skimmed_angle_protein_pair_list
            else:
                iteration_angle_dict[articles] += all_angles
                angle_score_query_dict[articles] += skimmed_angle_protein_pair_list 
            write_output(list_of_queries, iteration_angle_dict, angle_score_query_dict, angle_protein_word_dicts, input_type, outputFileName, outputType, processed_docs_all_proteins, final_protein_word_dict)
#known        
#    optparser.add_option("-q", "--q1", default='NEDD4', dest="q1", help="query1")
#    optparser.add_option("-w", "--q2", default='GRIN2A', dest="q2", help="query2")

#uknown
#    optparser.add_option("-q", "--q1", default='SSTR2', dest="q1", help="query1")
#    optparser.add_option("-w", "--q2", default='FABP5', dest="q2", help="query2")

#    default='/home/adam/workspace/TEESinput/example'
if __name__=="__main__":
    from optparse import OptionParser
    optparser = OptionParser(description="Get XML from PubMed")
    optparser.add_option("-q", "--q1", default='MDM2', dest="q1", help="query1")
    optparser.add_option("-w", "--q2", default='TERT', dest="q2", help="query2")
    optparser.add_option("-n", "--n", default=60, dest="num_articles", help="Number of Pubmed Papers to download per gene/protein")
    optparser.add_option("-o", "--outputFileName", default="", dest="outputFileName", help="output file name")
    optparser.add_option("-i", "--input_type", default='known', dest="input_type", help="single or 50examples or known or unknown or random or FrequentlyViewed, madhavi_split, negatome")
    optparser.add_option("-b", "--batch", default="no", dest="batch", help="yes or no")
    optparser.add_option("-d", "--dict", default="all", dest="dictType", help="all or protein")
    optparser.add_option("-t", "--outputType", default="tab", dest="outputType", help="'normal'= proteins/score/dict or 'tab'= csv #articles/angles")
    optparser.add_option("-r", "--iterate", default="no", dest="iterate", help="yes or no --- to iterate is to output averages every 5 angles")
    optparser.add_option("-a", "--iteration_type", default="docs", dest="iteration_type", help="docs or list_len")
    optparser.add_option("-e", "--evaluation", default="no", dest="evaluation_mode", help="yes or no --- evaluation blocks downloading more papers")
    optparser.add_option("-s", "--stemmed", default="no", dest="stemmed", help="yes or no for stemming")
    optparser.add_option("-m", "--mod", default='REL11 EPI11 ID11', dest="model", help="GE11, REL11, EPI11, ID11")
    optparser.add_option("-f", "--txt", default='no', dest="text_file", help="yes or no -- whether input is txt file or pmids")
    (options, args) = optparser.parse_args()
    
    index(options.q1, options.q2, options.num_articles, options.batch, options.input_type, options.outputFileName, options.dictType, options.outputType, options.iterate,
           options.evaluation_mode, options.iteration_type, options.stemmed, options.model, options.text_file)
    
        
