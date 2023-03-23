### For query classification: How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 1000? To 10000?
* 1000 - 322
* 10000 - 45

### For query classification: What were the best values you achieved for R@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category, as well as trying different fastText parameters or query normalization. Report at least 2 of your runs.

###### min_queries 100
 lr 0.5

* R@1     0.518
* R@2     0.64
* R@3     0.704
* R@5     0.768

lr 0.4  -epoch 25

* R@1     0.512
* R@2     0.64
* R@3     0.701
* R@5     0.765

lr 0.5  -epoch 25 -wordNgrams 2
* R@1     0.511
* R@2     0.64
* R@3     0.707
* R@5     0.771

###### min_queries 1000

lr 0.5
* P@1     0.546
* R@1     0.546
* R@2     0.674
* R@3     0.732
* R@5     0.788

lr 0.5  -epoch 25 -wordNgrams 2
* N       10000
* P@1     0.538
* R@1     0.538
* R@2     0.662
* R@3     0.727
* R@5     0.785

###### min_queries 10000 (normalisation is lowercase only)

lr 0.5  -epoch 25 -wordNgrams 2
* P@1     0.669
* R@1     0.669
* R@2     0.793
* R@3     0.844
* R@5     0.89


###### min_queries 10000 (normalisation is lowercasing + remove all except alphadigits + stemming)

lr 0.5  -epoch 25 -wordNgrams 2
* N       10000
* P@1     0.637
* R@1     0.637
* R@2     0.792
* R@3     0.843
* R@5     0.892

Weird, seems normalisation with lowercase is good enough in compare to other tricks


### For integrating query classification with search: Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.

---
###### query: tv
* classified to abcat0101001 (All Flat-Panel TVs)
* results w/o filtering: 
[
    [
        "Apple® - Apple TV®"
    ],
    [
        "Monster Cable - TV Screen Cleaning Kit"
    ],
    [
        "KCPI - Digital TV Converter Box"
    ],
    [
        "Magnavox - 15\" HD-Ready LCD TV w/HD Component Video Inputs"
    ],
    [
        "Studio RTA - TV Stand for Tube TVs Up to 27\""
    ],
    [
        "Dynex® - 20\" 480i Standard-Definition Digital TV/DVD Combo"
    ],
    [
        "NETGEAR - NeoTV Wireless Media Player"
    ],
    [
        "Western Digital - WD TV Live Media Player"
    ],
    [
        "Acer - S1 Series 20\" Widescreen Flat-Panel LED HD Monitor - Black"
    ],
    [
        "Rocketfish™ - Low-Profile Tilting Wall Mount for Most 32\" to 70\" Flat-Panel TVs - Black"
    ]
]
* results with filtering: all TVs!
[
    [
        "Magnavox - 15\" HD-Ready LCD TV w/HD Component Video Inputs"
    ],
    [
        "Insignia® - 19\" 720p Widescreen Flat-Panel LCD HDTV"
    ],
    [
        "Toshiba - 32\" Class - LCD - 720p - 60Hz - HDTV"
    ],
    [
        "Samsung - 22\" Class - LED - 1080p - 60Hz - HDTV"
    ],
    [
        "Insignia™ - 32\" Class / LCD / 720p / 60Hz / HDTV"
    ],
    [
        "Insignia™ - 40\" Class - LCD - 1080p - 60Hz - HDTV"
    ],
    [
        "Samsung - 32\" Class - LED - 720p - 60Hz - HDTV"
    ],
    [
        "Westinghouse - 32\" Class / LED / 720p / 60Hz / HDTV"
    ],
    [
        "Dynex™ - 32\" Class / LCD / 720p / 60Hz / HDTV"
    ],
    [
        "Samsung - 32\" Class - LCD -720p - 60Hz - HDTV"
    ]
]

###### query: canon
* classified as: 'abcat0401004' (Fun Basic Cameras) and 'pcmcat180400050000' (DSLR Body & Lens)
* w/o filtering: has printers, ink tank etc

[
    [
        "Canon - PIXMA Photo Printer"
    ],
    [
        "Canon - PowerShot A2300 16.0-Megapixel Digital Camera - Black"
    ],
    [
        "Canon - 55-250mm f/4-5.6 Telephoto Zoom Lens for Select Canon Cameras"
    ],
    [
        "Canon - PowerShot 5.0MP Digital Camera"
    ],
    [
        "Canon - PG-210XL Photo Ink Tank - Black"
    ],
    [
        "Canon - PowerShot SX260 HS 12.1-Megapixel Digital Camera - Black"
    ],
    [
        "Canon - PowerShot ELPH 110 HS 16.1-Megapixel Digital Camera - Black"
    ],
    [
        "Canon - All-In-One Photo Printer/ Copier/ Scanner"
    ],
    [
        "Canon - CLI-226 ChromaLife100+ Ink Tank - Black"
    ],
    [
        "Canon - PGI-225/CLI-226 ChromaLife100+ Ink Tank 4-Pack - Black/Cyan/Magenta/Yellow"
    ]
]
* with filtering: cameras only

[
	[
		"Canon - PowerShot A2300 16.0-Megapixel Digital Camera - Black"
	],
	[
		"Canon - PowerShot 5.0MP Digital Camera"
	],
	[
		"Canon - PowerShot SX260 HS 12.1-Megapixel Digital Camera - Black"
	],
	[
		"Canon - PowerShot ELPH 110 HS 16.1-Megapixel Digital Camera - Black"
	],
	[
		"Canon - EOS Rebel T3i 18.0-Megapixel DSLR Camera with 18-55mm Lens - Black"
	],
	[
		"Canon - PowerShot A2300 16.0-Megapixel Digital Camera - Red"
	],
	[
		"Canon - PowerShot A4000 IS 16.0-Megapixel Digital Camera - Blue"
	],
	[
		"Canon - EOS Digital Rebel T3 12.2-Megapixel Digital SLR Camera Kit"
	],
	[
		"Canon - PowerShot 4.0MP Digital Camera"
	],
	[
		"Canon - PowerShot A4000 IS 16.0-Megapixel Digital Camera - Silver"
	]
]
---

### For integrating query classification with search: Give 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.

---
###### query: apple

* model: query_category_model100.bin & query_category_model100.bin
* classified as: cat02015 (Movies & TV Shows)
* results: no

!!! but improved with model query_category_model1000.bin
* classified as: pcmcat247400050001 (MacBooks) and pcmcat209000050007 (iPad) -- it was below threshold of 0.5
* results: top10 
###### w/o filtering
[
	[
		"Apple® - Apple TV®"
	],
	[
		"Apple® - Earbuds for Select Apple® iPod® Models"
	],
	[
		"Apple - $15 iTunes Gift Card"
	],
	[
		"Apple - $25 iTunes Gift Card"
	],
	[
		"Apple® - USB Power Adapter for Apple® iPad™"
	],
	[
		"Apple® - iPod touch® 8GB* MP3 Player (4th Generation - Latest Model) - White"
	],
	[
		"Zagg - InvisibleSHIELD HD for Apple® iPad® (3rd Generation)"
	],
	[
		"Apple® - iPad® 2 with Wi-Fi - 16GB - Black"
	],
	[
		"Apple® - iPad™ Digital Camera Connection Kit"
	],
	[
		"Apple® - Digital A/V Adapter"
	]
]

###### w filtering

[
	[
		"Apple® - iPad® 2 with Wi-Fi - 16GB - Black"
	],
	[
		"Apple® - iPad® 2 with Wi-Fi - 16GB - White"
	],
	[
		"Apple® - The new iPad® with Wi-Fi - 16GB - White"
	],
	[
		"Apple® - The new iPad® with Wi-Fi - 16GB - Black"
	],
	[
		"Apple® - MacBook® Pro - 13.3\" Display - 4GB Memory - 500GB Hard Drive"
	],
	[
		"Apple® - The new iPad® with Wi-Fi - 32GB - Black"
	],
	[
		"Apple® - The new iPad® with Wi-Fi - 32GB - White"
	],
	[
		"Apple® - The new iPad® with Wi-Fi - 64GB - Black"
	],
	[
		"Apple® - MacBook® Pro - 13.3\" Display - 8GB Memory - 750GB Hard Drive"
	],
	[
		"Apple® - MacBook Air® - 13.3\" Display - 4GB Memory - 128GB Flash Storage"
	]
]

---
###### query: cameras
* classified as: 'cat02015' (Movies & TV Shows)
* results top10

###### w/o filtering:
[
	[
		"DigiPower - NKL12 Rechargeable Lithium-Ion Battery for Select Nikon CoolPix Digital Cameras"
	],
	[
		"Canon - 55-250mm f/4-5.6 Telephoto Zoom Lens for Select Canon Cameras"
	],
	[
		"DigiPower - CN6L Rechargeable Lithium-Ion Battery for Select Canon PowerShot Digital Cameras"
	],
	[
		"Nikon - 55-200mm Vibration Reduction Zoom Lens for Nikon DX SLR Cameras"
	],
	[
		"Nikon - Rechargeable Lithium-Ion Battery for Nikon D3100 Digital Cameras"
	],
	[
		"Kodak - EasyShare 7.1-Megapixel Digital Camera - Black"
	],
	[
		"HP - Photosmart 7.2MP Digital Camera - White"
	],
	[
		"Apple® - iPad™ Digital Camera Connection Kit"
	],
	[
		"Lowepro - Tahoe 30 Digital Camera Bag - Black"
	],
	[
		"Kodak - EasyShare 5.0MP Digital Camera - Pink"
	]
]

###### w filtering:
[]