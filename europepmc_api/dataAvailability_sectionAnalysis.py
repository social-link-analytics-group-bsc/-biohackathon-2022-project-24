#!/usr/local/bin python
'''
#!/usr/bin/env python
#!/homes/avenkat/.localpython/bin python2.7
Created on 19 Aug 2016

@author: Aravind Venkatesan, avenkat@ebi.ac.uk
@version: 1.0
@summary: The script parses OA articles in XML and checks of the Data Availability section. The script generates a TSV file with the <Tag> data availability section was found
@param: The scripts requires as input, a) path to the directory of input xml.gz files b) path to output directory. 

'''
import sys
#sys.path.append("/media/sf_H_DRIVE/workspace/pubmed_parser-master/pubmed_parser")
import pprint
import re
import glob
import os
import gzip
import xml.etree.ElementTree as etree
from lxml import etree as ET 
from io import StringIO
#from lxml.etree import ElementTree
from datetime import date
from subprocess import Popen, PIPE, STDOUT
from libxml2mod import parent
#import nltk

pp = pprint.PrettyPrinter(indent=4)

def iterparent(tree):
    return_dict = {}
    for parent in tree.getiterator():
        for child in parent:
            return_dict[child] = parent
    return return_dict


def sectionTagger(perl_script_path, xmlsegment): #, split_pattern
    perlLauncer = ['perl', perl_script_path]
    #parser = ET.XMLParser(recover=True)
    #tree = ET.fromstring(xmlsegment, parser)
    std_in = ET.tostring(xmlsegment)
    execute_cmd = Popen(perlLauncer, stdin=PIPE, stdout=PIPE, stderr=PIPE) #, stderr=subprocess.PIPE, shell=True
    output = execute_cmd.communicate(input=std_in)#[0]#pp.pprint(taggedSection.communicate()[0])
    taggedSection = output[0]
    std_out = output[1]
    #print std_out
    return taggedSection
    #print taggedSection


def getFrequnceCount(xmlsegment, metrics_ds):
    #pp = pprint.PrettyPrinter(indent=4)
    parser = ET.XMLParser(recover=True)#.XMLParser(encoding="utf-8")
    dataAvail = re.compile(r'Data Availability|Data \w+ [Aa]vailability|\w+ [Dd]ata [Aa]vailability|Availability \w+ [Dd]ata', flags=re.M)
#     dataAvail_v2 = re.compile(r'[Dd]ata \w+ [Aa]vailability', flags=re.I|re.M)
#     dataAvail_v3 = re.compile(r'\w+ [Dd]ata [Aa]vailability', flags=re.I|re.M)
#     dataAvail_v4 = re.compile(r'[Aa]vailability \w+ [Dd]ata', flags=re.I|re.M)
    root = ET.fromstring(xmlsegment, parser)# etree.fromstring(xmlsegment) tree = ET.parse(xmlsegment, parser)#
    #root = tree.getroot()
    #parent_map = dict((c, p) for p in root.getiterator() for c in p)
    #parent_map = iterparent(root)
    if re.search(r'\>[Dd]ata [Aa]vailability\<|\>[Dd]ata \w+ [Aa]vailability\<|\>\w+ [Dd]ata [Aa]vailability\<|\>[Dd]ata [Aa]vailability \w+\<|\>[Aa]vailability \w+ [Dd]ata\<|\>[Aa]vailability \w+ [Dd]ata \w+*\<', xmlsegment):
        metrics_ds['Articles with section'] += 1    
#     if re.search(r'\>[Dd]ata [Aa]vailability\<', xmlsegment):
#         metrics_ds['Articles with section'] += 1    
#     elif re.search(r'\>[Dd]ata \w+ [Aa]vailability\<', xmlsegment):
#         metrics_ds['Articles with section'] += 1
#     elif re.search(r'\>\w+ [Dd]ata [Aa]vailability\<', xmlsegment):
#         metrics_ds['Articles with section'] += 1
#     elif re.search(r'\>[Aa]vailability \w+ [Dd]ata\<', xmlsegment):
#         metrics_ds['Articles with section'] += 1
        
            
    if root != None:
        metrics_ds['Total articles'] += 1
#         #pmid = root.xpath('front/article-meta/article-id')#[0].text [@pub-id-type="pmid"]
#         #print pmid
#         for node in root.iterdescendants('SecTag'): #.iterdescendants('SecTag')
            #for children in parent:
                
#                 for node in children.iter():
#                     if node.text:
#                         #Searching for Section heading
#                         if dataAvail.match(node.text):
#                             if children.tag == 'SecTag':
#                                 if children.attrib['type'] not in metrics_ds:
#                                     metrics_ds[children.attrib['type']] = 1
#                                 else:
#                                     metrics_ds[children.attrib['type']] += 1     
#                             else:
#                                 new_tag = "%s, %s" % (str.lower(parent.tag), str.lower(children.tag)) 
#                                 if new_tag not in metrics_ds: #str.upper(parent.tag)
#                                     metrics_ds[new_tag] = 1 #str.upper(parent.tag)
#                                 else:
#                                     metrics_ds[new_tag] += 1 #str.upper(parent.tag)                                                         
#                         else: 
#                             continue
#                     else:
#                         continue
    else:
        print "Encountered an empty xml segment"

    return metrics_ds                

def getSectionName(xmlsegment):
    parser = ET.XMLParser(recover=True)#.XMLParser(encoding="utf-8")
    return_text = list()
    dataAvail = re.compile(r'[Dd]ata [Aa]vailability|[Dd]ata \w+ [Aa]vailability|\w+ [Dd]ata [Aa]vailability|[Aa]vailability \w+ [Dd]ata', flags=re.M)
    if xmlsegment != None:
        root = ET.fromstring(xmlsegment, parser)    
        for node in root.iterdescendants():
            if node.text:
                if dataAvail.match(node.text):
                    found = str(node.tag)+ ": " + node.text
                    return_text.append(found)
                elif dataAvail.search(node.text):
                    #found = str(node.tag)+ ": " + str(node.text)
                    return_text.append(node.text)
            else:
                continue
        return return_text
    else:
        print "Encountered an empty xml segment"


def fetchRawXMLTags(xmlsegment, met_ds):
    if xmlsegment != None:
        root = xmlsegment #ET.fromstring(string_seg, parser)
        counter = 0
        #print root 
        for parent in root:
            #print parent.tag
            #if parent.tag != 'front':
                #met_ds[parent.tag] = {}                
            for children in parent:
                for node in children.iterchildren():#children(): descendants()
                    #for subnode in node.iterchildren():
                    if node.tag == 'title' or node.tag == 'label':
                        if node.text:
                            if parent.tag not in met_ds:
                                met_ds[parent.tag] = {}
                            if parent.tag in met_ds:
                                if node.text not in met_ds[parent.tag]:
                                    met_ds[parent.tag][node.text] = 1
                                if node.text in met_ds[parent.tag]:
                                    met_ds[parent.tag][node.text] += 1
                        else:
                            continue
                
                    else:
                        continue    
                                                                                                  
        return met_ds                     
    else:
        print "Encountered an empty xml segment"


def fetchTaggedXMLTags(xmlsegment, met_ds):
    parser = ET.XMLParser(recover=True)
    if xmlsegment != None:
        print ".......XML start......."
        root = ET.fromstring(xmlsegment, parser)
        counter = 0
        #print root 
        #find_text = ET.XPath("//title", smart_strings=False) #/text()        
        for parent in root:
            if parent.iter('SecTag'):
                for children in parent.iter('SecTag'):
                    tagName = children.get('type')
                    #mid_dict = {}                
                    for node in children.iterchildren():
                        for subnode in node.iterchildren():
                            #print subnode.tag
                            #inner_dict = {}
                            if subnode.tag == 'title' or subnode.tag == 'label':
                                if subnode.text:
                                    if parent.tag not in met_ds:
                                        met_ds[parent.tag] = {}
                                    if parent.tag in met_ds:
                                        if tagName not in met_ds[parent.tag]:
                                            met_ds[parent.tag][tagName] = {}
                                        if tagName in met_ds[parent.tag]:
                                            if subnode.text not in met_ds[parent.tag][tagName]:
                                                met_ds[parent.tag][tagName][subnode.text] = 1
                                            if subnode.text in met_ds[parent.tag][tagName]:
                                                met_ds[parent.tag][tagName][subnode.text] += 1
                                else:
                                    continue
                         
                            else:
                                continue                                  
                        
            else:
                continue                                          
        return met_ds
    else:
        print "Encountered an empty xml segment"

def fetchOtherTags(xmlsegment, othr_ds, freq_count):
    parser = ET.XMLParser(recover=True)
    if xmlsegment != None:
        #print ".......XML start......."
        root = ET.fromstring(xmlsegment, parser)
        #print root 
        #find_text = ET.XPath("//title/text()", smart_strings=False) #/text()
        #find_text_2 = root.xpath("//*[re:test(local-name(), '^title|^label')]", namespaces={'re': "http://exslt.org/regular-expressions"}) #/text()
        #texts = find_text(root)
        #for text in find_text_2:
            #if text.text:
                #print text.tag, text.text#pp.pprint(find_text_2)
         
        for parent in root:
            for children in parent.iterchildren():
                if children.tag != 'SecTag':
                    for node in children.iterdescendants():#descendants
                            if node.tag == 'title' or node.tag == 'label':
                                if node.text:
                                    if node.text not in freq_count:
                                        freq_count[node.text] = 1
                                    if node.text in freq_count:
                                        freq_count[node.text] += 1
                                    
                                    path = [ancestor.tag for ancestor in node.iterancestors()]
                                    abs_path = ":".join(reversed(path))
                                    #print abs_path
                                    #print "\t" + node.text
                                    if abs_path not in othr_ds:
                                        othr_ds[abs_path] = {}
                                    if abs_path in othr_ds:
                                        if node.text not in othr_ds[abs_path]:
                                            othr_ds[abs_path][node.text] = 1
                                        if node.text in othr_ds[abs_path]:
                                            othr_ds[abs_path][node.text] += 1
                else:
                    continue
                                #print 
        #return met_ds
    else:
        print "Encountered an empty xml segment"
    


def main(agrv):
    
    input_dir = ''
    output_dir = ''
    section_metrics = {"Articles with section": 0, "Total articles": 0} #"Section not found:": 0, "Present as free text:": 0, 
    occurence_ds = {}
    journal_dict = {} 
    title_ds = dict()
    title_count = dict()
    #other_tags = {'title': '', 'count': 0, 'path': list()}
    xml_type_flag = False
    perlSectionTaggerPath = '/nfs/misc/literature/lit-textmining-pipelines/bin/SectionTagger_XML_inline.perl' 
    if os.path.isdir(agrv[0]):
        input_dir = agrv[0]
    #elif os.path.isdir(agrv[0]):
    else:
        raise TypeError("First argument not a directory: %s" % agrv[0])
        sys.exit(1)
    if os.path.isdir(agrv[1]):
        output_dir = agrv[1]
    else:
        raise TypeError("Second argument not a directory: %s" % agrv[1])
        sys.exit(1)

    pattern_split = re.compile(r'<!DOCTYPE .+$', flags=re.MULTILINE)
    article_delimiter = '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD v1.1d2 20140930//EN" "JATS-archivearticle1.dtd">'

    articles = glob.glob('%s*.xml.gz' % input_dir)
    
    for article in articles:
        xmlgzip = gzip.open(article, mode="rb", compresslevel=9)
        
        #wrting tagged section
#         fileName = os.path.splitext(os.path.basename(article))[0]#basename(article)
#         outFileName = "sectTagged_" + fileName + ".gz"
#         compressedFile = os.path.join(output_dir, outFileName)
#         compress = gzip.open(compressedFile, mode="wb", compresslevel=9)
#          
        #wrting section names
#         section_name_file = "OA_DataAvailability_sectionNames_" + str(date.today()) + ".txt"
#         out_secName_file = os.path.join(output_dir, section_name_file)
#         nameFH = open(out_secName_file, "wb")
#         
        datacontent = xmlgzip.read()
        if len(datacontent) != 0:
            if pattern_split.match(datacontent):
                xml_type_flag = True
                xmllist = list()
                xmllist = re.split(pattern_split, datacontent)
                xmllist.pop(0)
                print len(xmllist)
                for xmlstring in xmllist:
                    xmlstring.strip(' ')
                    #fetchTaggedXMLTags(xmlstring, title_ds)
                    fetchOtherTags(xmlstring, title_ds, title_count)
            else:
                parser = ET.XMLParser(recover=True)#.XMLParser(encoding="utf-8")
                tree = ET.fromstring(datacontent, parser)
                print len([ child.tag for child in tree.iterchildren()]) 
                for segment in tree:
                    fetchRawXMLTags(segment, title_ds)
#                 #occurence_metrics(xmlstring, occurence_ds, journal_dict) 
#                taggedSection = sectionTagger(perlSectionTaggerPath, segment)
#                 #print taggedSection
#                 if taggedSection != "":
#                     compress.write("%s\n" % article_delimiter)
#                     compress.write(taggedSection)
# #                 #getFrequnceCount(taggedSection, section_metrics) #section_metrics =
#                     texts = getSectionName(taggedSection)
#                pp.pprint(texts)
#                     for text in texts:
#                         nameFH.write("%s\n\n" % text.encode("utf-8"))
#                 else:
#                     continue 
#                 
        else:
            print "Empty file: %s" % article             
        xmlgzip.close()
#         compress.close()
#         nameFH.close()
    #pp.pprint(title_ds)
    
    #data_avail_file = "OA_DataAvailabilityAnalysis_" + str(date.today()) + ".tab"
    
    # Write Fetch Tag Names
    tn_with_ST = "OA_title_with_ST_" + str(date.today()) + ".tab"
    tn_without_ST = "OA_title_without_ST_" + str(date.today()) + ".tab"
    title_other = "OA_title_Other_" + str(date.today()) + ".tab"
    title_counter = "OA_title_count_OtherT_" + str(date.today()) + ".tab"   
    #output_TN_file = None
    
    if xml_type_flag == True:
        output_TN_file = os.path.join(output_dir, title_other)
        out_title_count = os.path.join(output_dir, title_counter)
        with open(output_TN_file, "wb") as tnSTFH:
            tnSTFH.write("Path\ttitle\tcounts\n")
            for key1 in title_ds:
                for key2 in title_ds[key1]:
                    #for key3 in title_ds[key1][key2]:
                    tnSTFH.write('%s\t%s\t%s\n' % (key1, key2.encode("utf-8"), str(title_ds[key1][key2]))) #key3, str(title_ds[key1][key2][key3]
        
        with open(out_title_count, "wb") as countFH:
            countFH.write("title\tcounts\n")
            for key, value in title_count.items():
                countFH.write('%s\t%s\n' % (key.encode("utf-8"), str(value)))
    else:
        output_TN_file = os.path.join(output_dir, tn_without_ST)
        with open(output_TN_file, "wb") as tnFH:
            tnFH.write("Parent_Tag\ttitle\tcounts\n")
            for key1 in title_ds:
                for key2 in title_ds[key1]:
                    tnFH.write('%s\t%s\t%s\n' % (key1, key2.encode("utf-8"), str(title_ds[key1][key2]))) 
            
#             for key1, value1 in sorted(title_ds.items()):
#                 for key2, value2 in sorted(value1.items()):
#                     tnFH.write('%s\t%s\t%s\n' % (key1, key2.encode("utf-8"), str(value2))) 
         
#    out_metrics_file = os.path.join(output_dir, data_avail_file)
#    with open(out_metrics_file, "wb") as outFH:   
#        outFH.write("Section\tOccurrence\n")
#        for key, value in sorted(section_metrics.items()):
#             outFH.write('%s\t%s\n' % (key, str(value))) #final_dict[key]
    
        
    
if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print "Usage: python dataAvailability_sectionAnalysis.py <inputDirectory> <outputDirectory>"
        sys.exit(1)
    else:
        main(sys.argv[1:])
