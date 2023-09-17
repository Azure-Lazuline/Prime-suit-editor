import numpy as np
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
from pathlib import Path

def recolor_all_suits(suits_to_recolor, do_export, outputdir,
                      powerheadcolor, powermaincolor, powerchestcolor, powermisccolor,
                      variaheadcolor, variamaincolor, variachestcolor, variamisccolor,
                      powervariavisorcolor,
                      gravityheadcolor, gravitymaincolor, gravitychestcolor, gravityvisorcolor,
                      phazonheadcolor, phazonmaincolor, phazonvisorcolor, phazonmisccolor,
                      fusionpowermaincolor, fusionpowerheadcolor, fusionpowerchestcolor,
                      fusionvariamaincolor, fusionvariaheadcolor, fusionvariachestcolor,
                      fusiongravitymaincolor, fusiongravityheadcolor, fusiongravitychestcolor,
                      fusionphazonmaincolor, fusionphazonheadcolor, fusionphazonchestcolor,
                      fusionallvisorcolor, fusionallmisccolor):

    #power suit visor is shared with varia suit visor and it'd be cool to split it eventually. tex1_64x64_m_dc893b73a414cb4c_14.png

    #morph ball energy is unimplemented since it needs to be done in the patcher. All the colors are already set up here though:
    #Power suit energy is powermisccolor (the only thing it's used for).
    #Varia nonspider is variamisccolor.
    #Varia spider is variavisorcolor, Gravity spider should be gravityvisorcolor.
    #Phazon spider is phazonvisorcolor for the outside edge, and phazonmisccolor for the core.


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------

    def getgradientcolors(color):
        ret = [[0, 0, 0], createshadow(color), color, createhighlight(color), [255, 255, 255]]

        #brightness = (color[0] / 255 + color[1] / 255 + color[2] / 255)
        brightness = max(max(color[0], color[1]), color[2]) / 255

        mult = 1
        #darken all colors by up to 30% if a very dark base color is selected, otherwise the highlights overpower it
        #if brightness < 0.5:
        #    mult = 0.7 + 0.3 * (brightness / 0.5)

        ret = np.array(ret) * mult
        
        return ret

    def getgradientpositions(center):
        return [0, center + (0 - center) * 0.5, center, center + (1 - center) * 0.5, 1]    

    #creates a 1x256 gradient map using the given color list, with each one at the equivalent position in colorspositions
    def creategradient(colorslist, colorspositions):
        
        #make a 256x1 array, and interpolate between values of colorslist depending on where x falls in colorspositions
        array = np.zeros((1, 256,3), dtype=np.uint8)
        for x in range(256):
            for index in range(len(colorslist) - 1):
                if x/255 >= colorspositions[index]:
                    percentbetweencolors = (x/255 - colorspositions[index]) / (colorspositions[index + 1] - colorspositions[index])
                    for i in range(3):
                        array[0, x, i] = colorslist[index][i] + (colorslist[index + 1][i] - colorslist[index][i]) * percentbetweencolors
        return array

    def clamp(num):
        return max(0, min(num, 255))

    #create an appropriate highlight color for the given input color, so the shading isn't flat
    def createhighlight(color):
        maxtowardsgreen = 60
        add = 0
        towardswhite = 0.5
        
        color2 = color.copy()
        maxrgb = max(color[0], color[1], color[2])
        #copy the highest of the r/b channels to the green channel (so red goes to yellow and blue goes to cyan), but clamped
        color2[1] = max(color2[1] - maxtowardsgreen, min(maxrgb, color2[1] + maxtowardsgreen))
        for i in range(3):
            color2[i] = clamp(color2[i] + (255 - color2[i]) * towardswhite + add)
        return color2

    #same for shadows
    def createshadow(color):
        maxawayfromgreen = 60
        subtract = 0
        towardsblack = 0.5

        color2 = color.copy()
        minrgb = min(color[0], color[1], color[2])
        color2[1] = max(color2[1] - maxawayfromgreen, min(minrgb, color2[1] + maxawayfromgreen))
        for i in range(3):
            color2[i] = clamp(color2[i] + (0 - color2[i]) * towardsblack - subtract)
        return color2




    #main function
    def recolor_suit(suitname, maskname, colors, gradientcenters, texnames):

        atlas = Image.open("img/" + suitname + '-base.png').convert('RGB')
        atlas_with_alpha = Image.open("img/" + suitname + '-base.png')
        #Get the pixel values into an array. Needs to be a copy since it's read-only by default
        colorarray = np.asarray(atlas).copy()

        #average all the colors to get the grayscale one
        grayscalearray = np.mean(colorarray, axis=2).astype(np.uint8)

        #for each of the 5 possible color layers, apply it to the relevant area
        for i in range(0, 5):
            maskname2 = ['-head.png', '-main.png', '-chest.png', '-visor.png', '-misc.png'][i]
            path = "img/" + maskname + maskname2
            if Path(path).is_file():
                #make a gradient of all possible values,
                gradientarray = creategradient(getgradientcolors(colors[i]), getgradientpositions(gradientcenters[i]))
                gradient = Image.fromarray(gradientarray)

                mask = Image.open(path).convert('L')
                array = np.zeros((*grayscalearray.shape,3), dtype=np.uint8)
                #then grab the relevant pixel from the gradient depending on the grayscale value of the source pixel
                np.take(gradient.getdata(), grayscalearray, axis=0, out=array)

                #turn the array values back into an image and copy it over the atlas, using the mask
                image = Image.fromarray(array)
                atlas.paste(image, mask=mask)

        #apply shading (for the preview image). It's stored as 0.5-gray-is-neutral.
        #take the image and double its brightness, so neutral is pure white. Then multiply it on top of the atlas to get the shadows.
        shading = Image.open("img/" + maskname + "-shading.png").convert('RGB')
        shadowamount = 0.5
        if suitname == "fusion-power" or suitname == "fusion-varia" or suitname == "fusion-gravity" or suitname == "fusion-phazon": shadowamount = 0.6    
        shading = ImageEnhance.Contrast(shading).enhance(shadowamount)
        shading = ImageEnhance.Brightness(shading).enhance(2)
        atlas = ImageChops.multiply(atlas, shading)

        #take the shading image again, adjust it so gray is at zero, then additive-blend it on the atlas
        shading = Image.open("img/" + maskname + "-shading.png").convert('RGB')
        shading = ImageEnhance.Contrast(shading).enhance(0.6) #amount of highlights
        shading = ImageChops.invert(shading) #no easy way with this lib to lerp towards white, so invert-multiply-invert it is...
        shading = ImageEnhance.Brightness(shading).enhance(2)
        shading = ImageChops.invert(shading)
        atlas = ImageChops.add(atlas, shading)

        #copy the alpha channel back to the image now that it's completed. (Keeping the alpha channel through the whole thing had complications)
        blank = Image.new('RGBA',[atlas.width, atlas.height], (0, 0, 0, 0))
        atlas = atlas.convert('RGBA')
        atlas = Image.composite(atlas, blank, atlas_with_alpha)
            
        #save out the atlas for easier debugging
        #atlas.save("DEBUG-atlas-" + suitname + ".png")

        if do_export:
            #slice and resize the atlas up into all the components.
            #Different suits have different layouts on the atlas because of way different sizes and components, so this is a bit of a mess...

            if suitname == "power" or suitname == "varia" or suitname == "gravity":
                if texnames[1] != "": atlas.crop([0, 0, 512, 512]).resize([256, 256]).save(outputdir + texnames[1]) #256x256 composite

                if texnames[2] != "": atlas.crop([0, 0, 0 + 256, 0 + 256]).save(outputdir + texnames[2]) #256x256 topleft
                if texnames[3] != "": atlas.crop([256, 0, 256 + 256, 0 + 256]).save(outputdir + texnames[3]) #256x256 topright
                if texnames[4] != "": atlas.crop([0, 256, 0 + 256, 256 + 256]).save(outputdir + texnames[4]) #256x256 bottomleft
                if texnames[5] != "": atlas.crop([256, 256, 256 + 256, 256 + 256]).save(outputdir + texnames[5]) #256x256 bottomright
                if texnames[6] != "": atlas.crop([512, 0, 512 + 256, 0 + 256]).save(outputdir + texnames[6]) #256x256 morphball
                if texnames[7] != "": atlas.crop([768, 0, 768 + 256, 0 + 256]).save(outputdir + texnames[7]) #256x256 spiderball
                if texnames[8] != "": atlas.crop([512, 256, 512 + 128, 256 + 128]).save(outputdir + texnames[8]) #128x128 3rd person arm
                if texnames[9] != "": atlas.crop([640, 384, 640 + 128, 384 + 128]).save(outputdir + texnames[9]) #128x128 gravity shoulder
                if texnames[10] != "": atlas.crop([640, 384, 640 + 128, 384 + 128]).resize([64, 64]).save(outputdir + texnames[10]) #64x64 gravity shoulder
                if texnames[11] != "": atlas.crop([640, 256, 640 + 64, 256 + 64]).save(outputdir + texnames[11]) #64x64 visor 1
                if texnames[12] != "": atlas.crop([704, 256, 704 + 64, 256 + 64]).save(outputdir + texnames[12]) #64x64 visor 2
                if texnames[13] != "": atlas.crop([640, 320, 640 + 64, 320 + 64]).save(outputdir + texnames[13]) #64x64 visor 3
                if texnames[14] != "": atlas.crop([704, 320, 704 + 64, 320 + 64]).save(outputdir + texnames[14]) #64x64 visor 4
                if texnames[15] != "": atlas.crop([512, 384, 512 + 64, 384 + 64]).save(outputdir + texnames[15]) #64x64 shine 1
                if texnames[16] != "": atlas.crop([576, 384, 576 + 64, 384 + 64]).save(outputdir + texnames[16]) #64x64 shine 2
                if texnames[17] != "": atlas.crop([512, 448, 512 + 64, 448 + 64]).save(outputdir + texnames[17]) #64x64 shine 3
                if texnames[18] != "": atlas.crop([768, 256, 768 + 128, 256 + 128]).save(outputdir + texnames[18]) #128x128 glass dark
                if texnames[19] != "": atlas.crop([896, 256, 896 + 128, 256 + 128]).save(outputdir + texnames[19]) #128x128 glass bright
                if texnames[20] != "": atlas.crop([576, 448, 576 + 64, 448 + 64]).save(outputdir + texnames[20]) #64x64 spiderball line
                if texnames[21] != "": atlas.crop([704, 320, 704 + 32, 320 + 32]).save(outputdir + texnames[21]) #32x32 power visor 5
                

            if suitname == "phazon":
                if texnames[1] != "": atlas.crop([0, 0, 256, 256]).resize([128, 128]).save(outputdir + texnames[1]) #128x128 composite

                if texnames[2] != "": atlas.crop([0, 0, 0 + 128, 0 + 128]).save(outputdir + texnames[2]) #128x128 topleft
                if texnames[3] != "": atlas.crop([128, 0, 128 + 128, 0 + 128]).save(outputdir + texnames[3]) #128x128 topright
                if texnames[4] != "": atlas.crop([0, 128, 0 + 128, 128 + 128]).save(outputdir + texnames[4]) #128x128 bottomleft
                if texnames[5] != "": atlas.crop([128, 128, 128 + 128, 128 + 128]).save(outputdir + texnames[5]) #128x128 bottomright
                if texnames[6] != "": atlas.crop([256, 0, 256 + 256, 0 + 256]).save(outputdir + texnames[6]) #256x256 suit shine
                if texnames[7] != "": atlas.crop([512, 0, 512 + 128, 0 + 128]).save(outputdir + texnames[7]) #128x128 spiderball
                if texnames[8] != "": atlas.crop([512, 128, 512 + 128, 128 + 128]).save(outputdir + texnames[8]) #128x128 glow clouds
                if texnames[9] != "": atlas.crop([64 * 0, 256, 64 * 1, 256 + 64]).save(outputdir + texnames[9]) #64x64 3rd person arm
                if texnames[10] != "": atlas.crop([64 * 1, 256, 64 * 2, 256 + 64]).save(outputdir + texnames[10]) #64x64 visor 1
                if texnames[11] != "": atlas.crop([64 * 2, 256, 64 * 3, 256 + 64]).save(outputdir + texnames[11]) #64x64 visor 2
                if texnames[12] != "": atlas.crop([64 * 3, 256, 64 * 4, 256 + 64]).save(outputdir + texnames[12]) #64x64 visor 3
                if texnames[13] != "": atlas.crop([64 * 4, 256, 64 * 5, 256 + 64]).save(outputdir + texnames[13]) #64x64 visor 4
                if texnames[14] != "": atlas.crop([64 * 5, 256, 64 * 6, 256 + 64]).save(outputdir + texnames[14]) #64x64 lights
                if texnames[15] != "": atlas.crop([64 * 6, 256, 64 * 7, 256 + 64]).save(outputdir + texnames[15]) #64x64 noise
                if texnames[16] != "": atlas.crop([64 * 7, 256, 64 * 8, 256 + 64]).save(outputdir + texnames[16]) #64x64 spiderball glow
                if texnames[17] != "": atlas.crop([64 * 8, 256, 64 * 9, 256 + 64]).save(outputdir + texnames[17]) #64x64 reflection map
                if texnames[18] != "": atlas.crop([576, 256, 576 + 32, 256 + 32]).save(outputdir + texnames[18]) #32x32 spiderball line
                if texnames[19] != "": atlas.crop([0, 320, 0 + 64, 320 + 64]).save(outputdir + texnames[19]) #32x32 circle reflect 1
                if texnames[20] != "": atlas.crop([64, 320, 64 + 64, 320 + 64]).save(outputdir + texnames[20]) #32x32 circle reflect 2

            #full samus preview,
            #256x256 helmet, 256x256 limbs,
            #256x256 torso, 256x256 morph ball,
            #128x128 helmet, 128x128 limbs, 128x128 torso,
            #128x128 orb dark, 128x128 orb light,
            #64x64 crystal, 64x64 visor

            if suitname == "fusion-power" or suitname == "fusion-varia" or suitname == "fusion-gravity" or suitname == "fusion-phazon":
                if texnames[1] != "": atlas.crop([0, 0, 0 + 256, 0 + 256]).save(outputdir + texnames[1]) #256x256 helmet
                if texnames[2] != "": atlas.crop([256, 0, 256 + 256, 0 + 256]).save(outputdir + texnames[2]) #256x256 limbs
                if texnames[3] != "": atlas.crop([0, 256, 0 + 256, 256 + 256]).save(outputdir + texnames[3]) #256x256 torso
                if texnames[4] != "": atlas.crop([256, 256, 256 + 256, 256 + 256]).save(outputdir + texnames[4]) #256x256 morph ball
                if texnames[5] != "": atlas.crop([0, 0, 0 + 256, 0 + 256]).resize([128, 128]).save(outputdir + texnames[5]) #128x128 helmet
                if texnames[6] != "": atlas.crop([256, 0, 256 + 256, 0 + 256]).resize([128, 128]).save(outputdir + texnames[6]) #128x128 limbs
                if texnames[7] != "": atlas.crop([0, 256, 0 + 256, 256 + 256]).resize([128, 128]).save(outputdir + texnames[7]) #128x128 torso
                if texnames[8] != "": atlas.crop([512, 0, 512 + 128, 0 + 128]).save(outputdir + texnames[8]) #128x128 orb dark
                if texnames[9] != "": atlas.crop([640, 0, 640 + 128, 0 + 128]).save(outputdir + texnames[9]) #128x128 orb light
                if texnames[10] != "": atlas.crop([512, 128, 512 + 64, 128 + 64]).save(outputdir + texnames[10]) #64x64 crystal
                if texnames[11] != "": atlas.crop([576, 128, 576 + 64, 128 + 64]).save(outputdir + texnames[11]) #64x64 visor

        #save the preview pic, even if not exporting
        previewpic = None
        if suitname == "power": previewpic = atlas.crop([768, 0, 768 + 256, 0 + 256])
        if suitname == "varia": previewpic = atlas.crop([1024, 0, 1024 + 256, 0 + 256])
        if suitname == "gravity": previewpic = atlas.crop([1024, 256, 1024 + 256, 256 + 256])
        if suitname == "phazon": previewpic = atlas.crop([768, 0, 768 + 256, 0 + 256])

        if suitname == "fusion-power" or suitname == "fusion-varia" or suitname == "fusion-gravity" or suitname == "fusion-phazon":
            previewpic = atlas.crop([768, 0, 768 + 256, 0 + 256])
            #fusion suit is darker in-engine compared to the texture; darken and adjust contrast of the preview to approximate it
            previewpic = ImageEnhance.Brightness(previewpic).enhance(0.8)
            previewpic = ImageEnhance.Contrast(previewpic).enhance(1.2)

        #phazon suit has boosted saturation to roughly approximate some missing effects
        if suitname == "phazon": previewpic = ImageEnhance.Color(previewpic).enhance(1.5)
        
        if previewpic is not None:
            previewpic.save("saved/" + texnames[0])
        

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------

    #main execution starts here

    #these two suits use the same visor texture, so only one config option is given for both of them right now.
    #the code itself can handle having it separate, so undo this and expose both these variables once there's not the texture overlap
    powervisorcolor = powervariavisorcolor
    variavisorcolor = powervariavisorcolor

    #there's technically support for a third color for Power Suit, but nothing i tried with it looked good, so set it to the same as default.
    #powermaincolor = powerchestcolor

    #bright colors for phazon suit colors 1&2 look REAL bad. Cap it to a certain brightness
    phazonheadcolor = np.array(phazonheadcolor) * 0.6
    phazonmaincolor = np.array(phazonmaincolor) * 0.8


    #set up all the image files that the atlas splits into.
    #The corresponding rects are defined up in recolor_suit.
    #All these filenames are given as dolphin custom texture names since that's the easiest way for me to test.
    #"Real" filenames and conversion to (and from?) the compressed format used by the game will have to be added when this is integrated.

    #the following filenames in order are:

    #full samus preview, 256x256 composite,
    #256x256 topleft, 256x256 topright,
    #256x256 bottomleft, 256x256 bottomright,
    #256x256 morphball, 256x256 spiderball
    #128x128 3rd person arm, #128x128 gravity shoulder, 64x64 gravity shoulder
    #64x64 visor 1, 64x64 visor 2,
    #64x64 visor 3, 64x64 visor 4,
    #64x64 shine 1, 64x64 shine 2, 64x64 shine 3,
    #128x128 glass dark, 128x128 glass bright, 64x64 spiderball line,
    #32x32 power visor 5

    powertexnames = ["preview-normal-1.png", "tex1_256x256_m_fba79698624fa6d5_14.png",
                "tex1_256x256_m_7ed9be20ef4fed55_14.png", "tex1_256x256_m_f5fcfccdfed56bd8_14.png",
                "tex1_256x256_m_6e76d486fc90efd4_14.png", "tex1_256x256_m_a61f3cc368a9c5fe_14.png",
                "tex1_256x256_m_8912adf818290b43_14.png", "", 
                "tex1_128x128_m_280f450554ef7706_14.png", "", "",
                "tex1_64x64_m_77e166fdb55187d8_14.png", "tex1_64x64_m_0419492b8934407f_14.png",
                "tex1_64x64_m_dc893b73a414cb4c_14.png", "",
                "tex1_64x64_m_4c1f4e1584953213_14.png", "", "",
                "", "", "",
                "tex1_32x32_m_7f5be2b873cb2a5b_14.png"]


    variatexnames = ["preview-normal-2.png", "tex1_256x256_m_e2abedcfa245f34a_14.png",
                "tex1_256x256_m_e50417cc89f6da17_14.png", "tex1_256x256_m_6b816c135d61fedf_14.png",
                "tex1_256x256_m_e54dec7509263ac3_14.png", "tex1_256x256_m_7a0241539f57e00a_14.png",
                "tex1_256x256_m_8557f218341331e7_14.png", "tex1_256x256_m_6d53290d9d04e634_14.png", 
                "tex1_128x128_m_028716ecc9868af9_14.png", "", "",
                "tex1_64x64_m_df40d29e98015bd0_14.png", "tex1_64x64_m_94a9f2e126592517_14.png",
                "tex1_64x64_m_dc893b73a414cb4c_14.png", "tex1_64x64_m_1f86871798bc6f66_14.png",
                "", "", "",
                "tex1_128x128_m_ac888c68e8016a5a_14.png", "tex1_128x128_m_7a96d73506a64aa8_14.png", "tex1_64x64_m_8263e8c124ae8da7_14.png",
                ""]

    gravitytexnames = ["preview-normal-3.png", "tex1_256x256_m_69bc2d04d6c6faae_14.png",
                "tex1_256x256_m_da817ef0f8338fa1_14.png", "tex1_256x256_m_2e96ffb547ec2103_14.png",
                "tex1_256x256_m_30614e5b942f77d9_14.png", "tex1_256x256_m_94c6e2799c1da72f_14.png",
                "", "tex1_256x256_m_61bd724c9101fa1b_14.png", 
                "tex1_128x128_m_a17b5f264c3f304e_14.png", "tex1_128x128_m_028c7cb584c3021a_14.png", "tex1_64x64_m_29d561b7be05f845_14.png",
                "tex1_64x64_m_1ff3e9d69d2d5c6d_14.png", "tex1_64x64_m_ac2e6e00c583698e_14.png",
                "tex1_64x64_m_30c21042f4da675e_14.png", "tex1_64x64_m_9860919f9decf6f4_14.png",
                "tex1_64x64_m_3cff94599a1dfdeb_14.png", "tex1_64x64_m_4b851c896c0b2422_14.png", "tex1_64x64_m_6c4e1270e0fc0ed8_14.png",
                "tex1_128x128_m_8d0b36522ce3a4de_14.png", "tex1_128x128_m_baddc0f7cd4fdba5_14.png", "tex1_64x64_m_7d07267436727c50_14.png",
                ""]

    powergradientcenters = [0.47, 0.57, 0.52, 0.52, 0.5]
    variagradientcenters = [0.47, 0.58, 0.52, 0.52, 0.5]
    gravitygradientcenters = [0.47, 0.32, 0.52, 0.52, 0.5]

    #phazon suit needs a completely different texture arrangement

    #full samus preview, 128x128 composite,
    #128x128 topleft, 128x128 topright,
    #128x128 bottomleft, 128x128 bottomright,
    #256x256 suit shine, 128x128 spiderball, 128x128 glow clouds
    #64x64 3rd person arm, 64x64 visor 1, 64x64 visor 2,
    #64x64 visor 3, 64x64 visor 4, 64x64 lights,
    #64x64 noise, 64x64 spiderball glow,
    #64x64 reflection map, 32x32 spiderball line
    #64x64 circle reflect 1, 64x64 circle reflect 2

    phazontexnames = ["preview-normal-4.png","tex1_128x128_m_c9f55a6fabc5198f_14.png",
                "tex1_128x128_m_6f5229898b196e5d_14.png","tex1_128x128_m_82e1b409dac4d327_14.png",
                "tex1_128x128_m_db45e945e2afa9ef_14.png","tex1_128x128_m_3d25f4e5acfa2c52_14.png",
                "tex1_256x256_m_4a16526bfe93d36d_14.png","tex1_128x128_m_f5b200dfea313720_14.png", "tex1_128x128_m_5ee7ebb7eeb3e737_14.png",
                "tex1_64x64_m_35f2fece808e0051_14.png", "tex1_64x64_m_005f4d9b757b9118_14.png","tex1_64x64_m_27d56f2744d5f9cf_14.png",
                "tex1_64x64_m_78d91fd55fb97ebb_14.png","tex1_64x64_m_121de930946cd9a0_14.png","tex1_64x64_m_c20d361c6b565727_14.png",
                "tex1_64x64_m_b9b5671d6d497284_14.png","tex1_64x64_m_c1edc9b118a856d5_14.png",
                "tex1_64x64_m_f3e75b2087f5bf7e_14.png","tex1_32x32_m_605c26ef6af1b5af_14.png",
                "tex1_64x64_m_6d377b9904ef6f8f_14.png", "tex1_64x64_m_1ce7d583ff26a85b_14.png"]

    phazongradientcenters = [0.25, 0.23, 0.5, 0.52, 0.52]


    #fusion suit

    #full samus preview,
    #256x256 helmet, 256x256 limbs,
    #256x256 torso, 256x256 morph ball,
    #128x128 helmet, 128x128 limbs, 128x128 torso,
    #128x128 orb dark, 128x128 orb light,
    #64x64 crystal, 64x64 visor

    #I don't know what the two orb textures are for. They seem to be loaded depending on the suit (except phazon?), but even changing the file to pure yellow or pure magenta, i don't see a difference. I included them for completeness just in case

    fusionpowertexnames = ["preview-fusion-1.png",
                           "tex1_256x256_m_98398abbeb14ad5c_14.png", "tex1_256x256_m_33d357fc8ed87a91_14.png",
                           "tex1_256x256_m_37c07bb6066e6b73_14.png", "tex1_256x256_m_d0de03e78b8ca40c_14.png",
                           "tex1_128x128_m_9ae763e15595297a_14.png", "tex1_128x128_m_4bed5052fb55a6ac_14.png", "tex1_128x128_m_9483e027dcc720d7_14.png",
                           "tex1_128x128_m_8d0b36522ce3a4de_14.png", "tex1_128x128_m_baddc0f7cd4fdba5_14.png",
                           "tex1_64x64_m_aac358eb2f216ded_14.png", "tex1_64x64_m_e8fab6f3e8dec6ce_14.png"]

    fusionvariatexnames = ["preview-fusion-2.png",
                           "tex1_256x256_m_d59284a25ec08045_14.png", "tex1_256x256_m_575326dfc6c903a5_14.png",
                           "tex1_256x256_m_6053890577f8025c_14.png", "tex1_256x256_m_dff4440b8e0ee5e8_14.png",
                           "tex1_128x128_m_0606265cd2571d98_14.png", "tex1_128x128_m_0af0a48dea260a14_14.png", "tex1_128x128_m_68158da962ba5af1_14.png",
                           "tex1_128x128_m_ac888c68e8016a5a_14.png", "tex1_128x128_m_7a96d73506a64aa8_14.png",
                           "tex1_64x64_m_aac358eb2f216ded_14.png", "tex1_64x64_m_e8fab6f3e8dec6ce_14.png"]

    fusiongravitytexnames = ["preview-fusion-3.png",
                           "tex1_256x256_m_7253c29756b07735_14.png", "tex1_256x256_m_a25882f5c8996274_14.png",
                           "tex1_256x256_m_25b4a0aaeb45f6af_14.png", "tex1_256x256_m_b858440daa0c6092_14.png",
                           "tex1_128x128_m_35c9657b63c0cac3_14.png", "tex1_128x128_m_1a76eeed42508f5c_14.png", "tex1_128x128_m_bc096a6a3653a3be_14.png",
                           "tex1_128x128_m_8d0b36522ce3a4de_14.png", "tex1_128x128_m_baddc0f7cd4fdba5_14.png",
                           "tex1_64x64_m_aac358eb2f216ded_14.png", "tex1_64x64_m_e8fab6f3e8dec6ce_14.png"]

    fusionphazontexnames = ["preview-fusion-4.png",
                           "tex1_256x256_m_d73531e5490260df_14.png", "tex1_256x256_m_eb57a51c23401ac4_14.png",
                           "tex1_256x256_m_80f33541e7a71329_14.png", "tex1_256x256_m_ebb4bc75133051d6_14.png",
                           "tex1_128x128_m_f91594d34a48f503_14.png", "tex1_128x128_m_507216dccf41f81c_14.png", "tex1_128x128_m_d6cee3f3769a6daf_14.png",
                           "", "",
                           "tex1_64x64_m_aac358eb2f216ded_14.png", "tex1_64x64_m_e8fab6f3e8dec6ce_14.png"]

    fusionpowergradientcenters = [0.5, 0.5, 0.6, 0.5, 0.7]
    fusionvariagradientcenters = [0.5, 0.6, 0.6, 0.5, 0.7]
    fusiongravitygradientcenters = [0.5, 0.48, 0.6, 0.5, 0.7]
    fusionphazongradientcenters = [0.5, 0.56, 0.6, 0.5, 0.7]


    #do the actual recoloring, once per suit.
    if suits_to_recolor[0]: recolor_suit("power", "mask-power", [powerheadcolor, powermaincolor, powerchestcolor, powervisorcolor, [0, 0, 0]], powergradientcenters, powertexnames)
    if suits_to_recolor[1]: recolor_suit("varia", "mask-normal", [variaheadcolor, variamaincolor, variachestcolor, variavisorcolor, [0, 0, 0]], variagradientcenters, variatexnames)
    if suits_to_recolor[2]: recolor_suit("gravity", "mask-normal", [gravityheadcolor, gravitymaincolor, gravitychestcolor, gravityvisorcolor, [0, 0, 0]], gravitygradientcenters, gravitytexnames)
    if suits_to_recolor[3]: recolor_suit("phazon", "mask-phazon", [phazonheadcolor, phazonmaincolor, [0, 0, 0], phazonvisorcolor, phazonmisccolor], phazongradientcenters, phazontexnames)

    if suits_to_recolor[4]: recolor_suit("fusion-power", "mask-fusion", [fusionpowerheadcolor, fusionpowermaincolor, fusionpowerchestcolor, fusionallvisorcolor, fusionallmisccolor], fusionpowergradientcenters, fusionpowertexnames)
    if suits_to_recolor[5]: recolor_suit("fusion-varia", "mask-fusion", [fusionvariaheadcolor, fusionvariamaincolor, fusionvariachestcolor, fusionallvisorcolor, fusionallmisccolor], fusionvariagradientcenters, fusionvariatexnames)
    if suits_to_recolor[6]: recolor_suit("fusion-gravity", "mask-fusion", [fusiongravityheadcolor, fusiongravitymaincolor, fusiongravitychestcolor, fusionallvisorcolor, fusionallmisccolor], fusiongravitygradientcenters, fusiongravitytexnames)
    if suits_to_recolor[7]: recolor_suit("fusion-phazon", "mask-fusion", [fusionphazonheadcolor, fusionphazonmaincolor, fusionphazonchestcolor, fusionallvisorcolor, fusionallmisccolor], fusionphazongradientcenters, fusionphazontexnames)
