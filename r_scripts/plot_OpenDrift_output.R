#
#  Andres Sepulveda (andres.sepulveda@gmail.com) 2020/08/04
# 

rm(list=ls())
library(ncdf4)

setwd("C:/Users/dgeo/IFOP_Catherine")

inp <-nc_open('20m_E1_av.nc')
  lon <- ncvar_get(inp,varid ='lat')
  lat <- ncvar_get(inp,varid ='lon')
  status <- ncvar_get(inp,varid ='status')
  z <- ncvar_get(inp,varid ='z')
  ptime <- ncvar_get(inp,varid ='time')
  trajectory <- ncvar_get(inp,varid ='trajectory')
nc_close(inp)

latini <- c()
latend <- c()
lonini <- c()
lonend <- c()
for (part in 1:length(trajectory)) {
#lat
  auxlat <- lat[,part]
  auxlat2 <-auxlat[auxlat < 1]
  latini[part] <- auxlat2[1]
  latend[part] <- auxlat2[length(auxlat2)]
# lon
  auxlon <- lon[,part]
  auxlon2 <-auxlon[auxlon < 1]
  lonini[part] <- auxlon2[1]
  lonend[part] <- auxlon2[length(auxlon2)]
}

iniend <-cbind(lonini,latini,lonend,latend)

write.csv(iniend,'InicialesFinales.csv')

