#!/usr/bin/python

import argparse
import sys
import csv
import os
import shutil
import hashlib
import codecs

sizes = { '1': 'c5lFSoDAAAAKgABAA', '2.5': 'c5lFSoEAAAAKgABAA',
          '5': 'c9lFSoFAAAAKgABAQ', '10': 'dBlFSoGAAAAKgABAA',
          '15': 'dBlFSoHAAAAKgABAA', '20': 'dFlFSoIAAAAKgABAQ',
          '30': 'eF1FSoJAAAAKgABAQ'
}

# Given the file prefix, where images are kept, and a name from the
# CSV, this function uses some heuristics to find the correct image
# name.  An exact match is not needed.  For instance, If there is a
# monster "Doodle",  it will accept a find for "Greater Doodle".
def find(prefix, name):
    fdir = prefix + name + '.png'
    if (os.path.exists(fdir)):
        return [ fdir, '' ]
    # The previous was an exact match. Heuristics start here.
    for type in { 'Angel', 'Demon', 'Devil', 'Rakshasa', 'Gremlin', 'Protean', 'Daemon',
                  'Qlippoth', 'Psychopomp', 'Agathion', 'Azata', 'Aeon', 'Dinosaur',
                  'Daemon', 'Fleshwarp', 'Kyton', 'Oni', 'Div', 'Nightshade', 'Kami',
                  'Empyreal Lord', 'Megafauna', 'Lycanthrope', 'Inevitable', 'Herd Animal',
                  'Vampire', 'Asura', 'Marsupial', 'Demon Lord', 'Genie', 'Familiar',
                  'Fish', 'House Spirit', 'Dolphin', 'Bat', 'Lurking Ray', 'Cat', 'Vampire',
                  'Sphinx', 'Titan', 'Great Old One', 'Ape', 'Parasite', 'Spider',
                  'Lizard', 'Snake', 'Primate', 'Kaiju', 'Demodand' }:
        fdir = prefix + type + ', ' + name + '.png'
        if (os.path.exists(fdir)):
            return [ fdir, '' ]
    part = name.split(' ')
    if (len(part) > 2):
        if (part[0] in { 'Very', 'Mature', 'Young', 'Great' } and
            part[1] in { 'Young', 'Old', 'Adult', 'Wyrm' }):
            fdir = prefix + 'Dragon, ' + part[-2] + '.png'
            if (os.path.exists(fdir)):
                return [ fdir, part[0] + ' ' + part[1] ]
    if (len(part) > 1):
        fdir = prefix + '{}, {}.png'.format(' '.join(part[1:]), part[0])
        if (os.path.exists(fdir)):
            return [ fdir, '' ]
        if (part[0] in { 'Juvenile', 'Wyrmling', 'Ancient', 'Adult', 'Young', 'Old', 'Wyrm' }):
            fdir = prefix + 'Dragon, ' + part[-2] + '.png'
            if (os.path.exists(fdir)):
                return [ fdir, part[0] ]
        if (part[0] in { 'Small', 'Large', 'Greater', 'Medium', 'Huge', 'Elder' } and
            part[-1] == 'Elemental'):
            fdir = prefix + 'Elemental, ' + part[-2] + '.png'
            if (os.path.exists(fdir)):
                return [ fdir, part[0] ]
        fdir = prefix + '{}, {}.png'.format(' '.join(part[2:]), ' '.join(part[0:2]))
        if (os.path.exists(fdir)):
            return [ fdir, '' ]
    part = name.split(', ')
    if (len(part) > 1 and (part[1] in { '1st form', '2nd form' })):
        fdir = prefix + "Lycanthrope, " + part[0] + '.png'
        if (os.path.exists(fdir)):
            return [ fdir, '' ]

    return [ '', '' ]

parser = argparse.ArgumentParser(description='''

Create MT tokens from a CSV table. For each line it will look for an
image in the image directory. The 'Name' column will be used as GM
name, as file name and to look for the image. (The Name of the token
will be encoded.)  All other columns will be mapped to properties.
The 'Source' column in the CSV file contains a subdirectory in this
image directory. A 'Skills' column is treated as comma-separated
sublist that is split and expected to contain 'name value' pieces. A
value will have a leading '+' removed.  A 'Space' column can map 1,
2.5, 5, 10, 15, 20, 30 to the size range TINY - COLOSSAL. (Other
values would lead to errors.) The name of each parsed lines are
printed. If you need other heuristics to find the image name from the
token name, adapt the "find" function in the script.  Note that the
Token format is not an official API. This script is tested against
version 1.9.4.

''')
parser.add_argument('csvfile',help='dataset to process')
parser.add_argument('imgdir',help='image directory where all token images are located. Tokens will also be placed there.')
parser.add_argument('-s', '--sizes', action='store_true', help='Map "Space" to Maptool token size')
args = parser.parse_args()

# opening the CSV file
with open(args.csvfile, mode ='r') as file:
    # reading the CSV file
    csvFile = csv.DictReader(file)
    
    for lines in csvFile:
        name = lines['Name']
        [ fdir, cat ] = find(args.imgdir + '/' + lines['Source'] + '/', name)
        if (fdir != ''):
            print(name )

            shutil.rmtree('tmp', True)
            os.mkdir('tmp')
            os.mkdir('tmp/assets')

            pf = open('tmp/properties.xml', mode = 'w')
            pf.write('<map><entry><string>version</string><string>1.9.3</string></entry></map>')
            pf.close()

            with open(fdir, mode = 'rb') as df:
                id = hashlib.md5(df.read()).hexdigest()
            cf = open('tmp/content.xml', mode = 'w')
            cf.write('<net.rptools.maptool.model.Token><imageAssetMap><entry><null/><net.rptools.lib.MD5Key>')
            cf.write('<id>{}</id>'.format(id))
            cf.write('</net.rptools.lib.MD5Key></entry></imageAssetMap><sizeScale>1.0</sizeScale>')
            cf.write('<snapToScale>true</snapToScale><snapToGrid>true</snapToGrid>')
            cf.write('<ownerType>0</ownerType><tokenShape>CIRCLE</tokenShape><tokenType>NPC</tokenType><layer>TOKEN</layer>')
            if (args.sizes):
                cf.write('<sizeMap><entry><java-class>net.rptools.maptool.model.SquareGrid</java-class><net.rptools.maptool.model.GUID>')
                cf.write('<baGUID>fwABA{}==</baGUID>'.format(sizes[lines['Space']]))
            cf.write('</net.rptools.maptool.model.GUID></entry></sizeMap>')
            cf.write('<gmName>{}</gmName><name>{}</name><propertyType>Basic</propertyType><propertyMapCI><store>'.format(name, codecs.encode(name, 'rot_13')))
            for k in lines.keys():
                if (k != 'Name'):
                    cf.write('<entry><string>{}</string><net.rptools.CaseInsensitiveHashMap_-KeyValue>'.format(k))
                    cf.write('<key>{}</key><value class="string">{}</value>'.format(k, lines[k]))
                    cf.write('</net.rptools.CaseInsensitiveHashMap_-KeyValue></entry>')
            for skl in lines['Skills'].split(', '):
                nv = skl.split(' ')
                if (len(nv) > 1):
                    cf.write('<entry><string>{}</string><net.rptools.CaseInsensitiveHashMap_-KeyValue>'.format(nv[0]))
                    cf.write('<key>{}</key><value class="string">{}</value>'.format(nv[0], (nv[1][1:]  if (nv[1].startswith('+')) else nv[1])))
                    cf.write('</net.rptools.CaseInsensitiveHashMap_-KeyValue></entry>')
            cf.write('</store></propertyMapCI></net.rptools.maptool.model.Token>')
            cf.close()

            af = open('tmp/assets/' + id, mode = 'w')
            af.write('<net.rptools.maptool.model.Asset><id><id>{}</id></id><name>{}</name>'.format(id, name))
            af.write('<extension>png</extension><image/></net.rptools.maptool.model.Asset>')
            af.close()

            shutil.copyfile(fdir,'tmp/assets/{}.png'.format(id))
            shutil.make_archive(fdir + '.rptok', 'zip', 'tmp')
            shutil.rmtree('tmp')
            shutil.move(fdir + '.rptok.zip', fdir.replace('.png',(', ' + cat) if (cat != '') else '') + '.rptok')
