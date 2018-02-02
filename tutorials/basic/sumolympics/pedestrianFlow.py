#!/usr/bin/python
# parameters
outfile = "sumolympicWalks.rou.xml"
startEdge = "beg"
endEdge   = "end"
departTime = 0.
departPos = -30.
numberTrips = 200
# generate xml file
with open(outfile, "w") as f:
    f.write("<routes>\n")
    for i in range(numberTrips):
        f.write('    <person depart="%f" id="p%d">\n' % (departTime, i))
        f.write('        <walk arrivalPos="%f" edges="%s %s"/>\n' % (departPos, startEdge, endEdge))
        f.write('    </person>\n')
    f.write("</routes>\n")

