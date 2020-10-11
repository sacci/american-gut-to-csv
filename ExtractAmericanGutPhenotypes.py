# Edit path in main function with name of directory with all .xml files.
# .xml files must be formatted accordingly to the model.

import os
import xml.etree.ElementTree as ET
import pandas as pd
from lxml import etree


# Build list of dictionary (key=TAG, value=VALUE). This list will be then transformed into a DF
def buildDF(xroot):
    rows = []
    # Get all sample dataframe data in current xml file

    samples = xroot.findall('SAMPLE/SAMPLE_ATTRIBUTES')
    for sample in samples:
        values = [value.text for value in sample.findall('SAMPLE_ATTRIBUTE/VALUE')]
        tags = [tag.text for tag in sample.findall('SAMPLE_ATTRIBUTE/TAG')]
        sampleDict = dict(zip(tags, values))
        rows.append(sampleDict)
    df = pd.DataFrame.from_records(rows)

    # Save run ids of samples of this .xml
    runIds = [ids.text for ids in xroot.findall('SAMPLE/SAMPLE_LINKS/SAMPLE_LINK/XREF_LINK/ID') if ids.text.startswith('ERR')]
    df.insert(0, "Run", runIds)

    return df


# Build .csv file by opening each .xml and extracting the phenotypes. 
def combineXmlIntoCsv(path):
    dfs = []
    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)

        # Check if xml has empty VALUES and remove them
        dom = etree.parse(fullname)
        root = dom.getroot()
        tags = root.xpath('/SAMPLE_SET/SAMPLE/SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE/TAG')
        for atrs in tags:
            parentNode = atrs.getparent()

            if len(parentNode.xpath('./VALUE')) < 1:
                parentNode.getparent().remove(parentNode)
       
        df = buildDF(root)

        # Original File
        df.insert(1, "XML File", filename)

        dfs.append(df)
        print('%s has been processed' %fullname)

    print('Combining .xml files (this may take a while...)')
    df_combination = pd.concat(dfs)
    df_combination.to_csv('phenotypes.csv', index=False, sep=',', date_format='%s')
    print('Done.')


if __name__ == '__main__':
    print("This script combines the .xml phenotype files from American Gut Project into a single .csv file.")
    xmlDirectory = input("Enter the path to the directory with all the .xml files (or the name of the directory, if it's inside the directory of this script): ")
    combineXmlIntoCsv(xmlDirectory)