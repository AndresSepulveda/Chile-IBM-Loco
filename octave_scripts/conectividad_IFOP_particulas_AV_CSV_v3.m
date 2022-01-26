more off
warning off
close all
clear all
%win_start
tic
disp('Leer AMERB')
%amers=load('PuntosJaivaAncud.txt');
%amers=load('Hab_Rocoso_Coquimbo.txt');
amers=load('PuntosCosta_AV.txt');

a_lat=amers(:,2);
a_lon=amers(:,1);

skip = 10;                     %%   Samping here

a_lon=a_lon(1:skip:end);         
a_lat=a_lat(1:skip:end);         %%

min_dista=5000;  % Has to be close to a point, in m

tabla=[];


disp('Leer Datos')

%%%file_prefix=['20m_E1';'20m_E2';'30m_E1';'30m_E2';'40m_E1';'40m_E2'];
%file_prefix=['Uniforme_IF_Obyo_10000_M0'; 'Uniforme_IF_Obyo_10000_M1'; 'Uniforme_IF_Obyo_10000_M2'; 'Uniforme_IF_Obyo_10000_M3'; ...
%             'Uniforme_IF_Obyo_10000_M4'; 'Uniforme_IF_Obyo_10000_M5'; 'Uniforme_IF_Obyo_10000_M6'; 'Uniforme_IF_Obyo_10000_M7'; ...
%             'Uniforme_IF_Obyo_10000_M8'; 'Uniforme_IF_Obyo_10000_M9'; 'Uniforme_IF_Obyo_10000_M10'; 'Uniforme_IF_Obyo_10000_M11'];
file_prefix=['Uniforme_IF_Obyo_10000_M00'; 'Uniforme_IF_Obyo_10000_M01'; 'Uniforme_IF_Obyo_10000_M02'; 'Uniforme_IF_Obyo_10000_M03'; ...
             'Uniforme_IF_Obyo_10000_M04'; 'Uniforme_IF_Obyo_10000_M05'; 'Uniforme_IF_Obyo_10000_M06'; 'Uniforme_IF_Obyo_10000_M07'; ...
             'Uniforme_IF_Obyo_10000_M08'; 'Uniforme_IF_Obyo_10000_M09'; 'Uniforme_IF_Obyo_10000_M10'; 'Uniforme_IF_Obyo_10000_M11'];

for ii=1:size(file_prefix,1)
tic
    tic
    num_lat_lon=[];
    quienconquien=[];
    prefix=file_prefix(ii,:)
    nc=load([prefix,'.txt']);

    lon_ini=nc(:,3);
    lat_ini=nc(:,4);
    lon_end=nc(:,7);
    lat_end=nc(:,8);
    status=nc(:,9);

    toc
    disp('Extraer Maximo/Minimo')
    tic
    
    particulas_od=zeros(size(a_lat,1),size(a_lat,1));
    not_stranded =zeros(4,size(a_lat,1));

    l0=0; % Active
    m0=0; % Missing_data
    n0=0; % Retired
    o0=0; % None

%     sankey_v2=[];
%     
    for i=1:size(lat_ini,1)  % Trayectorias
        ini_lat=lat_ini(i);
        end_lat=lat_end(i);
        ini_lon=lon_ini(i);
        end_lon=lon_end(i);
        end_status=status(i);

        aux_amers=zeros(length(a_lat),1);
        aux_ini_lat=aux_amers+ini_lat;
        aux_ini_lon=aux_amers+ini_lon;
        aux_end_lat=aux_amers+end_lat;
        aux_end_lon=aux_amers+end_lon;
        dista_ini=haversine(a_lat,a_lon,aux_ini_lat,aux_ini_lon);
        dista_end=haversine(a_lat,a_lon,aux_end_lat,aux_end_lon);
        if (min(dista_ini) < min_dista) && (min(dista_end) < min_dista)
            coord_ini=find(dista_ini == min(dista_ini));
            coord_end=find(dista_end == min(dista_end));
            if (end_status == 0)
                l0 = l0 +1;
                try
                    particulas_od(coord_ini(1),coord_end(1))=particulas_od(coord_ini(1),coord_end(1))+1;
%                     sankey_v2=[sankey_v2; coord_ini(1) coord_end(1) ini_lat];
                catch
                end %_try_catch
                not_stranded(1,coord_ini(1)) = not_stranded(1,coord_ini(1))+1;
            end
            if (end_status == 1)
                aux_nll=[coord_ini(1),a_lat(coord_ini(1)),a_lon(coord_ini(1))];
                num_lat_lon=[num_lat_lon;aux_nll];
                try
                    particulas_od(coord_ini(1),coord_end(1))=particulas_od(coord_ini(1),coord_end(1))+1;
%                     sankey_v2=[sankey_v2; coord_ini(1) coord_end(1) ini_lat];
                catch
                end %_try_catch
                not_stranded(2,coord_ini(1)) = not_stranded(2,coord_ini(1))+1;
                m0=m0+1;
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
    end
    toc
    disp('Totales')
    tic
    prefix;

% l0  % Active
% m0  % Missing
% n0  % Retired
% o0  % none

    tot=l0+m0+n0+o0;
%sum(sum(particulas_od))

    aux_tabla=[size(lat_ini,1), l0,m0,n0,o0,tot,sum(sum(particulas_od))];
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

%     san_file=[prefix,'_Sankey_v2'];
%     fname=[san_file, '.txt'];
%     save(fname,'sankey_v2','-ascii')

    toc
    
%     tic
% %     disp('Start Sankey')
%     sankey=[];
%     m=1;
%     n=1;
%     for i=1:size(particulas_od,1)
%         for j=1:size(particulas_od,1)
%             if particulas_od(i,j) > 0
%                 for k=1:particulas_od(i,j)
%                     sankey(m,1)=i;
%                     sankey(m,2)=j;
%                     sankey(m,3)=a_lat(i);
%                     m=m+1;
%                 end
%             end
%         end
%     end    
%     m
%     size(lon_ini)
%     
%     san_file=[prefix,'_Sankey'];
%     fname=[san_file, '.txt'];
%     save(fname,'sankey','-ascii')
 %%%   save -ascii sankey.txt sankey
    
%    sankey_noauto=sankey;
%     sankey_noauto_v2=sankey_v2;
% 
%     indx_s=find(sankey_noauto_v2(:,1) == sankey_noauto_v2(:,2));
%     sankey_noauto_v2(indx_s,:)=[];
%     %
%     %  Add latitude
    %
     
%     san_noa_file=[prefix,'_Sankey_NoAuto'];
%     fname=[san_noa_file, '.txt'];
%     save(fname,'sankey_noauto','-ascii')
    
%      san_noa_file_v2=[prefix,'_Sankey_NoAuto_v2'];
%      fname=[san_noa_file_v2, '.txt'];
%      save(fname,'sankey_noauto_v2','-ascii')
%     %%%save -ascii sankey_noauto.txt sankey_noauto
%     
%     disp('Sankey ready')
%     % m must be less or equal
%     toc
%     
%
% Correccion de Daniel Brieva 22/03/2020
%
    tic
    for jj=1:length(a_lat)
            auxqcq=[];
            aux_norm=normalized_particulas_od(jj,:);
            sort_norm=sort(aux_norm);
            bb=sum(normalized_particulas_od(jj,:));  % Must be 100
            auxqcq=[jj];
            for kk=length(a_lat):-1:length(a_lat)-2
                indx=find(aux_norm == sort_norm(kk));
                auxqcq=[auxqcq, indx(1), sort_norm(kk)];
            end
            quienconquien=[quienconquien; auxqcq];
    end

    toc
    disp('Graficar') 
    tic
    f = figure('visible','off');
    pcolor(normalized_particulas_od')
    title([prefix, ' Conectividad Normalizada'])
    ylabel('AMERB Destino')
    xlabel('AMERB Origen')
    colormap(flipud(hot));
    colorbar
    print('-dpng',[prefix,'_Normalizado_Inicial_Final.png'])

    f = figure('visible','off');
    pcolor(particulas_od')
    title([prefix, ' Conectividad - # Particulas'])
    ylabel('AMERB Destino')
    xlabel('AMERB Origen')
    colormap(flipud(hot));
    colorbar
    print('-dpng',[prefix,'_Inicial_Final.png'])

    f = figure('visible','off');
        aux_v=particulas_od;
        plotConfMat_as(fliplr(aux_v)');
    print('-dpdf',[prefix,'_Valores_Inicial_Final.pdf'])  % Not useful for big numbers
    
%     f = figure('visible','off');
%     try
% %        plot_alluvialflow(sankey_noauto);
%         plot_alluvialflow(sankey_noauto_v2);
%     catch
% %        print('-dpng',[san_noa_file,'.png'])
%     end    
%         print('-dpng',[san_noa_file_v2,'.png'])
        
    f = figure('visible','off');
    dia=diag(normalized_particulas_od);
    hist(dia)
    title([prefix,' - Autoreclutamiento'])
    xlabel('Porcentaje')
    ylabel('Numero de AMERBs')
    print('-dpng',[prefix,'_histograma_autoreclutamiento.png'])
    
    toc

    disp('Guardar Archivo') 
    tic

    filename=[prefix,'_inicial_final.txt'];
    %save('-ascii',filename,'particulas_od')
%     fid = fopen(filename,'w+'); 
%     for i=1:size(particulas_od,1)
%        fprintf(fid,'%i',particulas_od(i,:));
%        fprintf(fid,'\n');
%     end
%     fclose(fid)
    save(filename,'particulas_od','-ascii')
    
    toc

    aux_nll=sortrows(num_lat_lon,1);  %% NOT sort !
    [~,indx,~]=unique(aux_nll(:,1),"first");
    aux_nll=aux_nll(indx,:);

%%keyboard

    filename=[prefix,'_num_lat_lon.txt'];
    fid = fopen(filename,'w+');
    for i=1:size(aux_nll,1)
        fprintf(fid,'%i %.4f %.4f',aux_nll(i,:));
        fprintf(fid,'\n');
    end
    fclose(fid);


    filename=[prefix,'_tres_conexiones_particulas.txt'];
%save('-ascii',filename,'quienconquien')
%dlmwrite(filename,'quienconquien','precision',4)
    fid = fopen(filename,'w+');
    for i=1:size(quienconquien,1)
        fprintf(fid,'%i %i %.1f %i %.1f %i %.1f',quienconquien(i,:));
        fprintf(fid,'\n');
    end
    fclose(fid);
toc
end

filename=['Estadistica_particulas.txt'];
%save('-ascii',filename,'tabla')
fid = fopen(filename,'w+');
for i=1:size(tabla,1)
   fprintf(fid,'%i %i %i %i %i %i %i',tabla(i,:));
   fprintf(fid,'\n');
end
fclose(fid);

toc
