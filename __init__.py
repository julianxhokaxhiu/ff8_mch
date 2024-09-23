#*****************************************************************************#
#    Copyright (C) 2024 Shunsq                                                #
#    Copyright (C) 2024 Julian Xhokaxhiu                                      #
#                                                                             #
#    This file is part of FF8 MCH                                             #
#                                                                             #
#    FF8 MCH is free software: you can redistribute it and/or modify          #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License            #
#                                                                             #
#    FF8 MCH is distributed in the hope that it will be useful,               #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#*****************************************************************************#

"""***********************************************
*********Fieldmodel blender script***************
**********************************************"""
import os,bpy.path,bpy.ops,bmesh,math
from os.path import basename,dirname
from mathutils import Vector, Matrix,Euler

bl_info = {
    "name": "FF8 MCH Field Models",
    "author": "Shunsq,Julian Xhokaxhiu",
    "blender": (4, 2, 0),
    "version": (0, 1, 0),
    "location": "File > Import > FF8 Field Model (.mch)",
    "description": "Import field models from FF8",
    "category": "Import-Export"
}

global MAX_SIZE,MAX_TEXSIZE,MAX_ANGLE#max angle is 2pi
MAX_SIZE=0x1000
MAX_TEXSIZE=0x100#0x800#2048 *2048 upsacaled texture
MAX_ANGLE=0x1000#180deg
UPSCALE=1#0x100 for upscale

#MCH_TO_BLEND
def Empty_dir(directory):
    import os,bpy.path
    dir_path=bpy.path.abspath(directory)
    filelist=[file for file in os.listdir(dir_path)]#create list
    for file in filelist:
        filepath=''.join([dir_path,file])
        os.remove(filepath)
    return

class MchHeader_class:
    """Class defining all adresses and values of MCH header:
        -char_name
        -ModelAddress;//address
        -BoneCount;
        -VCount;
        -TexAnimSize;//texture anim size.Minimum is 0x14 ( for eye blinking)
        -FCount;
        -Unk1Count;//unknown data type 1 count
        -ObCount;
        -Unk2Count;//unknown data type 2 count
        -TriCount;
        -QuadCount;
        -BoneOffset;
        -VOffset;
        -TexAnimOffset;//texture anim
        -FOffset;
        -Unk1Offset;//unknown data type 1
        -ObOffset;
        -AnimOffset;
        -Unk2Offset;//unknown data type 2# Most the time 0x01FF0104
        -AnimCount;"""
    def __init__(self) :#constructor
        self.char_name='none'
        self.ModelAddress=0
        self.BoneCount=0
        self.VCount=0
        self.TexAnimSize=0
        self.FCount=0
        self.Unk1Count=0
        self.ObCount=0
        self.Unk2Count=0
        self.TriCount=0
        self.QuadCount=0
        self.BoneOffset=0
        self.VOffset=0
        self.TexAnimOffset=0
        self.FOffset=0
        self.Unk1Offset=0
        self.ObOffset=0
        self.AnimOffset=0
        self.Unk2Offset=0
        self.AnimCount=0
    def __repr__(self):#print
        return ("Name:{}  ModelAddress:{}  \
BoneCount:{}  \
VCount:{}  \
TexAnimSize:{}  \
FCount:{}\n\
ObCount:{}  \
TriCount:{}  \
QuadCount:{}  \
BoneOffset:{}  \
VOffset:{}\n\
TexAnimOffset:{}  \
FOffset:{}  \
Unk1Offset:{}  \
ObOffset:{}  \
AnimOffset:{}\n".format(
    self.char_name,
    hex(self.ModelAddress),
    hex(self.BoneCount),
    hex(self.VCount),
    hex(self.TexAnimSize),
    hex(self.FCount),
    hex(self.ObCount),
    hex(self.TriCount),
    hex(self.QuadCount),
    hex(self.BoneOffset),
    hex(self.VOffset),
    hex(self.TexAnimOffset),
    hex(self.FOffset),
    hex(self.Unk1Offset),
    hex(self.ObOffset),
    hex(self.AnimOffset)))    

class MchVertex_class:
    """Class defining a MCH vertex(8bytes):
        -x#2bytes
        -y#2bytes
        -z#2bytes
        -2 unknown bytes"""
    def __init__(self,x,y,z) :#constructor
        self.x=x
        self.y=y
        self.z=z
    #Comparison operators
    def __eq__(self, other):#"=="
        if isinstance(other,MchVertex_class):
            return (self.x == other.x)and(self.y == other.y)and(self.z == other.z)#compare all dictionary
        return NotImplemented
    def __ne__(self, other):#"!="
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    def __le__(self, other):
        if isinstance(other,MchVertex_class):
            return (self.x <= other.x)or((self.x == other.x)and(self.y <= other.y))or((self.x == other.x)and(self.y == other.y)and(self.z <=other.z))
        return NotImplemented
    def __lt__(self, other):
        if isinstance(other,MchVertex_class):
            return (self.x < other.x)or((self.x == other.x)and(self.y < other.y))or((self.x == other.x)and(self.y == other.y)and(self.z <other.z))
        return NotImplemented
    def __ge__(self, other):
        if isinstance(other,MchVertex_class):
            return (self.x >= other.x)or((self.x == other.x)and(self.y >= other.y))or((self.x == other.x)and(self.y == other.y)and(self.z >=other.z))
        return NotImplemented
    def __gt__(self, other):
        if isinstance(other,MchVertex_class):
            return (self.x >other.x)or((self.x == other.x)and(self.y > other.y))or((self.x == other.x)and(self.y == other.y)and(self.z >other.z))
        return NotImplemented


class MchUV_class:
    """Class defining a MCH vertex(8bytes):
        -x#1byte
        -y#1byte"""
    def __init__(self,u,v) :#constructor
        self.u=u
        self.v=v
    #Comparison operators
    def __eq__(self, other):#"=="
        if isinstance(other,MchUV_class):
            return (self.u== other.u)and(self.v==other.v)#compare all dictionary
        return NotImplemented
    def __ne__(self, other):#"!="
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    def __le__(self, other):
        if isinstance(other,MchUV_class):
            return (self.u <= other.u)or((self.u == other.u)and(self.v <= other.v))
        return NotImplemented
    def __lt__(self, other):
        if isinstance(other,MchUV_class):
            return (self.u < other.u)or((self.u == other.u)and(self.v < other.v))
        return NotImplemented
    def __ge__(self, other):
        if isinstance(other,MchUV_class):
            return (self.u >= other.u)or((self.u == other.u)and(self.v >= other.v))
        return NotImplemented
    def __gt__(self, other):
        if isinstance(other,MchUV_class):
            return (self.u > other.u)or((self.u == other.u)and(self.v > other.v))

class MchFace_class:
    """Class defining a MCH face(64bytes):
        -is_tri #Triangle if 0x25010607 and Quad if 0x2d010709
        -8 unused bytes
        -v1 #2bytes
        -v2 #2bytes
        -v3 #2bytes
        -v4 #2bytes
        -24 unused bytes
        -vt1 #1byte
        -vt2 #1byte
        -vt3 #1byte
        -vt4 #1byte
        -2 unused bytes
        -texgroup# 2bytes
        -12 unused bytes"""
    def __init__(self) :#constructor
        self.is_tri=0
        self.v1=0
        self.v2=0
        self.v3=0
        self.v4=0
        self.vt1=0
        self.vt2=0
        self.vt3=0
        self.vt4=0
        self.texgroup=0

class MchBone_class:
    """Class defining a MCH bone(64bytes):
        -parent
        -length
        -name
        -head#(x,y,z)
        -tail#(x,y,z)
        -Nbchild
        -Chainlength"""
    def __init__(self) :#constructor
        self.parent=-1#-1 if no parent
        self.length=0
        self.name='none'
        self.head=(0,0,0)#obtained with restpose data
        self.tail=(0,0,0)#obtained with restpose data

        self.Nbchild=0
        self.Chainlength=1
    def __repr__(self):
        return("name:{} parent:{} length:{} head:{} tail:{} Nbchild:{} Chainlength:{}\n"\
.format(self.name,hex(self.parent),hex(self.length),self.head,self.tail,hex(self.Nbchild),hex(self.Chainlength)))

class MchPose_class:
    """Class defining a MCH pose, a Euler rotation matrix XYZ
        -rotX#euler rotation vector around local X axis
        -rotY#euler rotation vector around local Y axis
        -rotZ#euler rotation vector around local Z axis"""
    def __init__(self) :#constructor
        self.rotX=0
        self.rotY=0
        self.rotZ=0
    def __repr__(self):
        return("rotX:{} rotY:{} rotZ:{}\n"\
.format(self.rotX,self.rotY,self.rotZ))

class MchFrame_class:
    """Class defining a MCH frame
        -Offset
        -poseList"""
    def __init__(self) :#constructor
        self.Offset=(0,0,0)
        self.poseList=[]
    def __repr__(self):
        return("Offset:{}\n".format(hex(self.Offset)))

class MchAnim_class:
    """Class defining a MCH anim
        -name
        -framecount
        -bonecount
        -oneAddress#address in chara.one
        -frameList"""
    def __init__(self) :#constructor
        self.name='none'
        self.frameCount=0
        self.boneCount=0
        self.oneAddress=0#Address in chara.one
        self.frameList=[]
    def __repr__(self):
        return("frameCount:{} boneCount:{} oneAddress:{}\n"\
.format(self.name,hex(self.frameCount),hex(self.boneCount),hex(self.oneAddress)))

class MchAlone_class:
    """Class defining a chara.one character, I call it "alone"
        -Address(4 bytes)
        -Size(4 bytes x2)
        -hasTim(4 bytes)#tim textures if NPC.<=0xd0000000 if hasTim=1.
            -TimOffset(4bytes) if hasTim=1
        -ModelOffsetfset#address of the mesh in chara.one
        -name(4 chars)
        -unk1 bytes(4 bytes)
        -0xeeeeeeee"""
    def __init__(self) :#constructor
        self.name=''
        self.Address=0
        self.Size=0
        self.hasTim=0
        self.TimOffset=0
        self.ModelOffset=0
        self.AnimCount=0
    def __repr__(self):
        return("name{} address:{} size:{} hasTim:{} timoffset:{} ModelOffset:{}\n"\
.format(self.name,hex(self.Address),hex(self.Size),hex(self.hasTim),hex(self.TimOffset),hex(self.ModelOffset),hex(self.AnimCount)))

class MchSkin_class:
    """Class defining a Skin group(8 bytes):
        -vertexFirstx#2bytes
        -vertexCount#2bytes
        -bone#2bytes

        -faceCount
        -faceList
        -vertexIdList
        -name"""
    def __init__(self) :#constructor
        self.vertexFirst=0
        self.vertexCount=0
        self.bone=0
        self.faceCount=0
        self.faceList=[]
        self.vertexIdList=[]
        self.name='none'
    def __repr__(self):
        return("name: {} vFirst:{} vCount:{} bone:{} fCount:{}\n"\
.format(self.name,hex(self.vertexFirst),hex(self.vertexCount),hex(self.bone),hex(self.faceCount)))


class CLUT_class:
    """Class defining a CLUT ( image or palette)
    uint32_t CLUT_imagesize;//(4bytes) size in bytes including the header
    uint16_t CLUT_x;//(2bytes)localisation on the cache
    uint16_t CLUT_y;//(2bytes)localisation on the cache
    uint16_t CLUT_pixH;//(2bytes)sizeX in pixel ( X4 for 4-bit , X2 for 8-bit, X1 for 16-bit, x2/3 for 24-bit)
    uint16_t CLUT_pixV;//(2bytes)sizeY in pixel
    /*--here starts the colors(2bytes for TIM an 4bytes for BMP)*/"""

    def __init__(self) :#constructor
        self.imagesize=0
        self.x=0
        self.y=0
        self.pixH=0
        self.pixV=0
    def __repr__(self):#print
        return ("Size:{} bytes  x:{} y:{} pixH:{} pixV:{}\n".format(
        self.imagesize,
        self.x,
        self.y,
        self.pixH,
        self.pixV))

def ReadMCH(inputfile): 
    """Open a .MCH file in binary mode, extracts its header, then stores it in an MchHeader class object"""
    header=MchHeader_class()
    inputfile.seek(0,0)
    byteArray=0
    out=0
    #Skip the texture maps
    while (byteArray!=None) and (out!=1):
        byteArray=int.from_bytes(inputfile.read(4), byteorder='little')
        if byteArray==0xffffffff:
            out=1
    
    #get address of header(after all the texture maps)
    header.ModelAddress=int.from_bytes(inputfile.read(4), byteorder='little')
    #get bone count
    inputfile.seek(header.ModelAddress)
    header.BoneCount=int.from_bytes(inputfile.read(4), byteorder='little')
    #get vertices count
    inputfile.seek(header.ModelAddress+0x04)
    header.VCount=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get texture animation count
    inputfile.seek(header.ModelAddress+0x08)
    header.TexAnimSize=int.from_bytes(inputfile.read(4), byteorder='little')

    #get face count
    inputfile.seek(header.ModelAddress+0x0c)
    header.FCount=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get unk1 count
    inputfile.seek(header.ModelAddress+0x10)
    header.Unk1Count=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get skin object count
    inputfile.seek(header.ModelAddress+0x14)
    header.ObCount=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get unk2 count
    inputfile.seek(header.ModelAddress+0x18)
    header.Unk2Count=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get tri count
    inputfile.seek(header.ModelAddress+0x1c)
    header.TriCount=int.from_bytes(inputfile.read(2), byteorder='little')
    
    #get quad count
    inputfile.seek(header.ModelAddress+0x1e)
    header.QuadCount=int.from_bytes(inputfile.read(2), byteorder='little')
    
    #get bone offset
    inputfile.seek(header.ModelAddress+0x20)
    header.BoneOffset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get vertices offset
    inputfile.seek(header.ModelAddress+0x24)
    header.VOffset=int.from_bytes(inputfile.read(4), byteorder='little')
   
    #get tex anim offset
    inputfile.seek(header.ModelAddress+0x28)
    header.TexAnimOffset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get face offset
    inputfile.seek(header.ModelAddress+0x2c)
    header.FOffset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get unk1 offset
    inputfile.seek(header.ModelAddress+0x30)
    header.Unk1Offset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get skin objects offset
    inputfile.seek(header.ModelAddress+0x34)
    header.ObOffset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get anim offset
    inputfile.seek(header.ModelAddress+0x38)
    header.AnimOffset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get unk2 offset
    inputfile.seek(header.ModelAddress+0x3c)
    header.Unk2Offset=int.from_bytes(inputfile.read(4), byteorder='little')
    
    #get anim count
    inputfile.seek(header.AnimOffset)
    header.AnimCount=int.from_bytes(inputfile.read(4), byteorder='little')       
    
    return header
    
def EnsureLookUpTable(Bmesh):
    #ensure lookup table(to modify a bmesh,it's necessary!
    if hasattr(Bmesh.verts, "ensure_lookup_table"): 
        Bmesh.verts.ensure_lookup_table()
    if hasattr(Bmesh.edges, "ensure_lookup_table"): 
        Bmesh.edges.ensure_lookup_table()
    if hasattr(Bmesh.faces, "ensure_lookup_table"): 
        Bmesh.faces.ensure_lookup_table()
    
    return 
    
def chainlength(bone_id,boneList):
    counter=0
    for i in range(0,len(boneList)):
        if((boneList[i].parent==bone_id)and(i!=bone_id)):
            counter+=1
            temp=chainlength(i,boneList)
            counter+=temp
    return counter
            
def createMeshFromData(name, verts, faces, uvs):

    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = [0,0,0]
    ob.show_name = True
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob# was scn.objects.active = ob
    ob.select_set(state = True)
 
    # Create mesh from given verts, faces.
    BVert=[[v.x,v.y,v.z] for v in verts]
    BFace=[]
    for i in range(len(faces)):        
        if ( faces[i].is_tri==0x25010607):        
            face=[faces[i].v1,faces[i].v2,faces[i].v3]
        else :        
            face=[faces[i].v1,faces[i].v2,faces[i].v3,faces[i].v4]
        BFace.append(face)
        
        
    me.from_pydata(BVert, [], BFace)    
    #test return
    #inputfile.close()
    #return ob
    #end-test return
    
    me.uv_layers.new(name=name+'UV')# was me.uv_textures.new(name+'UV')
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(me)
    
    EnsureLookUpTable(bm)

    uv_layer = bm.loops.layers.uv[0]
    for i in range(len(bm.faces)):
        f=bm.faces[i]
        if(len(f.loops)==3):
            f.loops[0][uv_layer].uv=(uvs[faces[i].vt1].u/256,uvs[faces[i].vt1].v/256)
            f.loops[1][uv_layer].uv=(uvs[faces[i].vt2].u/256,uvs[faces[i].vt2].v/256)
            f.loops[2][uv_layer].uv=(uvs[faces[i].vt3].u/256,uvs[faces[i].vt3].v/256)
        elif(len(f.loops)==4):
            f.loops[0][uv_layer].uv=(uvs[faces[i].vt1].u/256,uvs[faces[i].vt1].v/256)
            f.loops[1][uv_layer].uv=(uvs[faces[i].vt2].u/256,uvs[faces[i].vt2].v/256)
            f.loops[2][uv_layer].uv=(uvs[faces[i].vt3].u/256,uvs[faces[i].vt3].v/256)
            f.loops[3][uv_layer].uv=(uvs[faces[i].vt4].u/256,uvs[faces[i].vt4].v/256)
            
          
    bpy.ops.uv.remove_doubles(threshold=0.08)
    
    
    
    # Update mesh with new data
    bmesh.update_edit_mesh(me)
    bpy.ops.object.mode_set(mode='OBJECT')  
    return ob

###Drawing armature functions####
def createRig(name, origin, MCHboneList):
    import bpy, math
    from mathutils import Vector, Matrix
    # Create armature and object
    bpy.ops.object.add(
        type='ARMATURE', 
        enter_editmode=True,
        location=origin)
    ob = bpy.context.object
    ob.show_in_front= True
    ob.name = name
    amt = ob.data
    amt.name = name
    amt.show_axes = False
 
    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')
    for i in range(0,len(MCHboneList)):
        bname=MCHboneList[i].name
        vector=(MCHboneList[i].tail-MCHboneList[i].head)
        bone = amt.edit_bones.new(bname)
        if(i==0):
            pname="none"
            bone.head = (0,0,0)
            #vector = (0,0,1)#If vector = (0,0,0) the bone is not drawn !
            rot = Matrix.Identity(4)	# identity matrix
        else:
            pname=MCHboneList[MCHboneList[i].parent].name            
            parent = amt.edit_bones[pname]
            bone.parent = parent
            bone.head = parent.tail
            bone.use_connect = True
            (trans, rot_quat, scale) = parent.matrix.decompose()
            rot=rot_quat.to_matrix()
    
        bone.tail = Vector(vector) + bone.head
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

def ClearScene():
    scn = bpy.context.scene
#    for ob in scn.objects:
#        ob.select_set(state=True)
#        bpy.ops.object.mode_set(mode='OBJECT')
#        print("here!")
#        bpy.ops.object.delete()
        
    for a in bpy.data.actions:
        a.user_clear()
        bpy.data.actions.remove(a)
        print("here!")
    for m in bpy.data.meshes:
        m.user_clear()
        bpy.data.meshes.remove(m)
        
    for arm in bpy.data.armatures:
        arm.user_clear()
        bpy.data.armatures.remove(arm)
    
    for im in bpy.data.images:
        im.user_clear()
        bpy.data.images.remove(im)
        
    for mat in bpy.data.materials:
        mat.user_clear()
        bpy.data.materials.remove(mat)
    

        
def ReadBone(inputfile):
    header=ReadMCH(inputfile)
    inputfile.seek(header.ModelAddress+header.BoneOffset,0)
    boneList=[]
    print("bone Count from header:{}".format(header.BoneCount))
    for i in range(0,header.BoneCount):
        bone=MchBone_class()
        #get parent ( 2bytes)
        bone.parent=int.from_bytes(inputfile.read(2), byteorder='little')-1#base 1 in mch
        #skip 6 bytes
        inputfile.seek(6,1)
        #get length ( 2bytes).All bone length are negative
        bone.length=int.from_bytes(inputfile.read(2), byteorder='little')
        if(bone.length>0x10000-MAX_SIZE):
            bone.length-=0x10000
        #skip 54 bytes
        inputfile.seek(54,1)
        boneList.append(bone)
    
    #calculate nb of children
    for i in range(0,header.BoneCount):
        for j in range(0,header.BoneCount):
            if(boneList[j].parent==i):
                boneList[i].Nbchild+=1
    #calculate chain length
    for i in range(0,header.BoneCount):
        boneList[i].Chainlength=chainlength(i,boneList) 
            
    
    return boneList


def RestPose(mchfile,boneList,char_name):
    
    BoneRotations=[]
    header=ReadMCH(mchfile)
    mchfile.seek(header.ModelAddress+header.AnimOffset+2,0)
    anim=MchAnim_class()
    #frame count
    anim.frameCount=int.from_bytes(mchfile.read(2), byteorder='little')
    #bone count
    anim.boneCount=int.from_bytes(mchfile.read(2), byteorder='little')
    #offset
    x=int.from_bytes(mchfile.read(2), byteorder='little')
    if(x>0x10000-MAX_SIZE):
        x-=0x10000
    y=int.from_bytes(mchfile.read(2), byteorder='little')
    if(y>0x10000-MAX_SIZE):
        y-=0x10000
    z=int.from_bytes(mchfile.read(2), byteorder='little')
    if(z>0x10000-MAX_SIZE):
        z-=0x10000
    
    anim.offset=(x,y,z)
    #rotations
    poseList=[]
    mchfile.seek(header.ModelAddress+header.AnimOffset+2+10,0)
    for i in range(0,header.BoneCount):       
        pose=MchPose_class()
        
        pose.rotX=int.from_bytes(mchfile.read(2), byteorder='little')
        pose.rotY=int.from_bytes(mchfile.read(2), byteorder='little')
        pose.rotZ=int.from_bytes(mchfile.read(2), byteorder='little')
        #negative?
        if(pose.rotX>=0xf000):
            pose.rotX-=0x10000
        if(pose.rotY>=0xf000):
            pose.rotY-=0x10000            
        if(pose.rotZ>=0xf000):
            pose.rotZ-=0x10000
        poseList.append(pose)
         
    #bone name
    hairCount=0
    beltCount=0
    weaponLCount=0
    weaponRCount=0
    capeCount=0
    collarCount=0
    
    #    #----------Associate BoneNames to a bone number-------#
#    #test sequence
#        BoneSequence=\
#        [0,1,2,3,4,5,6,7,8,\
#        9,10,11,12,13,14,15,16,17,\
#        18,19,20,21,22,23,24,25,26,\
#        27,28,29,30,31,32,33,34,35,\
#        36,37,38,39,40,41,42,43,44,\
#        45,46,47,48,49,50,51,52,53]
    
    BoneNames=\
    ["root","upperbody","lowerbody","neck","collar0","collar1","collar2","collar3","collar4",\
    "collar5","breast_L","breast_R","cape0","cape1","cape2","cape3","cape4","cape5",\
    "head","hair0","hair1","hair2","hair3","hair4","hair5","shoulder_L","shoulder_R",\
    "arm_L","arm_R","forearm_L","forearm_R","hand_L","hand_R","weap0","weap1","weap2",\
    "weap3","weap4","weap5","weap6","hip_L","hip_R","belt0","belt1","belt2",\
    "belt3","belt4","belt5","thigh_L","thigh_R","tibia_L","tibia_R","foot_L","foot_R"]
    print("{} Bone names".format(len(BoneNames)))
    
    if char_name in ["d022","d023","d024","d025","d026","d051","d075"]:#RINOA
        BoneSequence=\
        [0,1,2,4,"N","N","N","N","N",\
        "N",3,5,"N","N","N","N","N","N",\
        10,16,22,27,29,30,31,9,11,\
        15,17,21,23,26,28,"N","N","N",\
        "N","N","N","N",7,8,6,12,18,\
        "N","N","N",13,14,19,20,24,25]
    
    elif char_name in ["d000","d001","d002","d003","d004","d005","d006","d007","d049","d052","d053"]:#SQUALL
        BoneSequence=\
        [0,1,2,4,"N","N","N","N","N",\
        "N",3,5,"N","N","N","N","N","N",\
        9,"N","N","N","N","N","N",8,10,\
        13,14,17,18,21,22,23,24,"N",\
        "N","N","N","N",6,7,"N","N","N",\
        "N","N","N",11,12,15,16,19,20]
    
    elif char_name in ["d027","d028","d029","d030"]:#SELPHIE
        BoneSequence=\
        [0,1,2,4,"N","N","N","N","N",\
        "N",3,5,"N","N","N","N","N","N",\
        9,14,19,"N","N","N","N",8,10,\
        13,15,18,20,23,24,"N","N","N",\
        "N","N","N","N",6,7,"N","N","N",\
        "N","N","N",11,12,16,17,21,22]
    elif char_name in ["d009","d010","d011","d012","d014"]:#ZELL
        BoneSequence=\
        [0,1,2,4,"N","N","N","N","N",\
        "N",3,5,"N","N","N","N","N","N",\
        9,"N","N","N","N","N","N",8,10,\
        13,14,17,18,21,22,"N","N","N",\
        "N","N","N","N",7,6,"N","N","N",\
        "N","N","N",12,11,16,15,20,19]
    elif char_name in ["d015","d016","d017"]:#IRVINE
        BoneSequence=\
        [0,1,2,4,5,11,"N","N","N",\
        "N",3,6,12,19,26,13,20,27,\
        10,18,25,32,"N","N","N",9,14,\
        17,21,24,28,31,33,"N","N","N",\
        "N","N","N","N",7,8,"N","N","N",\
        "N","N","N",15,16,22,23,29,30]
    
    elif char_name in ["d018","d019","d020","d021","d050"]:#QUISTIS
        BoneSequence=\
        [0,1,2,4,"N","N","N","N","N",\
				"N",3,5,"N","N","N","N","N","N",\
        9,14,20,15,21,"N","N",8,10,\
        13,16,19,22,25,26,"N","N","N",\
        "N","N","N","N",6,7,"N","N","N",\
        "N","N","N",11,12,17,18,23,24]
    
    elif char_name in ["d032","d033","d034","d035","d036","d037","d065"]:#SEIFER
        BoneSequence=\
				[0,1,2,6,8,20,5,17,24,\
				26,4,7,3,11,12,14,13,15,\
				18,"N","N","N","N","N","N",16,19,\
				27,28,35,36,39,40,41,"N","N",\
				"N","N","N","N",10,9,23,31,32,\
				25,33,34,22,21,30,29,38,37]
     
    
    else:
        print("Unknown character.Default bone sequence")
        BoneSequence=\
        [0,1,2,3,4,5,6,7,8,\
        9,10,11,12,13,14,15,16,17,\
        18,19,20,21,22,23,24,25,26,\
        27,28,29,30,31,32,33,34,35,\
        36,37,38,39,40,41,42,43,44,\
        45,46,47,48,49,50,51,52,53]
    
        
    for i in range(0,header.BoneCount):
        for j in range(0,len(BoneNames)):
            if BoneSequence[j]==i:
                boneList[i].name=BoneNames[j]
    
    for i in range(0,header.BoneCount):   
        print("bone {} {}->{}".format(i,boneList[i].name,poseList[i]))
        parent=boneList[boneList[i].parent]
        pparent=boneList[boneList[boneList[i].parent].parent]
        eul=Euler((0,0,0),'XYZ')
        if(i==0):
            boneList[i].head=Vector((0.0,0.0,0.0))
            boneList[i].length=Vector((anim.offset[0],anim.offset[1],anim.offset[2])).length
            
            boneList[i].tail=Vector((anim.offset[0],anim.offset[1],anim.offset[2]))
            boneList[i].tail=boneList[i].tail.normalized()*boneList[i].length/256
          
        else:
            rX=math.radians(360*poseList[i].rotX/MAX_ANGLE)
            rY=math.radians(360*poseList[i].rotY/MAX_ANGLE)
            rZ=math.radians(360*poseList[i].rotZ/MAX_ANGLE)
            
    
            eul=Euler((0,0,0),'XYZ')
            Vec=Vector((0,0,1))
            
            if (i==1):
                eul.rotate_axis('Y',math.radians(180))

            elif(boneList[i].name=="breast_L"):
                eul.rotate_axis('X',math.radians(-90))
            elif(boneList[i].name=="breast_R"):
                eul.rotate_axis('X',math.radians(90))
            elif(boneList[i].name=="shoulder_L"):
                eul.rotate_axis('X',math.radians(-60))
            elif(boneList[i].name=="shoulder_R"):
                eul.rotate_axis('X',math.radians(60))
            
            elif(boneList[i].name=="hip_L"):
                eul.rotate_axis('X',math.radians(-90))
            elif(boneList[i].name=="hip_R"):
                eul.rotate_axis('X',math.radians(90))
                
                
            elif(boneList[i].name=="head"):
                eul.rotate_axis('Y',math.radians(180))
            elif(boneList[i].name=="neck"):
                eul.rotate_axis('Y',math.radians(180))

            Vec.rotate(eul)
            boneList[i].tail=Vec*boneList[i].length/256+boneList[boneList[i].parent].tail
            boneList[i].head=boneList[boneList[i].parent].tail
        BoneRotations.append(eul)
        
        #removed armature creation here ---19/09/2024--Shunsq
    
 
   
 
    
    
    return BoneRotations

def poseRig(armature,boneList,poseList,offset,frame_num):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.posemode_toggle()#bpy.ops.object.mode_set(mode='POSE')
    bpy.context.scene.frame_set(frame_num)
  
    for i in range(0,len(poseList)):
                
        pbone = armature.pose.bones[boneList[i].name]
        # Set rotation mode to Euler XYZ, easier to understand
        # than default quaternions 
        pbone.rotation_mode = 'YXZ'
              
        rX=360*poseList[i].rotX/MAX_ANGLE
        rY=360*poseList[i].rotY/MAX_ANGLE
        rZ=360*poseList[i].rotZ/MAX_ANGLE
        
        rX=math.radians(rX)
        rY=math.radians(rY)
        rZ=math.radians(rZ) 
                
        pbone.rotation_euler=Euler((rX,rY,rZ),'YXZ')
        
        #insert a keyframe
        if(i==0):
            pbone.rotation_euler=Euler((0,0,0),'YXZ')
            #in pose mode Y is along bone direction, Z is forward
            locX=offset[0]
            locY=offset[1]
            locZ=offset[2]
            pbone.bone.select=True
            pbone.location=Vector((locY,locZ-boneList[i].length/256,locX))
            pbone.keyframe_insert(data_path="location" ,frame=frame_num)
            pbone.bone.select=False
        
        elif(i==1):
            pbone.rotation_euler.rotate(   Euler  ((0,(math.radians(180)),0),'YXZ'))
            pbone.rotation_euler.rotate(   Euler  (((math.radians(90)),0,0),'YXZ'))

        elif(i==2):
            pbone.rotation_euler.rotate(   Euler  (((math.radians(-90)),0,0),'YXZ'))
             
        
        pbone.keyframe_insert(data_path="rotation_euler" ,frame=frame_num)
        pbone.bone.select=False   
        
        
        
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.frame_set(0)
    
    

def CreateAction(armature,boneList,anim):
    """Create an action data block with MchAnim_class list called 'anim'"""
    if (armature.type!='ARMATURE'):
        return "No armature selected"    
    else:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        #name the action
        bpy.data.actions.new('before')
        armature.keyframe_insert(data_path="rotation_euler" ,frame=0)
        armature.animation_data.action=bpy.data.actions["before"]    
        tempName=armature.animation_data.action.name
        bpy.data.actions[tempName].name=anim.name           
        for i in range(0,anim.frameCount):
            curFrame=anim.frameList[i]
            poseRig(armature,boneList,curFrame.poseList,curFrame.Offset,i)                   
        bpy.ops.object.mode_set(mode='OBJECT')
              
    return  

def Retarget(arm_to_copy,arm_retarget,anim):   
    
    bpy.data.actions.new('before')
    arm_retarget.keyframe_insert(data_path="rotation_euler" ,frame=0)
    arm_retarget.animation_data.action=bpy.data.actions["before"]    
    tempName=arm_retarget.animation_data.action.name
    bpy.data.actions[tempName].name=anim.name+"re"
   
    bpy.context.view_layer.objects.active = arm_retarget
    

    bpy.ops.object.mode_set(mode='POSE') 
    
    
    for i in range(0,anim.frameCount):           
        bpy.context.scene.frame_set(i)
        arm_to_copy.animation_data.action=bpy.data.actions[anim.name]
    
        root_retarget=arm_retarget.pose.bones[0]   
        cns0 = root_retarget.constraints.new('COPY_LOCATION')
        cns0.name = 'Copy_Location'
        cns0.target = arm_to_copy
        cns0.subtarget = arm_retarget.pose.bones[0].name
        cns0.owner_space = 'WORLD'
        cns0.target_space = 'WORLD'
        
        root_retarget.bone.select=True
        bpy.ops.pose.visual_transform_apply()
        root_retarget.constraints.remove(root_retarget.constraints[0])    
        root_retarget.keyframe_insert(data_path="location" ,frame=i)
        root_retarget.bone.select=False
        
        for j in range(0,anim.boneCount):
            bone_retarget=arm_retarget.pose.bones[j]   
            cns = bone_retarget.constraints.new('COPY_ROTATION')
            cns.name = 'Copy_Rotation'
            cns.target = arm_to_copy
            cns.subtarget = arm_retarget.pose.bones[j].name
            cns.owner_space = 'WORLD'
            cns.target_space = 'WORLD'
            
            

            #apply transform
            bone_retarget.bone.select=True
            bpy.ops.pose.visual_transform_apply()
            for k in range(0,len(bone_retarget.constraints)):       
                bone_retarget.constraints.remove(bone_retarget.constraints[k])             
    
            
            bone_retarget.rotation_mode = 'YXZ'
            bone_retarget.keyframe_insert(data_path="rotation_euler" ,frame=i)
            bone_retarget.bone.select=False        
        
  
        bpy.context.scene.frame_set(0) 
    
    bpy.ops.object.mode_set(mode='OBJECT')
              
        

    return
def ReadAnim(boneList,onefile,char_name):
    """Returns a list of animations. An animation is a list of frames. A frame is a pose list of a bone list."""
    print("Extracting anim of {} from chara.one".format(char_name))
    onefile.seek(0,0)
    charCount=int.from_bytes(onefile.read(4), byteorder='little')
    print("{} characters".format(charCount))
    alone=MchAlone_class()
    for i in range(0,charCount):
        
        alone.Address=int.from_bytes(onefile.read(4), byteorder='little')+4#offset just after the character count so we add 4 for the absolute offset
        alone.Size=int.from_bytes(onefile.read(4), byteorder='little')
        onefile.seek(4,1)
        alone.hasTim=int.from_bytes(onefile.read(4), byteorder='little')
        if alone.hasTim<=0xd0000000:  #if has<=0xd0000000 then it's a NPC with textures
            alone.TimOffset=int.from_bytes(onefile.read(4), byteorder='little')
        alone.ModelOffset=int.from_bytes(onefile.read(4), byteorder='little')
        alone.name=onefile.read(4).decode(encoding="cp437")
        onefile.seek(8,1)
        if(alone.name==char_name):
            break
       
    armature_raw=bpy.context.scene.objects[char_name+"_armature_raw"]
    armature_rest=bpy.context.scene.objects[char_name+"_armature"]
    if(i==charCount-1):
        print("no {} found in chara.one".format(char_name))
    else: 
        print("{} found in chara.one".format(alone.name))
        #Read char animation
        onefile.seek(alone.Address,0)
        #anim count
        alone.AnimCount=int.from_bytes(onefile.read(2),byteorder='little')
        print("AnimCount:{}".format(alone.AnimCount))
        
        bpy.context.view_layer.objects.active = armature_raw
        
       
        for i in range(0,alone.AnimCount):
            
            anim=MchAnim_class()
            anim.name=char_name+"_act{}".format(i)
            anim.frameCount=int.from_bytes(onefile.read(2),byteorder='little')      
            anim.boneCount=int.from_bytes(onefile.read(2),byteorder='little')
            print ("frameCount:{} boneCount:{}".format(anim.frameCount,anim.boneCount))
            for j in range(0,anim.frameCount):           
                frame=MchFrame_class()
                offx=int.from_bytes(onefile.read(2),byteorder='little')
                offy=int.from_bytes(onefile.read(2),byteorder='little')
                offz=int.from_bytes(onefile.read(2),byteorder='little')
                if(offx>0xf000):
                    offx-=0x10000
                if(offy>0xf000):
                    offy-=0x10000
                if(offz>0xf000):
                    offz-=0x10000
                frame.Offset=Vector((offx/256,offy/256,offz/256))
                for k in range(0,anim.boneCount):
                    pose=MchPose_class()
                    
                    #Vehek 2 qhimm
                    byte_1=int.from_bytes(onefile.read(1),byteorder='little')
                    byte_2=int.from_bytes(onefile.read(1),byteorder='little')
                    byte_3=int.from_bytes(onefile.read(1),byteorder='little')
                    byte_4=int.from_bytes(onefile.read(1),byteorder='little')
                    
                    #ORIGINAL CODE
                    #pose.rotZ=((byte_1<<2)|((byte_4&3)<<0xA))
                    #pose.rotX=((byte_2<<2)|((byte_4&0xc)<<0x8))
                    #pose.rotY=((byte_3<<2)|((byte_4&0x30)<<0x6))
                    
                    #NEW CODE OPTION 2:Rx=(0,0,Rz1,Rz1,Rz1,Rz1,Rz1,Rz1,Rz1,Rz1,Rz4,Rz4)
                    pose.rotZ=((byte_1)|((byte_4&3)<<8))<<2
                    pose.rotX=((byte_2)|((byte_4&0xc)<<6))<<2
                    pose.rotY=((byte_3)|((byte_4&0x30)<<4))<<2
                    
                    if (pose.rotX>=0xf00):
                        pose.rotX-=0x1000
                    if (pose.rotY>=0xf00):
                        pose.rotY-=0x1000
                    if (pose.rotZ>=0xf00):
                        pose.rotZ-=0x1000
                    
                    frame.poseList.append(pose)
                anim.frameList.append(frame)
                       
            CreateAction(armature_raw,boneList,anim)
        
            #Retarget the animation on the restpose armature
            Retarget(armature_raw,armature_rest,anim)
            #Delete the raw animation
            act=bpy.data.actions[anim.name]
            act.user_clear()
            bpy.data.actions.remove(act)
            #Rename the new animation
            bpy.data.actions[anim.name+"re"].name=anim.name
        
        
        
    
    #Delete the raw armature
    bpy.context.view_layer.objects.active =armature_raw   
    bpy.ops.object.delete()
    #delete unused animation
    for u in bpy.data.actions:
        if (u.users==0):
            bpy.data.actions.remove(u)
   
    #Restpose
    bpy.context.view_layer.objects.active =armature_rest
    armature_rest.data.pose_position='REST' 
    armature_rest.data.display_type='WIRE'                  

    return
  
def TIM_TO_BLEND(inputfile,name):
    inputfile.seek(0,0)
    palette=CLUT_class()
    image=CLUT_class()
    texcount=0
    texoffset=0
    colordepth=0#/*file format(4bytes):
    """0x08 for 4-bits indexed(16 colors)
    0x09 for 8-bits indexed(256 colors)
    0x02 for 16-bits true color(no palette)
    0x03 for 24-bits true color(no palette)*/"""
    while texoffset!=0xFFFFFF:
        texoffset=int.from_bytes(inputfile.read(3), byteorder='little')
        inputfile.seek(1,1)#skip 1 byte
        if texoffset!=0xFFFFFF:
            texcount+=1
    print("{} textures found in mch".format(texcount))
    
    inputfile.seek(0,0)
    texoffset=0
    tex_image=bpy.data.images.new("{}".format(name),256,256)#original texture is 256x256
    
    for i in range(0,texcount):
        colordepth=0
        inputfile.seek(i*4,0)
        texoffset=int.from_bytes(inputfile.read(3), byteorder='little')
        inputfile.seek(texoffset+4,0)#skip0x10000000
        colordepth=int.from_bytes(inputfile.read(4), byteorder='little')
        print("texture {} TIM colordepth:{}".format(i,hex(colordepth)))
        
        #-------PALETTE IF 4-bit or 8-bit image----------
        if(colordepth==0x08) or (colordepth==0x09):
            #Color is 2bytes and stores ABGR data
            #Colorbits=ABBBBBGGGGGRRRRR
            palette.imagesize=int.from_bytes(inputfile.read(4), byteorder='little')  
            palette.x=int.from_bytes(inputfile.read(2), byteorder='little')
            palette.y=int.from_bytes(inputfile.read(2), byteorder='little')
            palette.pixH=int.from_bytes(inputfile.read(2), byteorder='little')
            palette.pixV=int.from_bytes(inputfile.read(2), byteorder='little')
            print("Palette size: {} x {}".format(palette.pixH,palette.pixV))
            
            #Convert 1 line of 256 pix into 16 pix x 16 pix image
            palette_image=bpy.data.images.new("palette{}".format(i),16,16)
            
            for pix in range(0,palette.pixH*palette.pixV):
                A=0
                B=0
                G=0
                R=0
                pix_image=0
                pix_image=int.from_bytes(inputfile.read(2), byteorder='little')
                A=(pix_image&0b1000000000000000)>>0x0F
                B=(pix_image&0b0111110000000000)>>0x0A
                G=(pix_image&0b0000001111100000)>>0x05
                R=pix_image&0b0000000000011111
                
                B=B/32#float <1.0
                G=G/32
                R=R/32
                
                if ((R!=0) or (G!=0) or (B!=0)):
                    A=1
                
                palette_image.pixels[pix*4]=R
                palette_image.pixels[pix*4+1]=G
                palette_image.pixels[pix*4+2]=B
                palette_image.pixels[pix*4+3]=A
                
        #-------IMAGE----------
        image.imagesize=int.from_bytes(inputfile.read(4), byteorder='little')  
        image.x=int.from_bytes(inputfile.read(2), byteorder='little')
        image.y=int.from_bytes(inputfile.read(2), byteorder='little')
        image.pixH=int.from_bytes(inputfile.read(2), byteorder='little')
        image.pixV=int.from_bytes(inputfile.read(2), byteorder='little')
        print("Image size: {} x {}".format(image.pixH,image.pixV))
            
        
        if colordepth==0x08:#4-bit
            palette_image=bpy.data.images["palette{}".format(i)]
            
            for pix in range(0,image.pixH*image.pixV*4):
                color=0
                color=int.from_bytes(inputfile.read(2), byteorder='little')
                R=palette_image.pixels[color*4]
                G=palette_image.pixels[color*4+1]
                B=palette_image.pixels[color*4+2]
                A=palette_image.pixels[color*4+3]
                
                if (R!=0) or (G!=0) or (B!=0):
                    A=1
                
                tex_image.pixels[pix*4]=R
                tex_image.pixels[pix*4+1]=G
                tex_image.pixels[pix*4+2]=B
                tex_image.pixels[pix*4+3]=A
                
        elif colordepth==0x09:#8-bit
            palette_image=bpy.data.images["palette{}".format(i)]
            print("teximage size {}x{}".format(tex_image.size[0],tex_image.size[1]))
            pix=0
            pix_offset=0
            pix_modulo=0
            pix_scaled=0
            for pix in range(0,image.pixH*image.pixV*2):
                color=0
                color=int.from_bytes(inputfile.read(1), byteorder='little')
                R=palette_image.pixels[color*4]
                G=palette_image.pixels[color*4+1]
                B=palette_image.pixels[color*4+2]
                A=palette_image.pixels[color*4+3]
                if (R!=0) or (G!=0) or (B!=0):
                    A=1    
                pix_modulo=pix%128
                if ( (pix_modulo==0) and pix>0):
                    pix_offset+=1
                pix_scaled=i*128*256+pix_modulo+256*pix_offset
                tex_image.pixels[pix_scaled*4]=R
                tex_image.pixels[pix_scaled*4+1]=G
                tex_image.pixels[pix_scaled*4+2]=B
                tex_image.pixels[pix_scaled*4+3]=A

    return 

def MCH_TO_BLEND():
    cur_dir=bpy.path.abspath("//")
    indir_name=''.join([cur_dir,"INPUT\\"])
    outdir_name=''.join([cur_dir,"OUTPUT\\"]) 
    mch_found=0
    one_found=0
    char_name='none'
    filelist=[entity for entity in os.listdir(indir_name)]#create list
    for entity in filelist:
        (filename, extension) = os.path.splitext(entity)
        if extension==".mch":
            mch_found=1
            char_name=filename[0:4]
            print("Character {} open\n".format(char_name))
        elif extension==".one":
            one_found=1
            char_name=filename[0:4]
            print("chara.one found\n")
    if mch_found==0:
        print("NO MCH found! Please put it in INPUT folder\n")
        return
    if one_found==0:
        print("NO chara.ONE found! No animation will be created\n")
   
    inputpath=''.join([indir_name,entity])
    print("{}\n".format(inputpath))
    inputfile=open(inputpath,"rb")
    

    header=MchHeader_class()
   
    
    header=ReadMCH(inputfile) 
     
    
    header.char_name=char_name
    print("{}\n".format(header))
    
   
    #Store vertices
    inputfile.seek(header.ModelAddress+header.VOffset)
    Vlist=[]
    for i in range(header.VCount):
        x=int.from_bytes(inputfile.read(2), byteorder='little')
        if(x>0x10000-MAX_SIZE):#negative
            x-=0x10000
        y=int.from_bytes(inputfile.read(2), byteorder='little')
        if(y>0x10000-MAX_SIZE):#negative
            y-=0x10000
        z=int.from_bytes(inputfile.read(2), byteorder='little')
        if(z>0x10000-MAX_SIZE):#negative
            z-=0x10000
        #skip 2 unknown bytes from actual position
        inputfile.seek(2,1)
        #store the vertex as a 3 float list
        Vlist.append(MchVertex_class(x/256,y/256,z/256))
        ##print("X{} Y{} Z{}".format(Vlist[i].x,Vlist[i].y,Vlist[i].z))   
       
        
    #Store faces and UVs
    inputfile.seek(header.ModelAddress+header.FOffset)
    Flist=[]
    UVlist=[]
    
    for i in range(header.FCount):
        inputfile.seek(header.ModelAddress+header.FOffset+i*64,0)
        fa=MchFace_class()
        Flist.append(fa)                     
        fa.is_tri=int.from_bytes(inputfile.read(4), byteorder='little')
        inputfile.seek(8,1)
        fa.v2=int.from_bytes(inputfile.read(2), byteorder='little')
        fa.v3=int.from_bytes(inputfile.read(2), byteorder='little')
        fa.v1=int.from_bytes(inputfile.read(2), byteorder='little')
        fa.v4=int.from_bytes(inputfile.read(2), byteorder='little')
        inputfile.seek(24,1)
        
        for j in range(4):#same order as face vertices(v2,v3,v1,v4)
            u=int.from_bytes(inputfile.read(1), byteorder='little')
            v=int.from_bytes(inputfile.read(1), byteorder='little')           
            UVlist.append(MchUV_class(u,v))
        
        #skip 2 unknown bytes from actual position
        inputfile.seek(2,1)
        fa.texgroup=int.from_bytes(inputfile.read(2), byteorder='little')
        #offset uvs by texture group
        for j in range(4):
            UVlist[4*i+j].v+=fa.texgroup*0x80
    
    
       
    #associate uvs to faces
    ##remove redundant uvs
    print("UV count before filter:",len(UVlist))
    UVlist_redundant=UVlist.copy()
    
    
    for uv in UVlist:   
        if(UVlist.count(uv)>1):
            UVlist.remove(uv)
    print("UV count after filter:",len(UVlist))
    
     
    
    ##associate uvs index
    for i in range(header.FCount):
        for j in range(len(UVlist)):
            if (UVlist[j]==UVlist_redundant[4*i]):
                Flist[i].vt2=j
            if (UVlist[j]==UVlist_redundant[4*i+1]):
                Flist[i].vt3=j
            if (UVlist[j]==UVlist_redundant[4*i+2]):
                Flist[i].vt1=j
            if (UVlist[j]==UVlist_redundant[4*i+3]):
                Flist[i].vt4=j
    #Draw the raw model in blender
         
    createMeshFromData("{}".format(header.char_name),Vlist,Flist,UVlist)
    
    
    #-----Associate material-------
    TIM_TO_BLEND(inputfile,header.char_name)
    mat=bpy.data.materials.new(header.char_name)
    bpy.data.objects["{}".format(header.char_name)].data.materials.append(mat)
    mat.use_nodes=True
    output_node=mat.node_tree.nodes["Material Output"]
    uv_node=mat.node_tree.nodes.new("ShaderNodeUVMap")
    tex_node=mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex_node.image=bpy.data.images[header.char_name]
    shader_node=mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.links.new(uv_node.outputs[0], tex_node.inputs[0])
    mat.node_tree.links.new(tex_node.outputs[0], shader_node.inputs[0])
    mat.node_tree.links.new(tex_node.outputs[1], shader_node.inputs[18])
    
    shader_node.location[0]=output_node.location[0]-300
    shader_node.location[1]=output_node.location[1]
    tex_node.location[0]=shader_node.location[0]-200
    tex_node.location[1]=shader_node.location[1]
    uv_node.location[0]=tex_node.location[0]-300
    uv_node.location[1]=tex_node.location[1]
    
    
    #Read skeleton
    BoneRotations=[]
    inputfile.seek(0,0)
    boneList=ReadBone(inputfile)
    inputfile.seek(0,0)
    BoneRotations=RestPose(inputfile,boneList,header.char_name)
    
    
    #----Create armature---19/09/2024---Shunsq
    #--------------------------------------------
    
    createRig(char_name+"_armature",Vector((0,0,0)),boneList)
    
    armature_rest=bpy.context.scene.objects[char_name+"_armature"]
     
    bpy.context.view_layer.objects.active=armature_rest
    bpy.ops.object.mode_set(mode='EDIT')
    for i in range(0,len(armature_rest.data.edit_bones)):
        eb=armature_rest.data.edit_bones[i]   
        eb.roll+=math.radians(-90)
    bpy.ops.object.mode_set(mode='OBJECT')

    #create raw armature( for charaone ) 
    rawbonelist=[]
    for i in range(0,header.BoneCount):
        bone=MchBone_class()
        
        bone=boneList[i]
        rawbonelist.append(bone)
    
    for i in range(0,header.BoneCount):   
        Vec=Vector((0,0,1))
        rawbonelist[i].tail=Vec*rawbonelist[i].length/256+rawbonelist[rawbonelist[i].parent].tail
        rawbonelist[i].head=rawbonelist[rawbonelist[i].parent].tail
    
    createRig(char_name+"_armature_raw",Vector((0,0,0)),rawbonelist) 
    armature_raw=bpy.context.scene.objects[char_name+"_armature_raw"]
    bpy.context.view_layer.objects.active=armature_raw
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in armature_raw.data.edit_bones:
        eb.roll+=math.radians(-90)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #END----Create armature---19/09/2024---Shunsq
    #--------------------------------------------
    
    #Read Anim
    one_found=0
    onepath="none"
    
    for entity in filelist:
        (filename, extension) = os.path.splitext(entity)
        if extension==".one":
            one_found=1
            onepath=''.join([indir_name,entity])
            print("{}\n".format(onepath))
            break             
    onefile=open(onepath,"rb")
    ReadAnim(boneList,onefile,char_name)
    #Read the skin objects
    char_ob=bpy.context.scene.objects[header.char_name]
    bpy.context.view_layer.objects.active=char_ob
    char_ob.select_set(state = True)
    inputfile.seek(header.ModelAddress+header.ObOffset)
    skinGroups=[]
    for i in range(0,header.ObCount):
        skin=MchSkin_class()
        #fist vertex base 0
        skin.vertexFirst=int.from_bytes(inputfile.read(2), byteorder='little')
        skin.vertexCount=int.from_bytes(inputfile.read(2), byteorder='little')
        #bone base 1
        skin.bone=int.from_bytes(inputfile.read(2), byteorder='little')-1
        #skip 2 bytes
        inputfile.seek(2,1)
        
        skin.name=boneList[skin.bone].name
        
        skinGroups.append(skin)
        print(" skin {}".format(skin.name))
        grp=char_ob.vertex_groups.new()
        grp.name=skin.name
        print(skin.vertexFirst)
        for j in range (0,header.VCount):
            if(j>=skin.vertexFirst)and(j<=(skin.vertexFirst+skin.vertexCount-1)):
                grp.add([j],1,'REPLACE')
            else:
                grp.add([j],0,'REPLACE')
    
    #limit total of groups per vertex to 1
    bpy.ops.object.vertex_group_limit_total(limit=1)
    #Put the skin objects in rest pose
    me=char_ob.data
    arma=bpy.context.scene.objects[header.char_name+"_armature"]
  
   
    for i in range(0,header.VCount):
        v=me.vertices[i]
        Vec=v.co  
        for j in range(0,header.ObCount):
            skin=skinGroups[j]
            min=skin.vertexFirst
            max=min+skin.vertexCount-1
            head=arma.data.bones[skin.name].head_local
            rot_eul=BoneRotations[skin.bone]           
                
      
            if(i>=min)and(i<=max):
                Vec.rotate(rot_eul) 
                Vec+=head
   
    
    # Give mesh object an armature modifier, using vertex groups but
    # not envelopes
    mod = char_ob.modifiers.new('MyRigModif', 'ARMATURE')
    mod.object = bpy.context.scene.objects[header.char_name+"_armature"]
    mod.use_bone_envelopes = False
    mod.use_vertex_groups = True
    inputfile.close()
    print("File closed")

    return

def BLEND_TO_MCH():
    cur_dir=bpy.path.abspath("//")
    indir_name=''.join([cur_dir,"INPUT\\"])
    outdir_name=''.join([cur_dir,"OUTPUT\\"]) 
    mch_found=0
    one_found=0
    char_name='none'
    
    filelist=[entity for entity in os.listdir(indir_name)]#create list
    for entity in filelist:
        (filename, extension) = os.path.splitext(entity)
        if extension==".mch":
            mch_found=1
            char_name=filename[0:4]
            print("Character {} open".format(char_name))
            break
   
    inputpath=''.join([indir_name,entity])
    print("{}\n".format(inputpath))
    inputfile=open(inputpath,"rb")
    
    #We need the original file to copy information: name, number of bones, texture animation
    
    header=MchHeader_class()
    header=ReadMCH(inputfile)
    header.char_name=char_name
    print("{}\n".format(header))    
        
    outputpath=''.join([outdir_name,char_name,'-new.mch'])
    print("{}\n".format(outputpath))
    outputfile=open(outputpath,"wb")
    
    #Get info from blend file
    Vcount=0
    Fcount=0
    Quadcount=0
    Tricount=0
    UVcount=0
    Vgroup_count=0
    Bone_count=0
    ob=bpy.data.objects["{}".format(header.char_name)]
    skl=bpy.data.objects["{}_armature".format(header.char_name)]
    Vcount=len(ob.data.vertices)
    Fcount=len(ob.data.polygons)    

    for i in range(0,Fcount):
        f=ob.data.polygons[i]
        UVcount+=f.loop_total
        if f.loop_total==3:
            Tricount+=1
        elif f.loop_total==4:
            Quadcount+=1
            
    
    Vgroup_count=len(ob.vertex_groups)
    Bone_count=len(skl.data.bones)
    
    print("Exporting {}\nVcount:{} Fcount:{} UVcount:{} Vgroups:{} Bones:{}".format(header.char_name,Vcount,Fcount,UVcount,Vgroup_count,Bone_count))
    
    #----NEW HEADER-------
    newheader=MchHeader_class()
    newheader.char_name=header.char_name
    newheader.ModelAddress=header.ModelAddress
    newheader.BoneCount=header.BoneCount
    newheader.VCount=Vcount
    newheader.TexAnimSize=header.TexAnimSize#we keep the same number of frames
    newheader.FCount=Fcount
    newheader.Unk1Count=header.Unk1Count
    newheader.ObCount=header.ObCount
    newheader.Unk2Count=header.Unk2Count
    newheader.TriCount=Tricount
    newheader.QuadCount=Quadcount
    newheader.BoneOffset=header.BoneOffset
    newheader.VOffset=header.VOffset
    newheader.TexAnimOffset=newheader.VOffset+8*Vcount#a vertex is 8 bytes
    newheader.FOffset=newheader.TexAnimOffset+newheader.TexAnimSize# tex animation is at least 0x14 bytes
    newheader.Unk1Offset=newheader.FOffset+Fcount*64#a face is 64 bytes
    newheader.ObOffset=newheader.Unk1Offset+newheader.Unk1Count*32#unk 1 is 32 bytes
    newheader.AnimOffset=newheader.ObOffset+newheader.ObCount*8#a skin object is 8 bytes
    newheader.AnimCount=header.AnimCount
    newheader.Unk2Offset=header.Unk2Offset# Most the time 0x01FF0104
    
    
   

    #--------------------------------------------
    #----UPDATE from 17/09/2024 starts here------
    #-------------------------------------------- 
    
    #----New model should share same skeleton, same texture count,same texture animation location
    #----New model real texture will be called with tonberry/FFnx plugin by detecting old texture
    
    #---COPY TEXTURES OFFSETS AND MAPS---
    #--------------------------------------
    inputfile.seek(0,0)
    outputfile.write(inputfile.read(header.ModelAddress))
    
    #---COPY BONE COUNT---
    inputfile.seek(header.ModelAddress,0)
    outputfile.write(inputfile.read(4))
    
    #---WRITE NEW VERTEXCOUNT---
    outputfile.write(newheader.VCount.to_bytes(4,'little'))
    
    #---WRITE TEX ANIM SIZE---
    outputfile.write(newheader.TexAnimSize.to_bytes(4,'little'))
    
    #---WRITE NEW FACECOUNT---
    outputfile.write(newheader.FCount.to_bytes(4,'little'))
        
    #---WRITE UNKNOWN1COUNT---
    outputfile.write(newheader.Unk1Count.to_bytes(4,'little'))
    
    #---WRITE SKINOBCOUNT---
    outputfile.write(newheader.ObCount.to_bytes(4,'little'))
    
    #---WRITE UNKNOWN2COUNT---
    outputfile.write(newheader.Unk2Count.to_bytes(4,'little'))
    
    #---WRITE NEW TRI COUNT---
    outputfile.write(newheader.TriCount.to_bytes(2,'little'))
    
    #---WRITE NEW QUAD COUNT---
    outputfile.write(newheader.QuadCount.to_bytes(2,'little'))
    
    #---WRITE NEW BONE OFFSET---
    outputfile.write(newheader.BoneOffset.to_bytes(4,'little'))
    
    #---WRITE NEW VERTICES OFFSET---
    outputfile.write(newheader.VOffset.to_bytes(4,'little'))
    
    #---WRITE NEW TEXANIM OFFSET---
    outputfile.write(newheader.TexAnimOffset.to_bytes(4,'little'))
    
    #---WRITE NEW FACES OFFSET---
    outputfile.write(newheader.FOffset.to_bytes(4,'little'))
    
    #---WRITE UNK1 OFFSET---
    outputfile.write(newheader.Unk1Offset.to_bytes(4,'little'))
    
    #---WRITE SKINOB OFFSET---
    outputfile.write(newheader.ObOffset.to_bytes(4,'little'))
    
    #---WRITE ANIM OFFSET---
    outputfile.write(newheader.AnimOffset.to_bytes(4,'little'))
    
    #---WRITE UNK2 OFFSET---
    outputfile.write(newheader.Unk2Offset.to_bytes(4,'little'))
    
    print("NEW BONE OFFSET:{}\nNEW VERTS OFFSET:{}\nNEW TANIM OFFSET:{}\nNEW FACE OFFET:{}\nNEW UNK1 OFFSET:{}\nNEW SKINOB OFFSET:{}\nNEW ANIM OFFSET:{}\nNEW UNK2 OFFSET:{}\n".\
    format(hex(newheader.BoneOffset),hex(newheader.VOffset),\
    hex(newheader.TexAnimOffset),hex(newheader.FOffset),\
    hex(newheader.Unk1Offset),hex(newheader.ObOffset),\
    hex(newheader.AnimOffset),hex(newheader.Unk2Offset),'08x'))
    
    

    #---COPY BONES AND UPSCALE---
    #---------------------------
    inputfile.seek(0,0)
    bonelist=ReadBone(inputfile)#bone size is still [-256,256] here
    inputfile.seek(0,0)
    BoneRotations=RestPose(inputfile,bonelist,char_name)
    outputfile.seek(0,2)
    print("REAL BONE OFFSET:{} ".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress+newheader.BoneOffset,0)

    for bone in bonelist:
        if bone.name!='root':  
            outputfile.write( (bone.parent+1).to_bytes(2,'little'))
            outputfile.write( ((bone.parent+1)*0x40).to_bytes(2,'little'))#bone parent ID * 0x40. Why?
            outputfile.write(b'\x00' * 4)#skip 4 bytes
            l=math.floor(bone.length*UPSCALE)
            if l<0:
                l+=0x10000
            outputfile.write(l.to_bytes(2,'little'))
        else:
            outputfile.write(b'\x00' * 10)#skip 10 bytes
        outputfile.write(b'\x00' * 54)#skip 54 bytes
        
    #--WRITE VERTICES IN SAME ORDER AS VGROUPS AND BONES--
    #----------------------------------------------------
    outputfile.seek(0,2)
    print("REAL VERTS OFFSET:{} ".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress +newheader.VOffset,0)
    char_ob=bpy.context.scene.objects[newheader.char_name]
    skl_ob=bpy.context.scene.objects["{}_armature".format(newheader.char_name)]
    Vorder=[[]for vg in range(newheader.ObCount)]#first index is the group ID, second index is the re-ordered vertex ID
    
    Vorder_total=0
    rot_eul=Euler((0,0,0),'XYZ')    
    me=char_ob.data
    
    for vgroup in char_ob.vertex_groups:
        
        for vertID in range(0,len(char_ob.data.vertices)):
            try: 
                vgroup.weight(vertID)
            except:
                pass  
            else:             
                if vgroup.weight(vertID)>0:
                   Vorder[vgroup.index].append(vertID)
        Vorder_total+=len(Vorder[vgroup.index])
                   
    print("Vorder total :{}\n".format(hex(Vorder_total),'08x'))    
    #---Get bone location and move vertices to zero
    Vorder_total=0
    for vgroup in char_ob.vertex_groups:
        bone=skl_ob.data.bones[vgroup.name]#beware : the bone ID in the skeleton is different from the original MCH
        boneID=-1
        for i in range ( 0 ,len(bonelist)):
            if bonelist[i].name==vgroup.name:
                boneID=i
                
        rot_eul=Euler((-BoneRotations[boneID][0],-BoneRotations[boneID][1],-BoneRotations[boneID][2]), 'ZYX')
 
          
        for orderID in range(len(Vorder[vgroup.index])):
            vert=me.vertices[Vorder[vgroup.index][orderID]]
            Vec=vert.co  
            nvert=Vector([0,0,0])
            head=bone.head_local
            nvert=(Vec-head)
            nvert.rotate(rot_eul)
            
            nvert[0]=math.floor(nvert[0]*256)*UPSCALE
            nvert[1]=math.floor(nvert[1]*256)*UPSCALE
            nvert[2]=math.floor(nvert[2]*256)*UPSCALE

            if nvert[0]<0:
                nvert[0]+=0x10000
            if nvert[1]<0:
                nvert[1]+=0x10000
            if nvert[2]<0:
                nvert[2]+=0x10000
          
            outputfile.write(int(nvert[0]).to_bytes(2,'little'))
            outputfile.write(int(nvert[1]).to_bytes(2,'little'))
            outputfile.write(int(nvert[2]).to_bytes(2,'little'))
            outputfile.write(b'\x00' * 2)#skip 2 zero bytes
            Vorder_total+=1
           
    #--COPY TEXTURE ANIMATION--
    #--------------------------
    inputfile.seek(header.ModelAddress + header.TexAnimOffset,0)
    outputfile.seek(0,2)
    print("REAL TANIM OFFSET:{} ".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress +newheader.TexAnimOffset,0)
    outputfile.write(inputfile.read( header.TexAnimSize)) 
   
    
    #--WRITE FACES--
    #---------------
    #bpy.ops.object.mode_set(mode='EDIT')
    #bm = bmesh.from_edit_mesh(char_ob.data)
    #uv_layer = bm.loops.layers.uv.verify()
    outputfile.seek(0,2)
    print("REAL FACE OFFSET:{}\n".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress +newheader.FOffset,0)
    uv_layer = me.uv_layers["{}UV".format(newheader.char_name)]
    Vinvert=[0 for i in range(newheader.VCount)]# if vertID is global ID, order ID is the Vgroup ID of vertID, offset is the position of the Vgroup, then Vinvert[vertID]=orderID +offset is the re-ordered ID
    offset=[0 for i in range(newheader.ObCount)]
    offset[0]=0
    for vgroupID in range(1,newheader.ObCount):
        offset[vgroupID]=offset[vgroupID-1]+len(Vorder[vgroupID-1])
    
    
    for vertID in range(0,newheader.VCount):
        orderID=-1
        vgroupID=-1
        for j in range (0, newheader.ObCount):
            for i in range (0, len(Vorder[j])):
                if ( (Vorder[j][i]==vertID) and (orderID==-1)and (vgroupID==-1)):
                    orderID=i
                    vgroupID=j
                    Vinvert[vertID]=orderID+offset[vgroupID]
                    
    print("max vert ID :{}\n".format(hex(max(Vinvert)),'08x'))
                        
    countface=0
    for face in char_ob.data.polygons:#is tri?
        
        texgroup=[0,0]# MAX_TEXSIZE = 2048 so 16x16 texture groups max
        UVcoords=[[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0]]
        istri=0
        vcol=0
   
        #---vertices
        if len(face.vertices)<4:#triangle
            istri=0x25010607
            outputfile.write(istri.to_bytes(4,'little'))
            faceunk=0x0000000100000044
            outputfile.write(faceunk.to_bytes(8,'little'))#Always 4400000001000000
                
            outputfile.write(Vinvert[face.vertices[1]].to_bytes(2,'little'))
            outputfile.write(Vinvert[face.vertices[2]].to_bytes(2,'little'))
            outputfile.write(Vinvert[face.vertices[0]].to_bytes(2,'little'))
            outputfile.write(b'\x00' * 2)#skip 2 bytes
            
        else:#quad
            istri=0x2d010709
            outputfile.write(istri.to_bytes(4,'little'))
            faceunk=0x0000000100000044
            outputfile.write(faceunk.to_bytes(8,'little'))#Always 4400000001000000
            outputfile.write(Vinvert[face.vertices[1]].to_bytes(2,'little'))
            outputfile.write(Vinvert[face.vertices[2]].to_bytes(2,'little'))
            outputfile.write(Vinvert[face.vertices[0]].to_bytes(2,'little'))
            outputfile.write(Vinvert[face.vertices[3]].to_bytes(2,'little'))
        #--normals??
        normalV=[0,0,0]
        
        normalV[0]=math.floor(face.normal[0]*256)
        normalV[1]=math.floor(face.normal[1]*256)
        normalV[2]=math.floor(face.normal[2]*256)
        if normalV[0]<0:
            normalV[0]+=0x10000
        if normalV[1]<0:
            normalV[1]+=0x10000
        if normalV[2]<0:
            normalV[2]+=0x10000
    
        outputfile.write(int(normalV[0]).to_bytes(2,'little'))
        outputfile.write(int(normalV[1]).to_bytes(2,'little'))
        outputfile.write(int(normalV[2]).to_bytes(2,'little'))
        outputfile.write(int(normalV[0]).to_bytes(2,'little'))
        
        #--vertex colors in A R G B format
        for k in range(4):
            vcol=0x00999999
            outputfile.write(vcol.to_bytes(4,'little'))

        #--UVs                  
        for loopnum in range(0,len(face.loop_indices)):
            loopID=face.loop_indices[loopnum]
            #loop_mesh = me.loops[loopnum]
            loop_uv=uv_layer.data[loopID]
            #loop_vert=me.vertices[loop_mesh.vertex_index]
            
        
        if len(face.vertices)<4:#triangle
            for loopnum in range(len(face.loop_indices)):
            
                loopID=face.loop_indices[loopnum]
                 #loop_mesh = me.loops[loopnum] 
                loop_uv = uv_layer.data[loopID]
                 #loop_vert=me.vertices[loop_mesh.vertex_index]
                 
                texgroup[0]=math.floor(loop_uv.uv[0]*MAX_TEXSIZE/256)
                texgroup[1]=math.floor(loop_uv.uv[1]*MAX_TEXSIZE/256)
            
                #offset coordinates by texgroup
                UVcoords[loopnum][0]=loop_uv.uv[0]*MAX_TEXSIZE -texgroup[0]*256
                UVcoords[loopnum][1]=loop_uv.uv[1]*MAX_TEXSIZE -texgroup[1]*256
                
            outputfile.write(int(UVcoords[1][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[1][1]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[2][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[2][1]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[0][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[0][1]).to_bytes(1,'little'))
            outputfile.write(b'\x00' * 2)#skip 2 bytes
            
        else:
            for loopnum in range(len(face.loop_indices)):
            
                loopID=face.loop_indices[loopnum]
                 #loop_mesh = me.loops[loopnum] 
                loop_uv = uv_layer.data[loopID]
                 #loop_vert=me.vertices[loop_mesh.vertex_index]
                 
                texgroup[0]=math.floor(loop_uv.uv[0]*MAX_TEXSIZE/256)
                texgroup[1]=math.floor(loop_uv.uv[1]*MAX_TEXSIZE/256)
            
                #offset coordinates by texgroup
                UVcoords[loopnum][0]=loop_uv.uv[0]*MAX_TEXSIZE -texgroup[0]*256
                UVcoords[loopnum][1]=loop_uv.uv[1]*MAX_TEXSIZE -texgroup[1]*256
                
            outputfile.write(int(UVcoords[1][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[1][1]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[2][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[2][1]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[0][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[0][1]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[3][0]).to_bytes(1,'little'))
            outputfile.write(int(UVcoords[3][1]).to_bytes(1,'little'))
        
        outputfile.write(b'\x00' * 2)#skip 2 bytes
        
        #--texture group of 256pix *256pix. In our case, MAX_TEXSIZE is 2048*2048, so 8x8 texture groups 
        outputfile.write(int(texgroup[0]).to_bytes(1,'little'))
        outputfile.write(int(texgroup[1]).to_bytes(1,'little'))
        outputfile.write(b'\x00' * 8)#skip 8 bytes
        countface+=1
        
    bpy.ops.object.mode_set(mode='OBJECT')
    #---WRITE UNK1 DATA---
    #---------------------
    outputfile.seek(0,2)
    print("REAL UNK1 OFFSET:{} ".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress +newheader.Unk1Offset,0)
    for unkcount in range(newheader.Unk1Count):          
        #---first skin object/ vertex group--Always zero
        outputfile.write(b'\x00' * 2)
        #--vertex group count
        outputfile.write(newheader.ObCount.to_bytes(2,'little'))
        #--twelve zeroes
        outputfile.write(b'\x00' * 12)
        #--first tri--Always zero
        outputfile.write(b'\x00' * 2)
        #--tri count
        outputfile.write(newheader.TriCount.to_bytes(2,'little'))
        #--first quad--Always zero
        outputfile.write(b'\x00' * 2)
        #--quad count
        outputfile.write(newheader.QuadCount.to_bytes(2,'little'))
        #--8 zeroes
        outputfile.write(b'\x00' * 8)
    
    
    
    
    #---WRITE SKIN OBJECT DATA---
    #----------------------------
    outputfile.seek(0,2)
    print("REAL SKIN OB OFFSET:{} ".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress +newheader.ObOffset,0)
    
    for vgroup in char_ob.vertex_groups:
        outputfile.write((Vinvert[Vorder[vgroup.index][0]]).to_bytes(2,'little'))#1stvertex
        outputfile.write(len(Vorder[vgroup.index]).to_bytes(2,'little'))#vertex count
        boneID=-1
        for i in range ( 0 ,len(bonelist)):
            if bonelist[i].name==vgroup.name:
                boneID=i
        outputfile.write((boneID+1).to_bytes(2,'little'))#bone ID in base 1 for MCH
        outputfile.write(b'\x00' * 2)#skip 2 bytes
    
    #--COPY REST POSE AND UNK2 to the end of file---
    #-----------------------------------------------
    outputfile.seek(0,2)
    print("REAL ANIM OFFSET:{}\n".format(hex(outputfile.tell()-header.ModelAddress),'08x'))
    
    outputfile.seek(newheader.ModelAddress +newheader.AnimOffset,0)
    inputfile.seek(header.ModelAddress + header.AnimOffset,0)
    data = inputfile.read(1)
    while True: 
        if data:
            outputfile.write(data)
            data = inputfile.read(1)
        else: 
            break
    print("rest pose and Unk2 written!\n")
    print("MCH written !Enjoy the new model!\n")

    inputfile.close()
    outputfile.close()
    print("File closed")

    return

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

curr_mch_header=MchHeader_class()

#IHM code
"""**********************************************
FF8 operators definitions for the user interface
************************************************"""
class MchToBlend_op(bpy.types.Operator, ImportHelper):
    '''Import from FF8 (.mch)'''
    bl_idname = "ff8tools.mch2blend"#No capitals in bl_idname!!"
    bl_label = "Import MCH from FF8"
    filename_ext = ".mch"
    filter_glob = StringProperty(default="*.mch", options={'HIDDEN'})

    def execute(self, context):
        ClearScene()
        MCH_TO_BLEND(context, self.filepath)
        return {'FINISHED'}

class BlendToMch_op(bpy.types.Operator, ExportHelper):
    '''Export to FF8 (.mch)'''
    bl_idname = "ff8tools.blend2mch"#No capitals in bl_idname!!"
    bl_label = "Export MCH to FF8"
    filename_ext = ".mch"
    filter_glob = StringProperty(default="*.mch", options={'HIDDEN'})

    def invoke(self, context, _event):
        global curr_mch_header
        if not self.filepath:
            blend_filepath = context.blend_data.filepath
            if not blend_filepath:
                blend_filepath = curr_mch_header.char_name
            else:
                blend_filepath = os.path.splitext(blend_filepath)[0]

            self.filepath = blend_filepath + self.filename_ext

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    def execute(self, context):
        BLEND_TO_MCH(context, self.filepath)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(MchToBlend_op.bl_idname, text="FF8 Field Model (.mch)")

def menu_func_export(self, context):
    self.layout.operator(BlendToMch_op.bl_idname, text="FF8 Field Model (.mch)")

def register():#register all custom operators
    bpy.utils.register_class(MchToBlend_op)
    bpy.utils.register_class(BlendToMch_op)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():#unregister all custom operators
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(MchToBlend_op)
    bpy.utils.unregister_class(BlendToMch_op)


if __name__=="__main__":
    register()
    print("Import successful!")
