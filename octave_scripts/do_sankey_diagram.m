function do_sankey_diagram(filename,puntos,prefix)

particulas_od=load(filename);

amers=load(puntos);

a_lat=amers(:,2);
a_lon=amers(:,1);


disp('Start Sankey')
    sankey=[];
    m=1;
    n=1;
    for i=1:size(particulas_od,1)
        for j=1:size(particulas_od,1)
            if particulas_od(i,j) > 0
                for k=1:particulas_od(i,j)
                    sankey(m,1)=i;
                    sankey(m,2)=j;
                    sankey(m,3)=a_lat(i);
                    m=m+1;
                end
            end
        end
    end    
    m
    size(lon_ini)
    
    san_file=[prefix,'_Sankey'];
    fname=[san_file, '.txt'];
    save(fname,'sankey','-ascii')
 %%%   save -ascii sankey.txt sankey
    
%    sankey_noauto=sankey;
    sankey_noauto=sankey;

    indx_s=find(sankey_noauto(:,1) == sankey_noauto(:,2));
    sankey_noauto(indx_s,:)=[];

        f = figure('visible','off');
    try
%        plot_alluvialflow(sankey_noauto);
        plot_alluvialflow(sankey_noauto);
    catch
%        print('-dpng',[san_noa_file,'.png'])
    end    
        print('-dpng',[san_file,'.png'])
