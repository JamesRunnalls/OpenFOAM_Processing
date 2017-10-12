#Export Points to CSV
 
import rhinoscriptsyntax as rs
 
#Select our points
pts = rs.GetObjects("Select Points for CSV Export", 1)
 
#create a filename variable
filename = rs.SaveFileName("Save CSV file","*.csv||", None, "ptExport", "csv")
 
#open the file for writing
file = open(filename, 'w')
 
#create and write a headerline for our CSV
headerline = "x,y,z\n"
file.write(headerline)
 
#print pts
for pt in pts:
    ptCoord = rs.PointCoordinates(pt)
    x = ptCoord[0]
    y = ptCoord[1]
    z = ptCoord[2]
    print "x: %.4f, y: %.4f, z: %.4f" %(x,y,z)
    line = "%.4f,%.4f,%.4f \n" %(x,y,z)
    file.write(line)
 
#Close the file after writing!
file.close()
