import csv
import simplekml

inputfile = csv.reader(open('erizolatlon.txt'),delimiter=' ')
kml=simplekml.Kml()

for row in inputfile:
  kml.newpoint(name=row[0], coords=[(row[2],row[1])])

kml.save('erizolatlon.kml')
