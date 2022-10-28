from urllib.parse import unquote, quote
from pathlib import Path
from argparse import ArgumentParser
from copy import deepcopy 
import sys
import json
import mainlz4

#from os import system
#system('mode con:cols=140 lines=2500')

def count_substr(text, substrs):
    return sum(s in text.casefold() for s in set(map(str.casefold, substrs)))
    
def rm_quotes_path(string):
    return Path(string.replace("\"", ""))

def rootURI_correction(rootURI, current_path, offset=-2):
    new_path = quote("jar:file:///" + current_path.replace('\\','/') + rootURI.split('/')[offset] + '/', safe='/\\:@!%={}')
    return new_path

def path_correction(patch, current_path, offset=-1):
    new_path = unquote(current_path + patch.split('\\')[offset])
    return new_path

def parser2(ddict, *correction_dataset):
    for correction_data in correction_dataset:
        data_type = str(type(ddict))
        if 'dict' in data_type:
            for key, data in ddict.items():
                if 'str' in str(type(key)) and correction_data['search_key'] in key:
                    #print(str(type(ddict[key])) + '\n  ' + str(key) + ' : \n' + str(ddict[key]))
                    for sign, sign_data in correction_data['signature'].items():
                        if ddict[key] != None and count_substr(ddict[key], correction_data['signature'][sign]) >= len(correction_data['signature'][sign]): 
                            ddict[key] = correction_data['correction_func'](ddict[key], sign)
                            #print(ddict[key])
                    #print('\n\n')
                    continue
                parser2(data, correction_data)
        if 'list' in data_type:
            for key in range(len(ddict)):
                parser2(ddict[key], correction_data)

if __name__ == '__main__':
    
    parser = ArgumentParser(prog='myprogram', usage='-profile <profile dir> -app <app path>', epilog = 'sample: %s -app "C:\\Program Files\\Mozilla Firefox\\firefox.exe" -profile "C:\\profiles\\Default"' % Path(sys.argv[0]).name)
    parser.add_argument('-app', type=rm_quotes_path, help='Path to firefox.exe or any firefox-based browser')
    parser.add_argument('-profile', type=rm_quotes_path, help='Path to firefox profile')
    args = parser.parse_args()
    if (args.profile == None or args.app == None): 
        parser.print_help()
        sys.exit()  
    
    #app_name = str(Path(args.app).name)
    app_dir = str(args.app.parents[0])
    profile_dir = str(args.profile)
    
    addonStartup_path = profile_dir + '\\' + 'addonStartup.json.lz4'
    extensions_path = profile_dir + '\\' + 'extensions.json'
    
    try:
        lz4_file = open(addonStartup_path, 'rb')
        addonStartupdata = mainlz4.decompress(lz4_file)
        lz4_file.close()
    except IOError as e:
        print("Unable to read '%s': %s" % (addonStartup_path, e), file=sys.stderr)
        raise SystemExit(1)
        
        
    try:
        extensions_file = open(extensions_path, 'r', encoding='utf-8')
        extensionsdata = json.load(extensions_file)
        extensions_file.close()
    except IOError as e:
        print("Unable to read '%s': %s" % (extensions_path, e), file=sys.stderr)
        raise SystemExit(1)
    
    rootURI_correction_data = {
            'search_key' : 'rootURI',
            'signature': {
                app_dir + '\\browser\\features' + '\\' : ['features', 'browser'], 
                profile_dir + '\\extensions' + '\\' : ['/extensions/']
            },
            'correction_func': rootURI_correction
        }
        
    path_correction_data = {
            'search_key' : 'path',
            'signature': {
                app_dir + '\\browser\\features' + '\\' : ['features', 'browser'], 
                profile_dir + '\\extensions' + '\\' : ['\\extensions\\']
            },
            'correction_func': path_correction
        }
        
    path__correction_data2 = {
            'search_key' : 'path',
            'signature': {
                app_dir + '\\browser\\features' : ['features', 'browser'], 
                profile_dir + '\\extensions' : ['\\extensions']
            },
            'correction_func': lambda y, x: x,
        }
    
    addonStartupdata2 = deepcopy(addonStartupdata)
    extensionsdata2 = deepcopy(extensionsdata)

    parser2(addonStartupdata2, rootURI_correction_data, path__correction_data2)
    parser2(extensionsdata2, rootURI_correction_data, path_correction_data)

    if all(addonStartupdata[k] == v for k, v in addonStartupdata2.items() if k in addonStartupdata) and all(extensionsdata[k] == v for k, v in extensionsdata2.items() if k in extensionsdata):
        print('All data match')
        print('No editing required')
    else:
        print('Data mismatch')
        print('Write...')
        try:
            lz4_file = open(addonStartup_path, 'wb')
            lz4_binary = mainlz4.compress(json.dumps(addonStartupdata2))
            lz4_file.write(lz4_binary)
            lz4_file.close()
        except IOError as e:
            print("Unable to write '%s': %s" % (addonStartup_path, e), file=sys.stderr)
            raise SystemExit(1)
        
        try:
            extensions_file = open(extensions_path, 'wb')
            extensions_file.write(json.dumps(extensionsdata2, indent=4,ensure_ascii=False).encode('utf-8'))
            extensions_file.close()
        except IOError as e:
            print("Unable to write '%s': %s" % (extensions_path, e), file=sys.stderr)
            raise SystemExit(1)   
    
    print('End of program')