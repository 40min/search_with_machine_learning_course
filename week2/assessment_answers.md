### For deriving synonyms from content: What were the results for your best model in the tokens used for evaluation?

```
- headphones:
earbud 0.899972
ear 0.88813
bud 0.671404
noise 0.6599
over 0.640875
skullcandy 0.587565
beats 0.561357
gumy 0.554397
sennheiser 0.551753
headset 0.527433

- laptop:
notebook 0.745962
laptops 0.730261
notebooks 0.592191
netbook 0.584632
briefcase 0.537566
netbooks 0.531382
macbook 0.50916
inspiron 0.503887
pc 0.498431
mouse 0.485129

- freezer:
freezers 0.796867
refrigerators 0.771283
refrigerator 0.76662
frost 0.668437
side 0.651033
ft 0.648997
cu 0.642417
bottom 0.616045
top 0.54612
monochromatic 0.537388

- nintendo
ds 0.946881
wii 0.907238
3ds 0.790215
psp 0.731942
advance 0.669693
playstation 0.656075
boy 0.652551
dsi 0.644902
gamecube 0.642548
ps3 0.616587

- whirlpool:
maytag 0.816705
biscuit 0.754196
frigidaire 0.731765
ge 0.692659
electrolux 0.652373
bisque 0.649213
bosch 0.628687
kitchenaid 0.626103
profile 0.602098
white 0.599121

- kodak

easyshare 0.814588
canon 0.608819
powershot 0.520018
finepix 0.519011
photosmart 0.511648
olympus 0.501548
share 0.49486
coolpix 0.494714
camera 0.487998
everio 0.486778

- ps2:
playstation 0.782187
ps3 0.667218
xbox 0.656355
gamecube 0.649255
360 0.625881
wii 0.622439
outdoors 0.616798
psp 0.616654
guides 0.613106
nintendo 0.608216

- razr:
razer 0.874194
gaming 0.567933
geek 0.448754
dragon 0.445144
squad 0.442885
geforce 0.441383
optoma 0.422339
wrist 0.416026
rate 0.415031
radeon 0.407621

- stratocaster:
toaster 0.648975
roaster 0.639571
strategy 0.633412
toasters 0.601316
slice 0.594157
cooker 0.590073
pots 0.58826
string 0.58722
pizza 0.579954
crock 0.574894

- holiday:
day 0.591069
miami 0.58057
carolina 0.567497
solid 0.551713
florida 0.551666
birthday 0.544539
chicago 0.543806
schedule 0.541469
panthers 0.53944
iowa 0.533343

- plasma:
600hz 0.668656
flat 0.635097
tvs 0.626769
panel 0.620513
televisions 0.569991
46 0.55295
32 0.548793
dlp 0.543857
47 0.5326
42 0.518323

- leather:
recliner 0.593814
executive 0.548056
case 0.52965
curved 0.509415
seating 0.504553
berkline 0.50379
theaterseatstore 0.490908
cases 0.479517
brown 0.468735
slip 0.452673

```


### For classifying reviews: How did you transform the review content?

I've tries several approaches, but none of them wrked better than just title + ' ' + comment.
Here some results
```
title
N       10000
P@1     0.633
R@1     0.633

comment
N       10000
P@1     0.639
R@1     0.639

both
N       10000
P@1     0.677
R@1     0.677

rating grades
N       10000
P@1     0.675
R@1     0.675

normalisaton
N       10000
P@1     0.64
R@1     0.64

skipping some word-types (all except)
N       10000
P@1     0.637
R@1     0.637
```