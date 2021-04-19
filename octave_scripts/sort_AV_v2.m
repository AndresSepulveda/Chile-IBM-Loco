more off
warning off
close all
clear all
%
%pkg load octcdf
%pkg load statistics
graphics_toolkit gnuplot

disp('Leer AMERS')
amers=load('./release_positions/IFOP_AMERS.txt');

s_a_lat=amers(:,2);
s_a_lon=amers(:,1);

[aux, indx_s_a]=sort(s_a_lat);

a_lat=s_a_lat(indx_s_a);
a_lon=s_a_lon(indx_s_a);

tabla=[];
quienconquien=[];

distas=[]; % Todas las distancias - mejor si se libera desde un solo punto.
norte=0;
nortes=[];
sure=0;
sures=[];
tiempos=[];
tnortes=[];
tsures=[];

disp('Leer Datos')
tic

%%%file_prefix=['20m_E1';'20m_E2';'30m_E1';'30m_E2';'40m_E1';'40m_E2'];
file_prefix=['20m_E1_av'] % ;'20m_E1_di'];  % '30m_E1';'40m_E1'];


for ii=1:size(file_prefix,1)
num_lat_lon=[];

prefix=file_prefix(ii,:);
%nc=netcdf(['/var/www/html/Loco/',prefix,'.nc'],'r');
nc=netcdf(['./',prefix,'.nc'],'r');

% age_seconds              (traj,time)
% land_binary_mask
% lat
% lon
% z
% status
% time(time)

s_lat=nc{'lat'}(:,:);
s_lon=nc{'lon'}(:,:);
s_status=nc{'status'}(:,:);
tiempo=nc{'time'}(:);

toc
disp('Extraer Maximo/Minimo')
tic
 
particulas_od=zeros(size(a_lat,1),size(a_lat,1));
not_stranded =zeros(4,size(a_lat,1));

l0=0; % Active
m0=0;  % Stranded
n0=0; % Missing_data
o0=0; % Retired

ini_lats=[];
ini_lons=[];
end_lats=[];
end_lons=[];

sort_lat=[];
for i=1:size(s_lat,1)  % Ordenando por latitud
   aux_lat=s_lat(i,:);
   aux_lat(aux_lat > 0)=[];
   sort_lat(i)=aux_lat(1);
end

[sorted_lat, indx_sort]=sort(sort_lat);

lat=[];
lon=[];
status=[];
for j=1:size(indx_sort,2)
   lat=[lat;s_lat(indx_sort(j),:)];
   lon=[lon;s_lon(indx_sort(j),:)];
   status=[status;s_status(indx_sort(j),:)];
end


for i=1:size(lat,1)  % Trayectorias
   aux_lat=lat(i,:);
   aux_lat(aux_lat > 0)=[];
   ini_lat=aux_lat(1);
   end_lat=aux_lat(end);


%
%  Longitud
%
   aux_lon=lon(i,:);
   indx_lon=find(aux_lon > 0);
   aux_lon(indx_lon)=[];
   ini_lon=aux_lon(1);
   end_lon=aux_lon(end);
%
%  Status
%
   aux_status=status(i,:);
   aux_status(indx_lon)=[];
   end_status=aux_status(end);
%
%   Tiempo
%
   aux_time=tiempo;
   aux_time(indx_lon)=[];
   ini_tiempo=aux_time(1);
   end_tiempo=aux_time(end);

   aux_amers=zeros(length(a_lat),1);
   aux_ini_lat=aux_amers+ini_lat;
   aux_ini_lon=aux_amers+ini_lon;
   aux_end_lat=aux_amers+end_lat;
   aux_end_lon=aux_amers+end_lon;
   dista_ini=haversine(a_lat,a_lon,aux_ini_lat,aux_ini_lon);
   dista_end=haversine(a_lat,a_lon,aux_end_lat,aux_end_lon);
   coord_ini=find(dista_ini == min(dista_ini));
   coord_end=find(dista_end == min(dista_end));
    
%   whos dista_ini
%    whos coord_ini coord_end
%    keyboard
%    pause
   if (end_status == 0)
      l0 = l0 +1;
      not_stranded(1,coord_ini(1)) = not_stranded(1,coord_ini(1))+1;
   end
   if (end_status == 1)
      aux_nll=[coord_ini(1),a_lat(coord_ini(1)),a_lon(coord_ini(1))];
      num_lat_lon=[num_lat_lon;aux_nll];
%%%      m0, coord_ini(1), coord_end(1) 
      particulas_od(coord_ini(1),coord_end(1))=particulas_od(coord_ini(1),coord_end(1))+1;
      not_stranded(2,coord_ini(1)) = not_stranded(2,coord_ini(1))+1;
      m0=m0+1;
      recorre=haversine(ini_lat,ini_lon,end_lat,end_lon);

      ini_lats=[ini_lats,ini_lat];
      end_lats=[end_lats,end_lat];
      ini_lons=[ini_lons,ini_lon];
      end_lons=[end_lons,end_lon];

      distas=[distas, recorre];
      trecorrido=(end_tiempo-ini_tiempo)/(3600*24);
      tiempos=[tiempos,trecorrido];

      if ini_lat < end_lat
         norte = norte + 1;
         nortes = [ nortes,  recorre ];
         tnortes=[tnortes,trecorrido];
      else
         sure = sure + 1;
         sures = [ sures, recorre ]; 
         tsures=[tsures,trecorrido];
     end
   end
   if (end_status == 2)
      n0 = n0 +1;
      not_stranded(3,coord_ini(1)) = not_stranded(3,coord_ini(1))+1;
   end
   if (end_status == 3)
      o0 = o0 +1;
      not_stranded(4,coord_ini(1)) = not_stranded(4,coord_ini(1))+1;
   end
end

%%pause

disp('Totales')

prefix;

% l0  % Active
% m0  % Stranded
% n0  % Missing
% o0  % Retired

tot=l0+m0+n0+o0;
%sum(sum(particulas_od))

aux_tabla=[ size(lat,1), l0,m0,n0,o0,tot,sum(sum(particulas_od))];

tabla=[tabla; aux_tabla];

normalized_particulas_od=particulas_od;

for j=1:size(a_lat,1)
   total_part=sum(normalized_particulas_od(j,:));
   if total_part==0
      normalized_particulas_od(j,:)= normalized_particulas_od(j,:)*0.0;
   else
      normalized_particulas_od(j,:)= (normalized_particulas_od(j,:)/total_part)*100;
   end
end
%
% Correccion de Daniel Brieva 22/03/2020
%

for jj=1:length(a_lat)
   auxqcq=[];
   aux_norm=normalized_particulas_od(jj,:);
   sort_norm=sort(aux_norm);
   bb=sum(normalized_particulas_od(jj,:));  % Must be 100
   auxqcq=[jj];
   for kk=length(a_lat):-1:length(a_lat)-9  % Connected to 10 
      indx=find(aux_norm == sort_norm(kk));
      auxqcq=[auxqcq, indx(1), sort_norm(kk)];
   end
   quienconquien=[quienconquien; auxqcq];
end


toc
disp('Graficar') 
tic

f = figure('visible','off');
tote=norte+sure;
al_norte=norte*100/tote
al_sure =sure *100/tote

subplot(2,3,1)
hist(distas,50,100)
title([prefix, ' Distancia recorrida '] )
xlabel('km')
ylabel('%')

subplot(2,3,2)
hist(nortes,50,100)
title([prefix, '  al Norte ', num2str(floor(al_norte)), ' %'] )
xlabel('km')
ylabel('%')

if (length(sures) >  0)
 subplot(2,3,3)
 hist(sures,50,100)
 title([prefix, '  al Sur ', num2str(ceil(al_sure)), ' %'] )
 xlabel('km')
 ylabel('%')
end

subplot(2,3,4)
hist(tiempos,50,100)
title([prefix, '  Tiempo de MV '] )
xlabel('dias')
ylabel('%')

subplot(2,3,5)
hist(tnortes,50,100)
title([prefix, '  Tiempo de MV - N'] )
xlabel('dias')
ylabel('%')

if (length(tsures) >  0)
   subplot(2,3,6)
   hist(tsures,50,100)
   title([prefix, '  Tiempo de MV - S'] )
   xlabel('dias')
   ylabel('%')
end

print('-dpng',['sort_',prefix,'_distancias.png'])


f = figure('visible','off');
pcolor(normalized_particulas_od)
title([prefix, ' Conectividad Normalizada'])
xlabel('AMER Destino')
ylabel('AMER Origen')
colorbar
print('-dpng',['sort_',prefix,'_Normalizado_Inicial_Final.png'])

f = figure('visible','off');
pcolor(particulas_od)
title([prefix, ' Conectividad - # Particulas'])
xlabel('AMER Destino')
ylabel('AMER Origen')
colorbar
print('-dpng',['sort_',prefix,'_Inicial_Final.png'])

f = figure('visible','off');
dia=diag(normalized_particulas_od);
hist(dia)
title([prefix,' - Autoreclutamiento'])
xlabel('Porcentaje')
ylabel('Numero de AMERs')
print('-dpng',['sort_',prefix,'_histograma_autoreclutamiento.png'])

f = figure('visible','off');
subplot(2,1,1)
plot(ini_lats,distas,'-x')
title([prefix,' - Distancias'])
xlabel('Latitud')
ylabel('Distancia')

subplot(2,1,2)
indx=find(distas > 6);
plot(ini_lats(indx),distas(indx),'-x')
title([prefix,' - Distancias > 6 km'])
xlabel('Latitud')
ylabel('Distancia')
print('-dpng',['sort_',prefix,'_dependencia_latitudinal.png'])

toc

disp('Guardar Archivo') 
tic

filename=['sort_',prefix,'ini_end_dista.txt'];
fid = fopen(filename,'w+');
for i=1:size(ini_lats,2)
   fprintf(fid,'%.4f %.4f %.4f %.4f %.4f',[ini_lats(i),ini_lons(i),end_lats(i),end_lons(i),distas(i)]);
   fprintf(fid,'\n');
end
fclose(fid);


filename=['sort_',prefix,'_inicial_final.txt'];
save('-ascii',filename,'particulas_od')

toc

end

aux_nll=sortrows(num_lat_lon,1);  %% NOT sort !
[~,indx,~]=unique(aux_nll(:,1),"first");
aux_nll=aux_nll(indx,:);

%%keyboard

filename=['sort_',prefix,'num_lat_lon.txt'];
fid = fopen(filename,'w+');
for i=1:size(aux_nll,1)
   fprintf(fid,'%i %.4f %.4f',aux_nll(i,:));
   fprintf(fid,'\n');
end
fclose(fid);

filename=['sort_',prefix,'estadistica_particulas.txt'];
%save('-ascii',filename,'tabla')
fid = fopen(filename,'w+');
for i=1:size(tabla,1)
   fprintf(fid,'%i %i %i %i %i %i %i',tabla(i,:));
   fprintf(fid,'\n');
end
fclose(fid);

filename=['sort_',prefix,'_conexiones_particulas.txt'];
%save('-ascii',filename,'quienconquien')
%dlmwrite(filename,'quienconquien','precision',4)
fid = fopen(filename,'w+');
for i=1:size(quienconquien,1)
   fprintf(fid,'%i %i %.1f %i %.1f %i %.1f %i %.1f %i %.1f %i %.1f %i %.1f %i %.1f %i %.1f %i %.1f',quienconquien(i,:));
   fprintf(fid,'\n');
end
fclose(fid);

