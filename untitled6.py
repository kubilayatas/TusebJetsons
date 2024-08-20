def create_img_FSR(self):
    sensorVal_list = self.ReadCellValueThread.buffer
    base_width = 150
    not_connected_color = (159,122,36)
    img1 = Image.new('RGB', [4*2,9*2], 255)
    wpercent1 = (base_width / float(img1.size[0]))
    hsize1 = int((float(img1.size[1]) * float(wpercent1)))
    data1 = img1.load()
    for x in range(img1.size[0]):
        for y in range(img1.size[1]-2):
            addr = int(y/2)*4+int(x/2)
            sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
            if sens_val==None:
                data1[x,y+2] = not_connected_color
            else:
                sens_val = int((sens_val/1023)*255)
                data1[x,y+2] = (sens_val,100,255-sens_val)
    ###
    for x in range(img1.size[0]):
        for y in range(2):
            addr = int(y/2)*4+int(x/2)+31
            if (addr==31 or addr==34):
                data1[x,y] = not_connected_color
            else:
                sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                if sens_val==None:
                    data1[x,y] = not_connected_color
                else:
                    sens_val = int((sens_val/1023)*255)
                    data1[x,y] = (sens_val,100,255-sens_val)
    ###
    img1 = img1.resize((base_width, hsize1), resample=Image.BICUBIC)
    #img = ImageTk.PhotoImage(img)
    img2 = Image.new('RGB', [4,9], 255)
    wpercent2 = (base_width / float(img2.size[0]))
    hsize2 = int((float(img2.size[1]) * float(wpercent2)))
    data2 = img2.load()
    for x in range(img2.size[0]):
        for y in range(img2.size[1]-1):
            addr = y*4+x
            sens_val = sensorVal_list[addr][7]
            if sens_val==None:
                data2[x,y+1] = not_connected_color
            else:
                sens_val += sensorVal_list[addr][9]
                sens_val = int(sens_val/2)
                sens_val = int((sens_val/65535)*255)
                data2[x,y+1] = (sens_val,100,255-sens_val)
    ###
    for x in range(img2.size[0]):
        for y in range(1):
            addr = y*4+x+31
            if (addr==31 or addr==34):
                data2[x,y] = not_connected_color
            else:
                sens_val = sensorVal_list[addr][7]
                if sens_val==None:
                    data2[x,y] = not_connected_color
                else:
                    sens_val += sensorVal_list[addr][9]
                    sens_val = int(sens_val/2)
                    sens_val = int((sens_val/65535)*255)
                    data2[x,y] = (sens_val,100,255-sens_val)
    ###
    img2 = img2.resize((base_width, hsize2), resample=Image.BICUBIC)
    
    img3 = Image.new('RGB', [4,9], 255)
    wpercent3 = (base_width / float(img3.size[0]))
    hsize3 = int((float(img3.size[1]) * float(wpercent3)))
    data3 = img3.load()
    for x in range(img3.size[0]):
        for y in range(img3.size[1]-1):
            addr = y*4+x
            sens_val = sensorVal_list[addr][6]
            if sens_val==None:
                data3[x,y+1] = not_connected_color
            else:
                sens_val += sensorVal_list[addr][8]
                sens_val = int(sens_val/2)
                sens_val = int((sens_val/65535)*255)
                data3[x,y+1] = (sens_val,100,255-sens_val)
    ###
    for x in range(img3.size[0]):
        for y in range(1):
            addr = y*4+x+31
            if (addr==31 or addr==34):
                data3[x,y] = not_connected_color
            else:
                sens_val = sensorVal_list[addr][6]
                if sens_val==None:
                    data3[x,y] = not_connected_color
                else:
                    sens_val += sensorVal_list[addr][8]
                    sens_val = int(sens_val/2)
                    sens_val = int((sens_val/65535)*255)
                    data3[x,y] = (sens_val,100,255-sens_val)
    ###
    img3 = img3.resize((base_width, hsize3), resample=Image.BICUBIC)
    #img = ImageTk.PhotoImage(img)
    return img1,img2,img3, self.width, self.height