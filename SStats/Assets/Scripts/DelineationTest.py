﻿import sys
import traceback
#import datetime
import os
import argparse
import arcpy
#import shutil
import json
#from arcpy.sa import *
#import arcpy.cartography as CA
#import logging
#import re


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
class DelineationWrapper(object):
    #region Constructor
    def __init__(self):
        regionID =""
        pourpoint= None
        simplification = 1
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
            parser.add_argument("-stabbr", help="specifies the abbr state name to perform delineation", type=str, default="IA")
            parser.add_argument("-pourpoint", help="specifies the json representation of an esri point feature collection ", type=json.loads, 
                                default = '[-93.7364137172699,42.306129898064221]')
            parser.add_argument("-pourpointwkid", help="specifies the esri well known id of pourpoint ", type=str, 
                                default = '4326')
          
            parser.add_argument("-simplification", help="specifies the simplify method to, 1 = full, 2 = simplified", type=int, choices=[1,2], default = 1)
            parser.add_argument("-processSR", help="specifies the spatial ref to perform operation", type=int, default = 4326)
                
            args = parser.parse_args()

            Results = {"PourPoint": {"fields": [{"alias": "OBJECTID", "type": "esriFieldTypeOID", "name": "OBJECTID"}, {"alias": "HydroID", "type": "esriFieldTypeInteger", "name": "HydroID"}, {"alias": "DrainID", "type": "esriFieldTypeInteger", "name": "DrainID"}, {"alias": "Name", "length": 25, "type": "esriFieldTypeString", "name": "Name"}, {"alias": "Descript", "length": 25, "type": "esriFieldTypeString", "name": "Descript"}, {"alias": "ReachCode", "length": 15, "type": "esriFieldTypeString", "name": "ReachCode"}, {"alias": "Measure", "type": "esriFieldTypeDouble", "name": "Measure"}, {"alias": "Latitude", "type": "esriFieldTypeDouble", "name": "Latitude"}, {"alias": "Longitude", "type": "esriFieldTypeDouble", "name": "Longitude"}, {"alias": "HUCID", "length": 25, "type": "esriFieldTypeString", "name": "HUCID"}], "displayFieldName": "", "geometryType": "esriGeometryPoint", "features": [{"geometry": {"y": 42.30609446500006, "x": -93.73641326299997}, "attributes": {"Name": "T2014121131250", "OBJECTID": 1, "Descript": "P07080105", "Longitude": -93.7364, "DrainID": 2, "HUCID": "07080105", "HydroID": 1, "Measure": None, "Latitude": 42.3061, "ReachCode": None}}], "spatialReference": {"wkid": 4326, "latestWkid": 4326}}, "Message": "INFO:Initialized_INFO:Delineation Started_INFO:creating workspace environment. D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb_INFO:Starting Delineation_AHMSG:Executing: StreamstatsGlobalWatershedDelineation in memory\\FC D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers\\GlobalWatershedRaw D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers\\GlobalWatershedPoint D:\\gistemp\\ClientData\\IA20141201131238376000\\Temp\\StreamStatsIA.xml CLEARFEATURES NO IA20141201131238376000 Start Time: Mon Dec 01 13:12:45 2014 Delineating global watershed for batchpoint 1 of 1.  dt=0.03s 1 global watershed(s) successfully delineated. Succeeded at Mon Dec 01 13:12:51 2014 (Elapsed Time: 6.00 seconds)_INFO:finished Delineation., removing holes_INFO:Executing: EliminatePolygonPart D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers\\GlobalWatershedRaw D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers\\GlobalWatershed AREA OR PERCENT \"1000 SquareMeters\" 1 CONTAINED ONLY Start Time: Mon Dec 01 13:12:55 2014 Succeeded at Mon Dec 01 13:12:55 2014 (Elapsed Time: 0.00 seconds)_INFO:Finished_", "Watershed": {"fields": [{"alias": "OBJECTID", "type": "esriFieldTypeOID", "name": "OBJECTID"}, {"alias": "HydroID", "type": "esriFieldTypeInteger", "name": "HydroID"}, {"alias": "DrainID", "type": "esriFieldTypeInteger", "name": "DrainID"}, {"alias": "Name", "length": 25, "type": "esriFieldTypeString", "name": "Name"}, {"alias": "Descript", "length": 25, "type": "esriFieldTypeString", "name": "Descript"}, {"alias": "GlobalWshd", "type": "esriFieldTypeInteger", "name": "GlobalWshd"}, {"alias": "RELATEDOIDS", "length": 250, "type": "esriFieldTypeString", "name": "RELATEDOIDS"}, {"alias": "WarningMsg", "length": 250, "type": "esriFieldTypeString", "name": "WarningMsg"}, {"alias": "DRNAREA", "type": "esriFieldTypeDouble", "name": "DRNAREA"}, {"alias": "M1D10Y", "type": "esriFieldTypeDouble", "name": "M1D10Y"}, {"alias": "M7D10Y", "type": "esriFieldTypeDouble", "name": "M7D10Y"}, {"alias": "M30D10Y", "type": "esriFieldTypeDouble", "name": "M30D10Y"}, {"alias": "M30D5Y", "type": "esriFieldTypeDouble", "name": "M30D5Y"}, {"alias": "M1D10Y1012", "type": "esriFieldTypeDouble", "name": "M1D10Y1012"}, {"alias": "M7D10Y1012", "type": "esriFieldTypeDouble", "name": "M7D10Y1012"}, {"alias": "QAH", "type": "esriFieldTypeDouble", "name": "QAH"}, {"alias": "KSATSSUR", "type": "esriFieldTypeDouble", "name": "KSATSSUR"}, {"alias": "STREAM_VAR", "type": "esriFieldTypeDouble", "name": "STREAM_VAR"}, {"alias": "DRNFREQ", "type": "esriFieldTypeDouble", "name": "DRNFREQ"}, {"alias": "BFI", "type": "esriFieldTypeDouble", "name": "BFI"}, {"alias": "SOILASSURGO", "type": "esriFieldTypeDouble", "name": "SOILASSURGO"}, {"alias": "SOILBSSURGO", "type": "esriFieldTypeDouble", "name": "SOILBSSURGO"}, {"alias": "SOILCSSURGO", "type": "esriFieldTypeDouble", "name": "SOILCSSURGO"}, {"alias": "SOILDSSURGO", "type": "esriFieldTypeDouble", "name": "SOILDSSURGO"}, {"alias": "RSD", "type": "esriFieldTypeDouble", "name": "RSD"}, {"alias": "PRECIP", "type": "esriFieldTypeDouble", "name": "PRECIP"}, {"alias": "HYSEP", "type": "esriFieldTypeDouble", "name": "HYSEP"}, {"alias": "I24H10Y", "type": "esriFieldTypeDouble", "name": "I24H10Y"}, {"alias": "CCM", "type": "esriFieldTypeDouble", "name": "CCM"}, {"alias": "DESMOIN", "type": "esriFieldTypeDouble", "name": "DESMOIN"}, {"alias": "FOS", "type": "esriFieldTypeDouble", "name": "FOS"}, {"alias": "STRMTOT", "type": "esriFieldTypeDouble", "name": "STRMTOT"}, {"alias": "BASLEN", "type": "esriFieldTypeDouble", "name": "BASLEN"}, {"alias": "CSL10_85", "type": "esriFieldTypeDouble", "name": "CSL10_85"}, {"alias": "TAU_ANN", "type": "esriFieldTypeDouble", "name": "TAU_ANN"}, {"alias": "PK2", "type": "esriFieldTypeDouble", "name": "PK2"}, {"alias": "PK5", "type": "esriFieldTypeDouble", "name": "PK5"}, {"alias": "PK10", "type": "esriFieldTypeDouble", "name": "PK10"}, {"alias": "PK25", "type": "esriFieldTypeDouble", "name": "PK25"}, {"alias": "PK50", "type": "esriFieldTypeDouble", "name": "PK50"}, {"alias": "PK100", "type": "esriFieldTypeDouble", "name": "PK100"}, {"alias": "PK200", "type": "esriFieldTypeDouble", "name": "PK200"}, {"alias": "PK500", "type": "esriFieldTypeDouble", "name": "PK500"}, {"alias": "Edited", "type": "esriFieldTypeInteger", "name": "Edited"}, {"alias": "BSHAPE", "type": "esriFieldTypeDouble", "name": "BSHAPE"}, {"alias": "NSSREGNO", "type": "esriFieldTypeInteger", "name": "NSSREGNO"}, {"alias": "IMPNLCD01", "type": "esriFieldTypeDouble", "name": "IMPNLCD01"}, {"alias": "URBNLCD01", "type": "esriFieldTypeDouble", "name": "URBNLCD01"}, {"alias": "HUCID", "length": 25, "type": "esriFieldTypeString", "name": "HUCID"}, {"alias": "ORIG_FID", "type": "esriFieldTypeInteger", "name": "ORIG_FID"}, {"alias": "Shape_Length", "type": "esriFieldTypeDouble", "name": "Shape_Length"}, {"alias": "Shape_Area", "type": "esriFieldTypeDouble", "name": "Shape_Area"}], "displayFieldName": "", "geometryType": "esriGeometryPolygon", "features": [{"geometry": {"rings": [[[-93.73658631999996, 42.305327833000035], [-93.73658316999996, 42.30505767000005], [-93.73646185199999, 42.30505844900006], [-93.73645975299996, 42.30487834100006], [-93.73633843499994, 42.30487912000007], [-93.73633738499996, 42.30478906500008], [-93.73609474899996, 42.30479062300003], [-93.73609369999997, 42.30470056900003], [-93.73585106499996, 42.30470212600005], [-93.73585001599997, 42.304612071000065], [-93.73572869799995, 42.30461285000007], [-93.73572764999994, 42.304522795000025], [-93.73560633199997, 42.30452357400003], [-93.73560318699998, 42.30425341000006], [-93.73548186999994, 42.30425418900006], [-93.73547977399994, 42.30407408000008], [-93.73535845699996, 42.304074858000035], [-93.73535112099995, 42.30344447600004], [-93.73522980599995, 42.30344525400005], [-93.73522875799995, 42.303355200000055], [-93.73510744299995, 42.30335597800007], [-93.73510639499995, 42.303265923000026], [-93.73498507999994, 42.30326670100004], [-93.73498403299999, 42.303176646000054], [-93.73486271799999, 42.30317742400007], [-93.73486062299997, 42.30299731500003], [-93.73498193799998, 42.30299653700007], [-93.73497984299996, 42.30281642800003], [-93.73522247099999, 42.302814873000045], [-93.73522142299998, 42.30272481900005], [-93.73546405099995, 42.302723263000075], [-93.73546300299995, 42.30263320800003], [-93.73558431699996, 42.302632430000074], [-93.73558221999997, 42.30245232100003], [-93.73582484699995, 42.30245076500006], [-93.73582274999995, 42.302270656000076], [-93.73594406299998, 42.30226987700007], [-93.73593776999996, 42.30172955000006], [-93.73581645799999, 42.301730329000065], [-93.73580597199998, 42.30082978400003], [-93.73568466199998, 42.300830562000044], [-93.73568256499999, 42.30065045300006], [-93.73556125499994, 42.300651231000074], [-93.73555706199994, 42.30029101300005], [-93.73543575299999, 42.30029179100006], [-93.73543051299998, 42.29984151900004], [-93.73555182199999, 42.299840741000025], [-93.73554448499999, 42.29921035900003], [-93.73566579199996, 42.29920958100007], [-93.73566264699997, 42.29893941700004], [-93.73578395399994, 42.29893863900003], [-93.73578290499995, 42.29884858500003], [-93.73590421199998, 42.298847806000026], [-93.73590316299999, 42.29875775200003], [-93.73602446899997, 42.298756973000025], [-93.73602027399994, 42.298396755000056], [-93.73614157999998, 42.29839597600005], [-93.73614053099999, 42.298305922000054], [-93.73638314199997, 42.298304364000046], [-93.73638419099996, 42.29839441900003], [-93.73650549699994, 42.29839364000003], [-93.73650444699996, 42.29830358500004], [-93.73662575299994, 42.29830280600004], [-93.73662260399999, 42.29803264200007], [-93.73674390899998, 42.29803186300006], [-93.73674285899995, 42.297941809000065], [-93.73686416399994, 42.29794102900007], [-93.73686311399996, 42.297850975000074], [-93.73698441899995, 42.29785019500008], [-93.73698336799998, 42.297760141000026], [-93.73710467299998, 42.29775936100003], [-93.73710362199995, 42.297669306000046], [-93.73722492699994, 42.29766852700004], [-93.73722282599994, 42.29748841800006], [-93.73734412999994, 42.297487638000064], [-93.73734307899997, 42.29739758300008], [-93.73746438299997, 42.29739680300003], [-93.73746333199995, 42.29730674900003], [-93.73794854599998, 42.297303627000076], [-93.73794959699995, 42.29739368200006], [-93.73807090099996, 42.29739290100008], [-93.73806879799997, 42.29721279200004], [-93.73819010099999, 42.297212011000056], [-93.73818484199995, 42.29676173900003], [-93.73830614499997, 42.29676095800005], [-93.73830193699996, 42.29640074000008], [-93.73842323799994, 42.29639995900004], [-93.73842218599998, 42.296309904000054], [-93.73866478899998, 42.29630834200003], [-93.73866057999999, 42.29594812400006], [-93.73878188099997, 42.295947342000034], [-93.73878082799996, 42.295857288000036], [-93.73890212899994, 42.295856506000064], [-93.73890107599999, 42.295766452000066], [-93.73877977499995, 42.29576723300005], [-93.73877872299994, 42.29567717900005], [-93.73890002299999, 42.29567639700008], [-93.73889896999998, 42.295586343000025], [-93.73926287099994, 42.29558399700005], [-93.73926181699994, 42.295493943000054], [-93.73938311699999, 42.295493161000024], [-93.73938206399998, 42.29540310600004], [-93.73950336399997, 42.295402324000065], [-93.73950230999998, 42.29531227000007], [-93.73974490899997, 42.29531070500008], [-93.73974069399998, 42.29495048700005], [-93.73986199299998, 42.29494970400003], [-93.73986093799994, 42.294859650000035], [-93.74010353599994, 42.294858084000055], [-93.74010248099995, 42.29476803000006], [-93.74058767599996, 42.29476489700005], [-93.74058873099995, 42.29485495200004], [-93.74083132799996, 42.29485338500007], [-93.74083027299997, 42.29476333000008], [-93.74107286999998, 42.294761763000054], [-93.74107181399995, 42.29467170800007], [-93.74119311199996, 42.29467092500005], [-93.74119099999996, 42.294490816000064], [-93.74131229799997, 42.294490031000066], [-93.74131335499999, 42.29458008600005], [-93.74143465299994, 42.294579302000045], [-93.74143570899997, 42.29466935600004], [-93.74131441099996, 42.29467014000005], [-93.74131546699994, 42.29476019500004], [-93.74143676499995, 42.29475941100003], [-93.74144310399998, 42.29529973800004], [-93.74156440299998, 42.29529895300004], [-93.74156545999995, 42.29538900800003], [-93.74168675999994, 42.29538822300003], [-93.74168781599997, 42.295478278000076], [-93.74180911599996, 42.29547749300008], [-93.74181017299998, 42.295567548000065], [-93.74193147299997, 42.29556676300007], [-93.74193252999999, 42.295656817000065], [-93.74205382999997, 42.29565603200007], [-93.74205488799998, 42.295746087000055], [-93.74217618799997, 42.29574530200006], [-93.74217830299995, 42.29592541100004], [-93.74229960399998, 42.295924626000044], [-93.74230066099994, 42.29601468000004], [-93.74242196199998, 42.296013895000044], [-93.74242301999999, 42.29610394900004], [-93.74230171899995, 42.29610473500003], [-93.74230806499997, 42.29664506100005], [-93.74242936699994, 42.29664427600005], [-93.74243148299996, 42.296824385000036], [-93.74255278499999, 42.29682359900005], [-93.74255807499998, 42.29727387100007], [-93.74267937899998, 42.297273086000075], [-93.74268149499994, 42.29745319500006], [-93.74280279899995, 42.29745240900007], [-93.74280597399996, 42.297722572000055], [-93.74304858199997, 42.29772100000008], [-93.74304752399996, 42.29763094600003], [-93.74341143599997, 42.29762858700008], [-93.74340931699999, 42.297448479000025], [-93.74353062099999, 42.29744769200005], [-93.74352956099995, 42.29735763800005], [-93.74389347199997, 42.297355278000055], [-93.74389241199998, 42.29726522300007], [-93.74401371499994, 42.297264436000034], [-93.74401265499995, 42.29717438200004], [-93.74413395799996, 42.29717359500006], [-93.74413289799998, 42.297083540000074], [-93.74425419999994, 42.29708275300004], [-93.74425313999996, 42.29699269900004], [-93.74437444299997, 42.29699191200007], [-93.74437338199994, 42.29690185700008], [-93.74449468499995, 42.29690107000005], [-93.74449362399997, 42.29681101500006], [-93.74473622899995, 42.29680944000006], [-93.74473516699999, 42.29671938600006], [-93.74485646999995, 42.29671859800004], [-93.74485434699994, 42.296538489000056], [-93.74509695099994, 42.29653691300007], [-93.74509482699995, 42.29635680400003], [-93.74521612899997, 42.29635601600006], [-93.74521506699995, 42.296265962000064], [-93.74533636799998, 42.29626517300005], [-93.74533530599996, 42.296175119000054], [-93.74545660799998, 42.29617433000004], [-93.74545448299995, 42.29599422200005], [-93.74569708499996, 42.29599264400008], [-93.74569602199995, 42.295902590000026], [-93.74581732299998, 42.29590180100007], [-93.74581625999997, 42.29581174700007], [-93.74593756099995, 42.29581095800006], [-93.74593649799999, 42.295720903000074], [-93.74605779799998, 42.29572011400006], [-93.74605673499997, 42.295630060000065], [-93.74617803499996, 42.29562927100005], [-93.74617697199994, 42.295539216000066], [-93.74629827199999, 42.295538427000054], [-93.74629720899998, 42.295448373000056], [-93.74653980799997, 42.29544679400004], [-93.74654087199997, 42.29553684800004], [-93.74666217199996, 42.29553605800004], [-93.74666429899997, 42.29571616700008], [-93.74690689999994, 42.29571458700008], [-93.74690796399994, 42.295804641000075], [-93.74702926399999, 42.29580385100007], [-93.74703565099998, 42.29634417700004], [-93.74715695199995, 42.296343387000036], [-93.74715801699995, 42.29643344100003], [-93.74727931799998, 42.29643265100003], [-93.74728038299997, 42.29652270500003], [-93.74764428799995, 42.296520333000046], [-93.74764535299994, 42.29661038800003], [-93.74752405099997, 42.296611178000035], [-93.74752724699994, 42.29688134100007], [-93.74704203699997, 42.29688450300006], [-93.74704310099997, 42.296974558000045], [-93.74692179899995, 42.296975348000046], [-93.74692392699995, 42.29715545600004], [-93.74680262399994, 42.29715624700003], [-93.74680475299994, 42.29733635500003], [-93.74692605599995, 42.297335565000026], [-93.74692924899995, 42.297605728000065], [-93.74705055299995, 42.29760493800006], [-93.74705161699995, 42.29769499200006], [-93.74717292099996, 42.29769420200006], [-93.74717824399994, 42.298144473000036], [-93.74729954899999, 42.298143683000035], [-93.74730061399998, 42.29823373700003], [-93.74742191899998, 42.29823294700003], [-93.74742298399997, 42.29832300100003], [-93.74754428899996, 42.29832221000004], [-93.74754535399995, 42.298412265000024], [-93.74766665999994, 42.298411474000034], [-93.74767092099995, 42.29877169100007], [-93.74754961499997, 42.29877248200006], [-93.74755494099998, 42.29922275300004], [-93.74743363399995, 42.29922354400003], [-93.74743469899994, 42.299313598000026], [-93.74731339199997, 42.299314389000074], [-93.74731552199995, 42.29949449700007], [-93.74695159999999, 42.29949686900005], [-93.74695266399999, 42.29958692300005], [-93.74683135699996, 42.29958771300005], [-93.74683242099997, 42.29967776700005], [-93.74658980499999, 42.29967934700005], [-93.74659086899999, 42.29976940100005], [-93.74646956099997, 42.29977019100005], [-93.74646849699997, 42.29968013700005], [-93.74610457399996, 42.29968250500008], [-93.74610563699997, 42.299772559000075], [-93.74598432899995, 42.29977334900008], [-93.74598539199997, 42.299863403000074], [-93.74586408399995, 42.29986419200003], [-93.74586620999997, 42.30004430100007], [-93.74574490099997, 42.300045090000026], [-93.74574596399998, 42.30013514400008], [-93.74562465499997, 42.300135933000035], [-93.74562890499999, 42.30049615000007], [-93.74538628599998, 42.30049772700005], [-93.74538841099996, 42.300677836000034], [-93.74526710099997, 42.30067862400006], [-93.74527347299994, 42.30121895000008], [-93.74515216199995, 42.30121973900003], [-93.74515322399998, 42.30130979300003], [-93.74503191299999, 42.30131058100005], [-93.74503722199995, 42.301760853000076], [-93.74515853399998, 42.301760064000064], [-93.74515959599995, 42.30185011900005], [-93.74528090799998, 42.30184933000004], [-93.74528303199997, 42.30202943900008], [-93.74540434399995, 42.30202865000007], [-93.74540540699996, 42.302118705000055], [-93.74552671899994, 42.30211791600004], [-93.74553203199997, 42.30256818700008], [-93.74541071799996, 42.30256897600003], [-93.74541177999998, 42.30265903000003], [-93.74529046699996, 42.30265981900004], [-93.74529152899999, 42.30274987300004], [-93.74541284299994, 42.30274908400003], [-93.74541390499996, 42.30283913900007], [-93.74529259099995, 42.302839927000036], [-93.74529790199995, 42.30329019900006], [-93.74517658699995, 42.303290987000025], [-93.74518295899998, 42.303831313000046], [-93.74506164299999, 42.30383210100007], [-93.74506695299999, 42.304282372000046], [-93.74518826999997, 42.30428158400008], [-93.74518933199994, 42.30437163800008], [-93.74506801499996, 42.30437242600004], [-93.74507226199995, 42.30473264300008], [-93.74495094499997, 42.304733432000035], [-93.74495200599995, 42.30482348600003], [-93.74483068899997, 42.304824274000055], [-93.74483174999995, 42.30491432800005], [-93.74471043199998, 42.304915116000075], [-93.74471149399994, 42.30500517000007], [-93.74459017599997, 42.30500595800004], [-93.74459123699995, 42.305096012000035], [-93.74446991899998, 42.30509680000006], [-93.74447522399998, 42.305547071000035], [-93.74435390499997, 42.30554785900006], [-93.74435496599995, 42.305637913000055], [-93.74399100799997, 42.30564027500003], [-93.74399206799995, 42.30573032900003], [-93.74374942899999, 42.30573190300004], [-93.74374730899996, 42.30555179500004], [-93.74362598999994, 42.305552582000075], [-93.74362492999995, 42.30546252700003], [-93.74350361099994, 42.305463314000065], [-93.74350255099995, 42.30537326000007], [-93.74338123199999, 42.305374046000054], [-93.74338017299999, 42.30528399200006], [-93.74325885399998, 42.30528477900003], [-93.74325779499998, 42.305194724000046], [-93.74313647599996, 42.30519551100008], [-93.74313541699996, 42.305105456000035], [-93.74301409899994, 42.30510624200008], [-93.74301303999994, 42.305016188000025], [-93.74289172199997, 42.30501697400007], [-93.74289066299997, 42.30492692000007], [-93.74276934499994, 42.30492770600006], [-93.74276828599994, 42.30483765100007], [-93.74264696899996, 42.30483843700006], [-93.74264590999996, 42.30474838300006], [-93.74252459199994, 42.30474916900005], [-93.74252353399999, 42.30465911400006], [-93.74240221699995, 42.30465990000005], [-93.74240115899994, 42.30456984500006], [-93.74227984099997, 42.30457063100005], [-93.74227878299996, 42.30448057600006], [-93.74215746599998, 42.30448136200005], [-93.74215429299994, 42.304211199000065], [-93.74154770999996, 42.30421512300006], [-93.74154876699998, 42.30430517700006], [-93.74094218199997, 42.30430909800003], [-93.74094323799994, 42.30439915300008], [-93.74057928699995, 42.304401504000055], [-93.74058034299998, 42.30449155800005], [-93.74045902499995, 42.30449234100007], [-93.74046008099998, 42.30458239600006], [-93.74033876299995, 42.304583179000076], [-93.74033981799994, 42.304673233000074], [-93.73961191299998, 42.30467793100007], [-93.73961085899998, 42.30458787600003], [-93.73864031899996, 42.304594132000034], [-93.73863926599995, 42.304504078000036], [-93.73815399699998, 42.304507202000025], [-93.73815504899994, 42.30459725700007], [-93.73791241399994, 42.304598818000045], [-93.73791346599995, 42.30468887300003], [-93.73767083099995, 42.304690434000065], [-93.73767188199997, 42.30478048800006], [-93.73755056399995, 42.304781269000046], [-93.73755161499997, 42.30487132300004], [-93.73730897899998, 42.30487288300003], [-93.73731002999995, 42.304962938000074], [-93.73718871199998, 42.30496371800007], [-93.73718976299995, 42.305053772000065], [-93.73694712599996, 42.30505533200005], [-93.73694922599998, 42.305235441000036], [-93.73682790799995, 42.30523622000004], [-93.73682895799999, 42.30532627500003], [-93.73658631999996, 42.305327833000035]], [[-93.73658631999996, 42.305327833000035], [-93.73659051899995, 42.30568805100006], [-93.73646919999999, 42.305688830000065], [-93.73647444799997, 42.30613910200003], [-93.73635312799996, 42.306139881000036], [-93.73634473199996, 42.30541944600003], [-93.73646605099998, 42.305418667000026], [-93.73646500099994, 42.30532861300003], [-93.73658631999996, 42.305327833000035]]]}, "attributes": {"CCM": None, "SOILDSSURGO": None, "HydroID": 2, "M7D10Y1012": None, "QAH": None, "DRNFREQ": None, "M30D5Y": None, "Edited": 0, "Shape_Area": 8.778447931981523e-05, "RELATEDOIDS": None, "PK5": None, "SOILASSURGO": None, "CSL10_85": None, "SOILBSSURGO": None, "STREAM_VAR": None, "M7D10Y": None, "HYSEP": None, "KSATSSUR": None, "PK2": None, "PK500": None, "DESMOIN": None, "Name": "T2014121131250", "OBJECTID": 1, "FOS": None, "STRMTOT": None, "BFI": None, "Descript": "W07080105", "GlobalWshd": 1, "PK25": None, "DRNAREA": None, "DrainID": 2, "NSSREGNO": None, "M1D10Y": None, "Shape_Length": 0.0629372166137532, "M30D10Y": None, "TAU_ANN": None, "SOILCSSURGO": None, "PK200": None, "I24H10Y": None, "M1D10Y1012": None, "PK100": None, "RSD": None, "ORIG_FID": 1, "WarningMsg": None, "HUCID": "6.29372166137532E-02", "PRECIP": None, "PK10": None, "URBNLCD01": None, "BSHAPE": None, "PK50": None, "IMPNLCD01": None, "BASLEN": None}}], "spatialReference": {"wkid": 4326, "latestWkid": 4326}}, "Workspace": "IA20141201131238376000"} 

        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc()}
                       }

        finally:
            print "Results="+json.dumps(Results) 

if __name__ == '__main__':
    DelineationWrapper()
