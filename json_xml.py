import os
import json
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
from xml.dom.minidom import parseString
 
categorys = ['car', 'bus', 'person', 'bike', 'truck', 'motor', 'train', 'rider', 'traffic sign', 'traffic light']
 
def parseJson(jsonFile):

    objs = []
    obj = []
    f = open(jsonFile)
    info = json.load(f)
    objects = info['frames'][0]['objects']
    for i in objects:
        if (i['category'] in categorys):
            obj.append(int(i['box2d']['x1']))
            obj.append(int(i['box2d']['y1']))
            obj.append(int(i['box2d']['x2']))
            obj.append(int(i['box2d']['y2']))
            obj.append(i['category'])
            objs.append(obj)
            obj = []
    
    return objs
 
 
class PascalVocWriter:
 
    def __init__(self, foldername, filename, imgSize, databaseSrc='Unknown', localImgPath=None):

        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
 
    def prettify(self, elem):

        xml = ElementTree.tostring(elem)
        dom = parseString(xml)
        
        prettifyResult = dom.toprettyxml('    ')
        return prettifyResult
 
    def genXML(self):

        
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None or \
                len(self.boxlist) <= 0:
            return None
 
        top = Element('annotation')  
        folder = SubElement(top, 'folder')
        folder.text = self.foldername  
 
        filename = SubElement(top, 'filename')  
        filename.text = self.filename  
 
        localImgPath = SubElement(top, 'path')  
        localImgPath.text = self.localImgPath  
 
        source = SubElement(top, 'source')  
        database = SubElement(source, 'database')  
        database.text = self.databaseSrc  
 
        size_part = SubElement(top, 'size')  
        width = SubElement(size_part, 'width')  
        height = SubElement(size_part, 'height')  
        depth = SubElement(size_part, 'depth')  
        width.text = str(self.imgSize[1])  
        height.text = str(self.imgSize[0])  
        if len(self.imgSize) == 3:  
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'
 
        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top
 
    def addBndBox(self, xmin, ymin, xmax, ymax, name):

        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        self.boxlist.append(bndbox)
 
    def appendObjects(self, top):

        for each_object in self.boxlist:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            name.text = str(each_object['name'])
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            truncated.text = "0"
            difficult = SubElement(object_item, 'Difficult')
            difficult.text = "0"
            bndbox = SubElement(object_item, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(each_object['xmin'])
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(each_object['ymin'])
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(each_object['xmax'])
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(each_object['ymax'])
 
    def save(self, targetFile=None):

        root = self.genXML()
        self.appendObjects(root)
        if targetFile is None:
            full_path = os.path.join(self.foldername, self.filename + '.xml')
        else:
            full_path = targetFile
        if not os.path.isdir(self.foldername):
            os.makedirs(self.foldername)
        with open(full_path, 'w') as out_file:
            prettifyResult = self.prettify(root)
            out_file.write(prettifyResult)

 
class PascalVocReader:
    def __init__(self, filepath):
        self.shapes = []
        self.filepath = filepath
        self.parseXML()
    def getShapes(self):
        return self.shapes
    def addShape(self, label, bndbox):
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, points, None, None))
    def parseXML(self):
        assert self.filepath.endswith('.xml'), "Unsupport file format"
        parser = etree.XMLParser(encoding='utf-8')
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        filename = xmltree.find('filename').text
        for object_iter in xmltree.findall('object'):
            bndbox = object_iter.find("bndbox")
            label = object_iter.find('name').text
            self.addShape(label, bndbox)
        return True
 
 
def main(srcDir, dstDir):
    i = 1
    for dirpath, dirnames, filenames in os.walk(srcDir):
        for filepath in filenames:
            fileName = os.path.join(dirpath, filepath)
            print(fileName)
            print("processing: {}, {}".format(i, fileName))
            i = i + 1
            xmlFileName = filepath[:-5]  
            
            objs = parseJson(str(fileName))
            
            if len(objs):
                tmp = PascalVocWriter(dstDir, xmlFileName, (720, 1280, 3), fileName)
                for obj in objs:
                    tmp.addBndBox(obj[0], obj[1], obj[2], obj[3], obj[4])
                tmp.save()
            else:
                print(fileName)
 
 
if __name__ == '__main__':
    srcDir = 'bdd100/labels'
    dstDir = 'bdd100/labels-xml'
    main(srcDir, dstDir)
