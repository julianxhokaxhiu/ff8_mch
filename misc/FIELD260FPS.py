#*****************************************************************************#
#    Copyright (C) 2024 Shunsq                                                #
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

###
# PLEASE NOTE:
# THIS IS A STANDALONE SCRIPT. YOU CAN LAUNCH IT USING ONLY PYTHON
# YOU DO NOT NEED BLENDER FOR IT!
###

"""***********************************************
*********FIELD260FPS blender script***************
**********************************************"""
import os,math,tkinter
from os.path import basename,dirname

bl_info = {
    "name": "FF8 60 FPS conversion",
    "author": "Shunsq",
    "blender": (4, 2, 0),
    "version": (0, 1, 1),
    "location": "File > Export > 60fps chara.one(.one)",
    "description": "Convert chara.one animations to 60fps",
    "category": "Import-Export"
}

def FIELD_TO_60FPS(directory=""):
    one_found=0
    
    filelist=[entity for entity in os.listdir(directory)]#create list
    for entity in filelist:
        (filename, extension) = os.path.splitext(entity)
        if extension==".one":
            one_found=1
            curr_one_name=filename
            break
    print("{} one file found\n".format(curr_one_name))
   
    inputpath=''.join([directory,'/',curr_one_name,".one"])
    outputpath=''.join([directory,'/',curr_one_name,"-new.one"])
    
    inputfile=open(inputpath,"rb")
    
    outputfile=open(outputpath,"wb")
    
    
    
    '''This value controls the number of intermediate frames to create'''
    F_INTER=1# Between 2 frames, we interpolate F_INTER frames
    
    
    charCount=0
    
    #copy some info from original file
    #----------------------------------
    inputfile.seek(0,0)
    charCount=int.from_bytes(inputfile.read(4),byteorder='little')
    print("{} characters".format(charCount))
    outputfile.write(charCount.to_bytes(4,'little'))
    
    ModelAddress=[ 0 for char in range(charCount) ]
    ModelSize=[ 0 for char in range(charCount) ]
    ModelHasTim=[ 0 for char in range(charCount) ]#if <=0xd0000000 then it's a NPC with textures. Starting here, it is smae format as MCH for NPC
    ModelOffset=[ 0 for char in range(charCount) ]# 0 for main chars, because no texure in charaone. modelAddress for NPC; because textures are in charaone
    ModelName=[ "" for char in range(charCount) ]
    ModelAnimCount=[ 0 for char in range(charCount) ]
    Address_in_file=[ 0 for char in range(charCount) ]#To change later address and size if animations have changed
    
    for charID in range(charCount):
        Address_in_file[charID]=outputfile.tell()#will be used later to change address and size  
        ModelAddress[charID]=int.from_bytes(inputfile.read(4),byteorder='little')
        outputfile.write(ModelAddress[charID].to_bytes(4,'little'))

        ModelSize[charID]=int.from_bytes(inputfile.read(4),byteorder='little')
        inputfile.seek(4,1)#Model size duplicate ?
        outputfile.write(ModelSize[charID].to_bytes(4,'little'))
        outputfile.write(ModelSize[charID].to_bytes(4,'little'))#duplicate of model size
        
        ModelHasTim[charID]=int.from_bytes(inputfile.read(4),byteorder='little')
        outputfile.write(ModelHasTim[charID].to_bytes(4,'little'))

        if ModelHasTim[charID]<=0xd0000000:
            endtex=int.from_bytes(inputfile.read(4),byteorder='little')
            outputfile.write(endtex.to_bytes(4,'little'))
            texCount=1#at least 1 texture
            while endtex!=0xFFFFFFFF:#actually 0xFFFFFFFF is end code for textures. So it is possible to have 2 textures, or even more
                texCount+=1
                endtex=int.from_bytes(inputfile.read(4),byteorder='little')
                outputfile.write(endtex.to_bytes(4,'little'))

        ModelOffset[charID]=int.from_bytes(inputfile.read(4),byteorder='little')
        outputfile.write(ModelOffset[charID].to_bytes(4,'little'))

        ModelName[charID]=inputfile.read(4).decode(encoding="cp437")
        outputfile.write(ModelName[charID].encode('ascii'))
        print("modelname {}\n".format(ModelName[charID]))
         
        endcode=int.from_bytes(inputfile.read(8),byteorder='little')# changes depending on the field
        outputfile.write(endcode.to_bytes(8,'little'))
        
        
  
    padding=ModelAddress[0]+4 - outputfile.tell()
    outputfile.write(b'\x00'*padding)# list of zeroes before model
  
    
    outputfile.close()
    outputfile=open(outputpath,"r+b")#read and write mode to modify locally the file
    outputfile.read()#go to end of file
    
    
    
    #Write the animations
    for charID in range(charCount):
        New_address=outputfile.tell()-4
        print("Old address was {} New address is {}\n".format(hex(ModelAddress[charID]),hex(New_address),'08x'))
             
        inputfile.seek(ModelAddress[charID]+4,0)
        NPC_boneCount=0
        NPC_VCount=0
        NPC_TexAnimSize=0
        NPC_FCount=0
        NPC_Unk1Count=0
        NPC_ObCount=0
        NPC_Unk2Count=0
        NPC_TriCount=0
        NPC_QuadCount=0
        NPC_BoneOffset=0
        NPC_VOffset=0
        NPC_TexAnimOffset=0
        NPC_FOffset=0
        NPC_Unk1Offset=0
        NPC_ObOffset=0
        NPC_AnimOffset=0
        NPC_Unk2Offset=0#Always 0x01800140
        
        NPC_Address=0
  
        if ModelHasTim[charID]<=0xd0000000:# NPC
            #copy texture until ModelOffset
            outputfile.write(inputfile.read(ModelOffset[charID]))
            
            #copy NPC 3D model MCH
            NPC_Address=ModelAddress[charID]+4 + ModelOffset[charID]
            inputfile.seek(NPC_Address,0)
            
            #do here same operations as mch2blend
            NPC_boneCount=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_VCount=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_TexAnimSize=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_FCount=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_Unk1Count=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_ObCount=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_Unk2Count=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_TriCount=int.from_bytes(inputfile.read(2), byteorder='little')
            NPC_QuadCount=int.from_bytes(inputfile.read(2), byteorder='little')
            NPC_BoneOffset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_VOffset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_TexAnimOffset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_FOffset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_Unk1Offset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_ObOffset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_AnimOffset=int.from_bytes(inputfile.read(4), byteorder='little')
            NPC_Unk2Offset=int.from_bytes(inputfile.read(4), byteorder='little')#Always 0x01800140
            
            
            #skip header + anything until animation starts
            inputfile.seek(NPC_Address,0)
            outputfile.write(inputfile.read(NPC_AnimOffset))
            
            #get anim count
            inputfile.seek(NPC_Address+NPC_AnimOffset,0)            
        else:
            inputfile.seek(ModelAddress[charID]+4,0)               
        
        ModelAnimCount[charID]=int.from_bytes(inputfile.read(2),byteorder='little')
        outputfile.write(ModelAnimCount[charID].to_bytes(2,'little'))
            
        print("Anim count of {} : {}\n".format(ModelName[charID],ModelAnimCount[charID]))
    
        for animID in range(ModelAnimCount[charID]):
                      
            frameCount=int.from_bytes(inputfile.read(2),byteorder='little')        
            boneCount=int.from_bytes(inputfile.read(2),byteorder='little')
            
            AnimOffset=[ [0,0,0] for frameID in range(frameCount)]
            BoneRot=[ [ [0,0,0] for boneID in range(boneCount)] for frameID in range(frameCount)]
            
            outputfile.write( (    (frameCount-1)*F_INTER  + frameCount   ).to_bytes(2,'little'))# we multiply the frame rate 
            outputfile.write( boneCount.to_bytes(2,'little'))
            
            before_frames=outputfile.tell()
            
            #---copy every original frame, spaced by F_INTER-1 frames
            for frameID in range(0,frameCount):# every original frame
                #copy offsets
                AnimOffset[frameID][0]=int.from_bytes(inputfile.read(2),byteorder='little')
                AnimOffset[frameID][1]=int.from_bytes(inputfile.read(2),byteorder='little')
                AnimOffset[frameID][2]=int.from_bytes(inputfile.read(2),byteorder='little')
                
                outputfile.write(AnimOffset[frameID][0].to_bytes(2,'little'))
                outputfile.write(AnimOffset[frameID][1].to_bytes(2,'little'))
                outputfile.write(AnimOffset[frameID][2].to_bytes(2,'little'))
                
                '''if(AnimOffset[frameID][0]>0xf000):
                    AnimOffset[frameID][0]-=0x10000
                if(AnimOffset[frameID][1]>0xf000):
                    AnimOffset[frameID][1]-=0x10000
                if(AnimOffset[frameID][2]>0xf000):
                    AnimOffset[frameID][2]-=0x10000 '''#My previous code was wrong. On 2 bytes , the range is [-32768,32768] which is [0x10000-0x0800 , 0x800]      
                
                if(AnimOffset[frameID][0]>0x8000):
                    AnimOffset[frameID][0]-=0x10000
                if(AnimOffset[frameID][1]>0x8000):
                    AnimOffset[frameID][1]-=0x10000
                if(AnimOffset[frameID][2]>0x8000):
                    AnimOffset[frameID][2]-=0x10000
                
                #copy bone poses
                for boneID in range(boneCount):
                    byte_1=int.from_bytes(inputfile.read(1),byteorder='little')
                    byte_2=int.from_bytes(inputfile.read(1),byteorder='little')
                    byte_3=int.from_bytes(inputfile.read(1),byteorder='little')
                    byte_4=int.from_bytes(inputfile.read(1),byteorder='little')
                    
                    outputfile.write(byte_1.to_bytes(1,'little'))
                    outputfile.write(byte_2.to_bytes(1,'little'))
                    outputfile.write(byte_3.to_bytes(1,'little'))
                    outputfile.write(byte_4.to_bytes(1,'little'))
                      
                    #Bone rotation is [Rx,Ry,Rz]
                    BoneRot[frameID][boneID][2]=((byte_1)|((byte_4&3)<<8))<<2#12 bits
                    BoneRot[frameID][boneID][0]=((byte_2)|((byte_4&0xc)<<6))<<2
                    BoneRot[frameID][boneID][1]=((byte_3)|((byte_4&0x30)<<4))<<2
                    
                    
                    '''if (BoneRot[frameID][boneID][0]>=0xf00):
                        BoneRot[frameID][boneID][0]-=0x1000
                    if (BoneRot[frameID][boneID][1]>=0xf00):
                        BoneRot[frameID][boneID][1]-=0x1000
                    if (BoneRot[frameID][boneID][2]>=0xf00):
                        BoneRot[frameID][boneID][2]-=0x1000'''#wrong
                        
                    if (BoneRot[frameID][boneID][0]>=0x800):
                        BoneRot[frameID][boneID][0]-=0x1000
                    if (BoneRot[frameID][boneID][1]>=0x800):
                        BoneRot[frameID][boneID][1]-=0x1000
                    if (BoneRot[frameID][boneID][2]>=0x800):
                        BoneRot[frameID][boneID][2]-=0x1000
                           
                #---Create placeholders for interpolated frame
                if frameID<(frameCount-1):
                    for interID in range(F_INTER):
                        #--offset
                        outputfile.write(b'\x00'*6)
                        #--bone poses
                        outputfile.write(b'\x00'*4*boneCount)
            
               
            
            #---INTERPOLATION OF FRAMES------
            
            outputfile.seek(before_frames,0)   
            
            for frameID in range(0,frameCount-1):
                outputfile.read( (6 + 4 *boneCount) )#skip original frame
                 
                stepX=(AnimOffset[frameID+1][0] - AnimOffset[frameID][0]) / (F_INTER+1) 
                stepY=(AnimOffset[frameID+1][1] - AnimOffset[frameID][1]) / (F_INTER+1) 
                stepZ=(AnimOffset[frameID+1][2] - AnimOffset[frameID][2]) / (F_INTER+1) 
                stepBoneRot =[[0,0,0] for boneID in range(boneCount)]
                
                
                for boneID in range(boneCount):
                    stepBoneRot[boneID][0]=(BoneRot[frameID+1][boneID][0]-BoneRot[frameID][boneID][0]) / (F_INTER+1) 
                    stepBoneRot[boneID][1]=(BoneRot[frameID+1][boneID][1]-BoneRot[frameID][boneID][1]) / (F_INTER+1) 
                    stepBoneRot[boneID][2]=(BoneRot[frameID+1][boneID][2]-BoneRot[frameID][boneID][2]) / (F_INTER+1) 
                    
                
                for interID in range(F_INTER):
                    interX=AnimOffset[frameID][0] + stepX*(interID+1)
                    interY=AnimOffset[frameID][1] + stepY*(interID+1)
                    interZ=AnimOffset[frameID][2] + stepZ*(interID+1)
                    
                    interX=int(interX)
                    interY=int(interY)
                    interZ=int(interZ)
                    
                    if interX<0:
                        interX+=0x10000
                    if interY<0:
                        interY+=0x10000
                    if interZ<0:
                        interZ+=0x10000
                    
                    outputfile.write(interX.to_bytes(2,'little'))
                    outputfile.write(interY.to_bytes(2,'little'))
                    outputfile.write(interZ.to_bytes(2,'little'))
                    
                    for boneID in range(boneCount):
                        rotX=BoneRot[frameID][boneID][0]+stepBoneRot[boneID][0]*(interID+1)
                        rotY=BoneRot[frameID][boneID][1]+stepBoneRot[boneID][1]*(interID+1)
                        rotZ=BoneRot[frameID][boneID][2]+stepBoneRot[boneID][2]*(interID+1)
                                    
                        #On 12 bits ( 10 bits + 2 shifts), the smallest number is -2048( 0x1000-0x800)
                        
                        rotX=int(rotX)&0xFFF#12bits
                        rotY=int(rotY)&0xFFF#12bits
                        rotZ=int(rotZ)&0xFFF#12bits
                                                 
                        if rotX<0:
                            rotX+=0x1000
                        if rotY<0:
                            rotY+=0x1000
                        if rotZ<0:
                            rotZ+=0x1000
                            
                        rotX=rotX>>2#10bits
                        rotY=rotY>>2#10bits
                        rotZ=rotZ>>2#10bits
                        
                            
                        #chatGPT
                        #byte_4= (int(rotZ/4)&0x3)|(  (int(rotX/4)&0xc) ) |( (int(rotY/4)&0x30))
                        #byte_1= int(rotZ/4)& ~(0x3<<8)
                        #byte_2= int(rotX/4)& ~(0xC<<6)
                        #byte_3= int(rotY/4)& ~(0x30<<4)
                        
                        '''new interpretation, with b1b1b1b1b1b1b1b1-b2b2b2b2b2b2b2b2-b3b3b3b3b3b3b3b3-b4b4b4b4b4b4b4b4 = \
                                                    RzRzRzRzRzRzRzRz-RxRxRxRxRxRxRxRx-RyRyRyRyRyRyRyRy-RzRzRxRxRyRy 0 0'''
                        '''byte_4= ((rotZ&0x300)>>8) |((rotX&0x300)>>6) |   ((rotY&0x300)>>4)
                        byte_1= rotZ&0x7F
                        byte_2= rotX&0x7F
                        byte_3= rotY&0x7F'''
                        
                        byte_4= ((rotZ>>8)&3) |(  ((rotX>>8)&3)<<2   ) |(   ((rotY>>8)&3)<<4 )
                        byte_1= rotZ&0xFF
                        byte_2= rotX&0xFF
                        byte_3= rotY&0xFF
                        
                        
                        
                        outputfile.write(byte_1.to_bytes(1,'little'))
                        outputfile.write(byte_2.to_bytes(1,'little'))
                        outputfile.write(byte_3.to_bytes(1,'little'))
                        outputfile.write(byte_4.to_bytes(1,'little'))
            
            outputfile.read( (6 + 4 *boneCount) )#read last frame
        
                
        # Add around 2000 zeroes between characters, and rewrite model addresse and size              
        outputfile.read()#end of file
        outputfile.write(b'\x00'*2000)
        New_size=outputfile.tell()-(New_address+4)
      
       
        
        
        outputfile.seek(Address_in_file[charID]+4,0)
        outputfile.write(New_size.to_bytes(4,'little'))
        outputfile.write(New_size.to_bytes(4,'little'))#written twice
        
        outputfile.read()#end of file
        #change address for next model
        if charID<charCount-1:
            New_address=outputfile.tell()-4
            
            outputfile.seek(Address_in_file[charID+1],0)
            
            outputfile.write(New_address.to_bytes(4,'little'))
            outputfile.read()# back to end of file
        
    print("{} interpolated from 30fps to 60 fps !\n".format(filename))                      
    inputfile.close()
    outputfile.close()
          
          
                
    return


    
if __name__=="__main__":
    import os,os.path,tkinter
    os.system("cls") 
    from tkinter import filedialog
    from tkinter import *
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()

    FIELD_TO_60FPS(folder_selected)



            








